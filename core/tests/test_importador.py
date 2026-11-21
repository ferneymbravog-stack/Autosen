from datetime import datetime
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase

from core.importador import extraer_inserts, parsear_valores
from core.models import Alerta, Cliente, Lectura, Sensor, Usuario, Vehiculo
from core.tests.fabricas import crear_cliente

DUMP = Path(__file__).parent / "datos" / "dump_prueba.sql"
if not DUMP.is_file():
    DUMP.parent.mkdir(parents=True, exist_ok=True)
    DUMP.write_text(
        "INSERT INTO `usuario` (`Id_usuario`, `Nombre`, `Correo`, `Contrasena`, `Rol`) VALUES\n"
        "(1, 'Admin', 'admin@autosen.com', '$2y$12$hashDePruebaNoReal', 'ADMIN');\n\n"
        "INSERT INTO `cliente` (`Id_cliente`, `Nombre_cliente`, `Apellido_cliente`, `Contrasena`, `Correo`, `Id_usuario`, `Estado`, `Telefono`) VALUES\n"
        "(1, 'John', 'O\\'Neil', '$2y$12$hash1', 'john@test.com', 1, 'activo', '3001234567'),\n"
        "(2, 'Juan', 'Ro\\'cio', '$2y$12$hash2', 'juan@test.com', NULL, 'bloqueado', '3007654321');\n\n"
        "INSERT INTO `vehiculo` (`Id_vehiculo`, `Id_cliente`, `Nombre_vehiculo`, `Color`, `Marca`, `Modelo`, `Placa`, `Tipo_placa`, `elm_mac`) VALUES\n"
        "(4, 1, 'Onix, el rojo', 'Rojo', 'Chevrolet', '2020-01-01', 'EMT262', 'publico', NULL);\n\n"
        "INSERT INTO `sensores` (`Id_sensor`, `Nombre_sensor`, `Tipo_sensor`, `Tipo_daño`, `Nivel`, `Estado`, `Id_vehiculo`) VALUES\n"
        "(21, 'Sensor Oxigeno', 'Oxigeno', 'Falla en mezcla\\ncombustible', 50, NULL, 4),\n"
        "(22, 'Sensor Temperatura', 'Temperatura', NULL, NULL, 'OK', 4);\n\n"
        "INSERT INTO `lecturas` (`Id_lectura`, `Id_vehiculo`, `Nombre_sensor`, `Tipo_sensor`, `Valor`, `Unidad`, `Nivel`, `Estado`, `Fecha_lectura`) VALUES\n"
        "(7, 4, 'Sensor Temperatura', 'Temperatura', 2345.5, 'C', 30, 'OK', '2026-09-14 20:04:25');\n\n"
        "INSERT INTO `alertas` (`Id_alerta`, `Id_vehiculo`, `Nombre_sensor`, `Tipo_sensor`, `Valor`, `Nivel`, `Tipo`, `Mensaje`, `Leida`, `Fecha_alerta`) VALUES\n"
        "(3, 4, 'Sensor Oxigeno', 'Oxigeno', 100.0, 80, 'falla', 'Falla crítica; revisar (motor)', 0, '2026-09-14 20:05:00');\n",
        encoding="utf-8"
    )


class ParserTests(SimpleTestCase):
    def test_tipos_y_escapes(self):
        texto = r"""(1, 'O\'Neil', NULL, 2.5, 'a''b', 'x\ny'),
(2, 'c,d;(e)', -3, '', 'z\\', 't\tu')"""
        self.assertEqual(parsear_valores(texto),
                         [[1, "O'Neil", None, 2.5, "a'b", "x\ny"], [2, "c,d;(e)", -3, "", "z\\", "t\tu"]])

    def test_extraer_inserts_en_orden(self):
        inserts = extraer_inserts(DUMP.read_text(encoding="utf-8"))
        self.assertEqual([t for t, _, _ in inserts],
                         ["usuario", "cliente", "vehiculo", "sensores", "lecturas", "alertas"])
        self.assertEqual(inserts[3][1][3], "Tipo_daño")


class ImportarMysqlTests(TestCase):
    def importar(self, **opciones):
        salida = StringIO()
        call_command("importar_mysql", str(DUMP), stdout=salida, **opciones)
        return salida.getvalue()

    def test_importa_conservando_ids_y_valores(self):
        salida = self.importar()
        for linea in ("usuario: 1", "cliente: 2", "vehiculo: 1", "sensores: 2", "lecturas: 1", "alertas: 1"):
            self.assertIn(linea, salida)
        self.assertEqual(Usuario.objects.get(pk=1).contrasena, "$2y$12$hashDePruebaNoReal")
        self.assertEqual(Cliente.objects.get(pk=1).apellido_cliente, "O'Neil")
        juan = Cliente.objects.get(pk=2)
        self.assertEqual((juan.apellido_cliente, juan.usuario, juan.estado), ("Ro'cio", None, "bloqueado"))
        v = Vehiculo.objects.get(pk=4)
        self.assertEqual((v.nombre_vehiculo, v.placa, v.tipo_placa, v.elm_mac),
                         ("Onix, el rojo", "EMT262", "publico", None))
        s = Sensor.objects.get(pk=21)
        self.assertEqual((s.tipo_dano, s.estado), ("Falla en mezcla\ncombustible", None))
        self.assertEqual(Sensor.objects.get(pk=22).nivel, 0)
        lectura = Lectura.objects.get(pk=7)
        self.assertEqual((lectura.valor, lectura.fecha_lectura), (2345.5, datetime(2026, 9, 14, 20, 4, 25)))
        self.assertEqual(Alerta.objects.get(pk=3).mensaje, "Falla crítica; revisar (motor)")

    def test_secuencias_continuan_despues_de_los_ids_importados(self):
        self.importar()
        self.assertEqual(crear_cliente(correo="nuevo@test.com").pk, 3)

    def test_aborta_si_hay_datos_y_no_se_pide_limpiar(self):
        crear_cliente(correo="otro@test.com")
        with self.assertRaisesMessage(CommandError, "La tabla cliente ya tiene datos; usa --limpiar para reemplazarlos."):
            self.importar()

    def test_limpiar_reemplaza_los_datos(self):
        crear_cliente(correo="otro@test.com")
        self.importar(limpiar=True)
        self.assertEqual(Cliente.objects.count(), 2)
        self.assertFalse(Cliente.objects.filter(correo="otro@test.com").exists())
