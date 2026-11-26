from datetime import datetime
from unittest import mock

from django.test import Client, TestCase

from core.models import Alerta, Lectura, Vehiculo
from core.tests.fabricas import (crear_alerta, crear_cliente, crear_lectura, crear_sensor, crear_usuario,
                                 crear_vehiculo, login_admin, login_cliente)


class LecturasTests(TestCase):
    def setUp(self):
        self.v = crear_vehiculo(crear_cliente())

    def enviar(self, **datos):
        base = {"idVehiculo": self.v.pk, "nombreSensor": "Temperatura refrigerante", "tipoSensor": "TEMP", "valor": "95"}
        return self.client.post("/api/obd2/lecturas", {**base, **datos})

    def test_guardar_lectura_con_falla(self):
        r = self.enviar(unidad="°C")
        lectura = Lectura.objects.get()
        self.assertEqual(r.json(), {"ok": True, "mensaje": "Lectura registrada.", "idLectura": lectura.pk, "nivel": 75,
                                    "estado": "FALLA"})
        self.assertEqual((lectura.valor, lectura.unidad, lectura.fecha_lectura.microsecond), (95.0, "°C", 0))
        self.assertEqual(Alerta.objects.get().mensaje, "Falla crítica en Temperatura refrigerante: nivel 75% (95.0 °C).")

    def test_sin_unidad(self):  # Review Focus 5
        self.enviar()
        self.assertEqual(Lectura.objects.get().unidad, "")
        self.assertEqual(Alerta.objects.get().mensaje, "Falla crítica en Temperatura refrigerante: nivel 75% (95.0).")

    def test_unidad_vacia(self):  # Review Focus 5
        self.enviar(unidad="")
        self.assertEqual(Alerta.objects.get().mensaje, "Falla crítica en Temperatura refrigerante: nivel 75% (95.0 ).")

    def test_advertencia_y_sin_alerta(self):
        self.assertEqual(self.enviar(tipoSensor="RPM", valor="1800").json()["estado"], "ADVERTENCIA")
        self.assertEqual(Alerta.objects.get().tipo, "advertencia")
        self.assertEqual(self.enviar(valor="80").json()["estado"], "OK")
        self.assertEqual(Alerta.objects.count(), 1)

    def test_valor_infinito_no_se_guarda(self):  # revisión final #5
        r = Client(raise_request_exception=False).post("/api/obd2/lecturas", {
            "idVehiculo": self.v.pk, "nombreSensor": "x", "tipoSensor": "TEMP", "valor": "Infinity"})
        self.assertEqual((r.status_code, Lectura.objects.count()), (400, 0))

    def test_errores(self):
        self.assertEqual(self.enviar(idVehiculo=9999).json(), {"ok": False, "mensaje": "Vehículo no encontrado."})
        r = Client(raise_request_exception=False).post("/api/obd2/lecturas", {
            "idVehiculo": self.v.pk, "nombreSensor": "x", "tipoSensor": "TEMP", "valor": "abc"})
        self.assertEqual(r.status_code, 400)


class ElmTests(TestCase):
    def test_guardar_y_consultar_elm(self):
        v = crear_vehiculo(crear_cliente())
        url = f"/api/obd2/vehiculo/{v.pk}/elm"
        self.assertEqual(self.client.get(url).json(), {"ok": True, "idVehiculo": v.pk, "elmMac": None, "conectado": False,
                                                       "mensaje": "No hay un ELM327 asociado a este vehículo."})
        r = self.client.post(url, {"elmMac": "00:1D:A5:68:98:8B"})
        self.assertEqual(r.json(), {"ok": True, "mensaje": "ELM327 guardado para reconexión futura.",
                                    "elmMac": "00:1D:A5:68:98:8B"})
        self.assertEqual(self.client.get(url).json()["mensaje"],
                         "ELM327 registrado. La conexión Bluetooth debe realizarse desde Android.")
        for metodo in ("get", "post"):
            r = getattr(self.client, metodo)("/api/obd2/vehiculo/9999/elm", {"elmMac": "x"})
            self.assertEqual(r.json(), {"ok": False, "mensaje": "Vehículo no encontrado."})


class ConsultasTests(TestCase):
    def setUp(self):
        self.v = crear_vehiculo(crear_cliente())

    def test_historial_y_ultima(self):
        primera = crear_lectura(self.v.pk, fecha=datetime(2026, 10, 21, 19, 45, 0), nombre_sensor="A", tipo_sensor="RPM",
                                valor=900.0, unidad="rpm", nivel=13)
        for i in range(30):
            crear_lectura(self.v.pk, nombre_sensor=f"S{i}")
        historial = self.client.get(f"/api/obd2/historial/{self.v.pk}").json()["lecturas"]
        self.assertEqual(len(historial), 31)
        self.assertEqual(historial[-1], {"idLectura": primera.pk, "nombreSensor": "A", "tipoSensor": "RPM", "valor": 900.0,
                                         "unidad": "rpm", "nivel": 13, "estado": "OK", "fechaLectura": "2026-10-21T19:45"})
        ultima = self.client.get(f"/api/obd2/ultima/{self.v.pk}").json()
        self.assertEqual((ultima["ok"], len(ultima["lecturas"]), ultima["lecturas"][0]["nombreSensor"]), (True, 30, "S29"))
        self.assertEqual(list(ultima["lecturas"][0]),
                         ["nombreSensor", "tipoSensor", "valor", "unidad", "nivel", "estado", "fechaLectura"])

    def test_alertas_solo_miran_las_ultimas_50_globales(self):
        propia = crear_alerta(self.v.pk, leida=1)
        r = self.client.get(f"/api/obd2/alertas/{self.v.pk}").json()
        self.assertEqual(list(r["alertas"][0]), ["idAlerta", "nombreSensor", "tipoSensor", "valor", "nivel", "tipo",
                                                 "mensaje", "leida", "fechaAlerta"])
        self.assertEqual((r["alertas"][0]["idAlerta"], r["alertas"][0]["leida"]), (propia.pk, True))
        otro = crear_vehiculo(crear_cliente(correo="otro@test.com"), placa="OTR999")
        for _ in range(50):
            crear_alerta(otro)
        self.assertEqual(self.client.get(f"/api/obd2/alertas/{self.v.pk}").json(), {"ok": True, "alertas": []})

    def test_contrato_claves_json_api_intacto_y_borrado_conserva_historial(self):
        c = crear_cliente(correo="contrato@test.com")
        v = crear_vehiculo(c, placa="API777", nombre="Spark")
        lec = crear_lectura(v, nombre_sensor="Sensor O2", tipo_sensor="O2", valor=0.85, unidad="V", nivel=80)
        ale = crear_alerta(v, nombre_sensor="Sensor O2", tipo_sensor="O2", valor=0.85, nivel=80, tipo="falla")

        # 1. Claves exactas de historial
        r_hist = self.client.get(f"/api/obd2/historial/{v.pk}").json()
        self.assertEqual(list(r_hist.keys()), ["ok", "lecturas"])
        self.assertEqual(
            list(r_hist["lecturas"][0].keys()),
            ["idLectura", "nombreSensor", "tipoSensor", "valor", "unidad", "nivel", "estado", "fechaLectura"],
        )

        # 2. Claves exactas de alertas
        r_ale = self.client.get(f"/api/obd2/alertas/{v.pk}").json()
        self.assertEqual(list(r_ale.keys()), ["ok", "alertas"])
        self.assertEqual(
            list(r_ale["alertas"][0].keys()),
            ["idAlerta", "nombreSensor", "tipoSensor", "valor", "nivel", "tipo", "mensaje", "leida", "fechaAlerta"],
        )

        # 3. Claves exactas de última lectura
        r_ult = self.client.get(f"/api/obd2/ultima/{v.pk}").json()
        self.assertEqual(list(r_ult.keys()), ["ok", "lecturas"])
        self.assertEqual(
            list(r_ult["lecturas"][0].keys()),
            ["nombreSensor", "tipoSensor", "valor", "unidad", "nivel", "estado", "fechaLectura"],
        )

        # 4. Claves exactas de alertas en vivo (cliente y admin)
        cli_c = Client()
        login_cliente(cli_c, c)
        r_vivo = cli_c.get("/api/alertas/en-vivo").json()
        self.assertEqual(list(r_vivo.keys()), ["ok", "alertas", "total"])
        self.assertEqual(
            list(r_vivo["alertas"][0].keys()),
            ["id", "sensor", "tipo_sensor", "nivel", "tipo", "mensaje", "vehiculo", "placa", "fecha"],
        )

        # 5. Al eliminar el vehículo desde el panel, lecturas y alertas quedan con vehiculo=None y placa_historica intacta
        cli_admin = Client()
        login_admin(cli_admin, crear_usuario(correo="adm@autosen.com", rol="SUPERADMIN"))
        cli_admin.post(f"/admin/vehiculo/{v.pk}/eliminar")
        self.assertFalse(Vehiculo.objects.filter(pk=v.pk).exists())
        lec.refresh_from_db()
        ale.refresh_from_db()
        self.assertIsNone(lec.vehiculo)
        self.assertIsNone(ale.vehiculo)
        self.assertEqual((lec.placa_historica, ale.placa_historica), ("API777", "API777"))

        # En alertas en vivo del admin, sigue mostrando la placa histórica y las mismas claves JSON
        r_vivo_post = cli_admin.get("/api/alertas/en-vivo?modo=admin").json()
        item_borrado = next(x for x in r_vivo_post["alertas"] if x["id"] == ale.pk)
        self.assertEqual(item_borrado["placa"], "API777")
        self.assertEqual(
            list(item_borrado.keys()),
            ["id", "sensor", "tipo_sensor", "nivel", "tipo", "mensaje", "vehiculo", "placa", "fecha"],
        )


class ConectarTests(TestCase):
    def test_requiere_sesion_de_cliente(self):
        self.assertRedirects(self.client.post("/api/obd2/conectar"), "/login", fetch_redirect_response=False)

    def test_sin_vehiculos(self):
        login_cliente(self.client, crear_cliente())
        self.assertEqual(self.client.post("/api/obd2/conectar").json(), {
            "ok": False, "conectado": False,
            "mensaje": "Primero registra un vehículo para poder conectar el escáner ELM327."})

    def test_conecta_el_primer_vehiculo(self):
        c = crear_cliente()
        v1, v2 = crear_vehiculo(c, placa="ABC123"), crear_vehiculo(c, placa="DEF456")
        crear_sensor(v1, tipo="MAF", nombre="MAF")
        crear_sensor(v1, tipo="ECT", nombre="ECT")
        crear_sensor(v2, tipo="O2")
        cliente_http = Client(enforce_csrf_checks=True)
        login_cliente(cliente_http, c)
        with mock.patch("api.obd2.random.random", return_value=0.0):
            r = cliente_http.post("/api/obd2/conectar")
        self.assertEqual(r.json(), {
            "ok": True, "conectado": True, "idVehiculo": v1.pk, "vehiculo": "Onix ABC123", "elmMac": "ELM327-SIM-ABC123",
            "mensaje": "Escáner ELM327 conectado por Bluetooth. Recibiendo datos del vehículo en tiempo real.",
            "lecturas": [
                {"nombreSensor": "MAF", "tipoSensor": "MAF", "valor": 2.0, "unidad": "g/s", "nivel": 0, "estado": "OK"},
                {"nombreSensor": "ECT", "tipoSensor": "ECT", "valor": 75.0, "unidad": "°C", "nivel": 75,
                 "estado": "FALLA"}]})
        self.assertEqual(Lectura.objects.count(), 2)
        self.assertEqual(Alerta.objects.get().mensaje, "Falla crítica en ECT: nivel 75% (75.0 °C).")
