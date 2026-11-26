import io
from contextlib import redirect_stdout
from importlib import import_module

from django.apps import apps as django_apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

from core.models import Sensor, Vehiculo
from core.tests.fabricas import crear_cliente, crear_usuario, crear_vehiculo

normalizar_datos = import_module("core.migrations.0002_normalizar_datos").normalizar_datos


class NormalizarDatosTests(TestCase):
    def test_normaliza_vehiculos_existentes(self):
        v = crear_vehiculo(crear_cliente(), placa=" emt262 ", tipo_placa="Público", modelo="2020")
        normalizar_datos(django_apps, None)
        v.refresh_from_db()
        self.assertEqual((v.placa, v.tipo_placa, v.modelo), ("EMT262", "publico", "2020-01-01"))

    def test_quita_el_guion_y_avisa_las_placas_que_chocan(self):  # revisión final
        c = crear_cliente()
        con_guion = crear_vehiculo(c, placa="XYZ-999")
        choque = [crear_vehiculo(c, placa=p) for p in ("ABC-123", "abc123")]
        salida = io.StringIO()
        with redirect_stdout(salida):
            normalizar_datos(django_apps, None)
        self.assertEqual(Vehiculo.objects.get(pk=con_guion.pk).placa, "XYZ999")
        self.assertEqual([Vehiculo.objects.get(pk=v.pk).placa for v in choque], ["ABC-123", "abc123"])
        self.assertIn("ABC123", salida.getvalue())

    def test_la_0004_vuelve_a_normalizar(self):  # bases que ya aplicaron la 0002
        operacion = import_module("core.migrations.0004_placas_sin_guion").Migration.operations[0]
        self.assertIs(operacion.code, normalizar_datos)

    def test_tipo_desconocido_se_conserva(self):  # no inventa datos
        v = crear_vehiculo(crear_cliente(), tipo_placa="Taxi")
        normalizar_datos(django_apps, None)
        v.refresh_from_db()
        self.assertEqual(v.tipo_placa, "Taxi")

    def test_normalizar_datos_es_idempotente(self):  # Review Focus 3
        v = crear_vehiculo(crear_cliente(), placa="ABC123", tipo_placa="particular", modelo="2020-01-01")
        normalizar_datos(django_apps, None)
        normalizar_datos(django_apps, None)
        v.refresh_from_db()
        self.assertEqual((v.placa, v.tipo_placa, v.modelo), ("ABC123", "particular", "2020-01-01"))

    def test_nivel_obligatorio_con_cero_por_defecto(self):
        self.assertFalse(Sensor._meta.get_field("nivel").null)
        sensor = Sensor.objects.create(vehiculo=crear_vehiculo(crear_cliente()), nombre_sensor="S", tipo_sensor="T")
        self.assertEqual(sensor.nivel, 0)

    def test_borrar_admin_desvincula_clientes(self):  # Review Focus 5
        admin = crear_usuario()
        c = crear_cliente()
        c.usuario = admin
        c.save()
        admin.delete()
        c.refresh_from_db()
        self.assertIsNone(c.usuario)


class MigracionHuerfanosVehiculoTests(TransactionTestCase):
    """Verifica que las migraciones 0009 y 0010 limpien huérfanos, llenen placa_historica y sean reversibles."""

    def test_migracion_0009_y_0010_limpia_huerfanos_llena_placas_y_es_reversible(self):
        executor = MigrationExecutor(connection)
        executor.migrate([("core", "0008_renombrar_web_push_a_navegador")])
        apps_0008 = executor.loader.project_state([("core", "0008_renombrar_web_push_a_navegador")]).apps

        Cliente08 = apps_0008.get_model("core", "Cliente")
        Vehiculo08 = apps_0008.get_model("core", "Vehiculo")
        Lectura08 = apps_0008.get_model("core", "Lectura")
        Alerta08 = apps_0008.get_model("core", "Alerta")

        from core.utilidades import ahora

        c = Cliente08.objects.create(
            nombre_cliente="Test", apellido_cliente="Mig", contrasena="h", correo="mig@test.com", estado="activo"
        )
        v = Vehiculo08.objects.create(
            cliente=c, nombre_vehiculo="Onix", color="Rojo", marca="Chevrolet", placa="MIG123", tipo_placa="particular"
        )
        lec_valida = Lectura08.objects.create(
            id_vehiculo=v.pk, nombre_sensor="O2", tipo_sensor="O2", valor=0.5, unidad="V", nivel=40,
            estado="ADVERTENCIA", fecha_lectura=ahora(),
        )
        lec_huerfana = Lectura08.objects.create(
            id_vehiculo=99999, nombre_sensor="ECT", tipo_sensor="ECT", valor=95.0, unidad="C", nivel=80,
            estado="FALLA", fecha_lectura=ahora(),
        )
        ale_huerfana = Alerta08.objects.create(
            id_vehiculo=88888, nombre_sensor="ECT", tipo_sensor="ECT", valor=95.0, nivel=80, tipo="falla",
            mensaje="Falla", leida=0, fecha_alerta=ahora(),
        )

        # Avanzar a la última migración aplicando 0009 y 0010
        executor = MigrationExecutor(connection)
        salida = io.StringIO()
        with redirect_stdout(salida):
            executor.migrate(executor.loader.graph.leaf_nodes("core"))

        self.assertIn("lecturas: 1, alertas: 1", salida.getvalue())

        apps_actual = executor.loader.project_state(executor.loader.graph.leaf_nodes("core")).apps
        LecturaActual = apps_actual.get_model("core", "Lectura")
        AlertaActual = apps_actual.get_model("core", "Alerta")

        lv = LecturaActual.objects.get(pk=lec_valida.pk)
        lh = LecturaActual.objects.get(pk=lec_huerfana.pk)
        ah = AlertaActual.objects.get(pk=ale_huerfana.pk)
        self.assertEqual((lv.vehiculo_id, lv.placa_historica), (v.pk, "MIG123"))
        self.assertIsNone(lh.vehiculo_id)
        self.assertIsNone(ah.vehiculo_id)

        # Verificar reversibilidad a 0008 y volver al estado final
        executor = MigrationExecutor(connection)
        executor.migrate([("core", "0008_renombrar_web_push_a_navegador")])
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes("core"))
