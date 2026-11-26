"""Pruebas automatizadas de servicios externos (sin llamadas de red reales)."""
import io
import json
import smtplib
import urllib.error
from datetime import datetime
from unittest import mock

from django.core import mail
from django.core.management import call_command
from django.test import Client, SimpleTestCase, TestCase, TransactionTestCase, override_settings

from core.models import NotificacionEnviada, RegistroAuditoria
from core.normalizacion import normalizar_telefono_whatsapp
from core.notificaciones import despachar_notificacion_multicanal
from core.servicios_externos import enviar_email, enviar_telegram, enviar_whatsapp
from core.tests.fabricas import (
    _post_con_csrf,
    crear_alerta,
    crear_cliente,
    crear_usuario,
    crear_vehiculo,
    login_admin,
    login_cliente,
)


def _respuesta_http(cuerpo: dict | str, status: int = 200):
    """Construye un objeto de respuesta simulado compatible con context manager de urlopen."""
    texto = json.dumps(cuerpo) if isinstance(cuerpo, dict) else cuerpo
    resp = mock.MagicMock()
    resp.status = status
    resp.read.return_value = texto.encode("utf-8")
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    return resp


class TelegramServicioTests(SimpleTestCase):
    """Pruebas unitarias del cliente Telegram Bot API."""

    @override_settings(TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
    def test_variables_no_configuradas(self):
        exito, detalle = enviar_telegram("Hola")
        self.assertEqual((exito, detalle), (False, "Telegram no configurado"))

    @override_settings(TELEGRAM_BOT_TOKEN="TOKEN_SECRETO_123", TELEGRAM_CHAT_ID="-100987654")
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_envio_exitoso_y_formato_peticion(self, mock_urlopen):
        mock_urlopen.return_value = _respuesta_http({"ok": True, "result": {"message_id": 1}})
        exito, detalle = enviar_telegram("<b>Alerta</b>")
        self.assertTrue(exito)
        self.assertIn("Telegram", detalle)

        peticion = mock_urlopen.call_args[0][0]
        self.assertEqual(peticion.get_method(), "POST")
        self.assertEqual(mock_urlopen.call_args[1]["timeout"], 5)
        datos = json.loads(peticion.data.decode("utf-8"))
        self.assertEqual(datos, {
            "chat_id": "-100987654",
            "text": "<b>Alerta</b>",
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })

    @override_settings(TELEGRAM_BOT_TOKEN="TOKEN_SECRETO_123", TELEGRAM_CHAT_ID="-100987654")
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_recorta_texto_a_4000_caracteres(self, mock_urlopen):
        mock_urlopen.return_value = _respuesta_http({"ok": True})
        enviar_telegram("X" * 4500)
        datos = json.loads(mock_urlopen.call_args[0][0].data.decode("utf-8"))
        self.assertEqual(len(datos["text"]), 4000)

    @override_settings(TELEGRAM_BOT_TOKEN="TOKEN_SECRETO_123", TELEGRAM_CHAT_ID="-100987654")
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_respuesta_ok_false(self, mock_urlopen):
        mock_urlopen.return_value = _respuesta_http({"ok": False, "description": "Bad Request: chat not found"})
        exito, detalle = enviar_telegram("Prueba")
        self.assertFalse(exito)
        self.assertIn("chat not found", detalle)
        self.assertNotIn("TOKEN_SECRETO_123", detalle)

    @override_settings(TELEGRAM_BOT_TOKEN="TOKEN_SECRETO_123", TELEGRAM_CHAT_ID="-100987654")
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_http_error_401_lee_description_sin_exponer_token(self, mock_urlopen):
        cuerpo = io.BytesIO(json.dumps({"ok": False, "description": "Unauthorized"}).encode("utf-8"))
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.telegram.org/botTOKEN_SECRETO_123/sendMessage",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=cuerpo,
        )
        with self.assertLogs("autosen.externos", level="ERROR") as logs:
            exito, detalle = enviar_telegram("Prueba")
        self.assertFalse(exito)
        self.assertIn("401", detalle)
        self.assertIn("Unauthorized", detalle)
        self.assertNotIn("TOKEN_SECRETO_123", detalle)
        for linea in logs.output:
            self.assertNotIn("TOKEN_SECRETO_123", linea)

    @override_settings(TELEGRAM_BOT_TOKEN="TOKEN_SECRETO_123", TELEGRAM_CHAT_ID="-100987654")
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_url_error_y_timeout_y_json_invalido(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Fallo DNS en TOKEN_SECRETO_123")
        exito, detalle = enviar_telegram("Prueba")
        self.assertFalse(exito)
        self.assertNotIn("TOKEN_SECRETO_123", detalle)

        mock_urlopen.side_effect = TimeoutError("timed out")
        exito, detalle = enviar_telegram("Prueba")
        self.assertFalse(exito)
        self.assertIn("5 s", detalle)

        mock_urlopen.side_effect = None
        mock_urlopen.return_value = _respuesta_http("{json-roto")
        exito, detalle = enviar_telegram("Prueba")
        self.assertFalse(exito)
        self.assertIn("JSON", detalle)


class DespachoTelegramBDTests(TestCase):
    """Verifica el registro en BD, escape HTML y aislamiento de fallos en Telegram."""

    def test_sin_configurar_guarda_omitido(self):
        c = crear_cliente()
        v = crear_vehiculo(c)
        alerta = crear_alerta(v.pk, nivel=75, tipo="falla", fecha=datetime(2026, 11, 20, 10, 30, 0))
        NotificacionEnviada.objects.all().delete()

        with override_settings(TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID=""):
            despachar_notificacion_multicanal(alerta)

        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="TELEGRAM")
        self.assertEqual(reg.estado, "OMITIDO")
        self.assertEqual(reg.destinatario, "sin configurar")
        self.assertEqual(reg.detalle_error, "Telegram no configurado")

    @override_settings(TELEGRAM_BOT_TOKEN="TOK_TEST", TELEGRAM_CHAT_ID="-100555")
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_escape_html_en_datos_dinamicos_y_fallo_no_afecta_otros_canales(self, mock_urlopen):
        c = crear_cliente(nombre="Juan <b>Hacker</b>", apellido="Pérez & Cía")
        c.telefono = "<script>300</script>"
        c.save()
        v = crear_vehiculo(c, nombre="Auto <i>X</i>", placa="ABC123")
        alerta = crear_alerta(
            v.pk,
            nivel=80,
            tipo="falla",
            nombre_sensor="Sensor <b>O2</b>",
            tipo_sensor="O2&1",
            mensaje="Falla < crítica >",
            fecha=datetime(2026, 11, 20, 14, 15, 0),
        )
        NotificacionEnviada.objects.all().delete()

        # Primero probamos éxito y escape HTML
        mock_urlopen.return_value = _respuesta_http({"ok": True})
        despachar_notificacion_multicanal(alerta)
        reg_ok = NotificacionEnviada.objects.get(alerta=alerta, canal="TELEGRAM")
        self.assertEqual(reg_ok.estado, "ENVIADO")
        self.assertIsNone(reg_ok.detalle_error)
        self.assertEqual(reg_ok.destinatario, "-100555")
        self.assertIn("Juan &lt;b&gt;Hacker&lt;/b&gt;", reg_ok.mensaje)
        self.assertIn("Pérez &amp; Cía", reg_ok.mensaje)
        self.assertIn("Auto &lt;i&gt;X&lt;/i&gt;", reg_ok.mensaje)
        self.assertIn("Sensor &lt;b&gt;O2&lt;/b&gt;", reg_ok.mensaje)
        self.assertIn("Falla &lt; crítica &gt;", reg_ok.mensaje)
        self.assertIn("FALLA CRÍTICA", reg_ok.mensaje)

        # Ahora simulamos fallo en Telegram y verificamos que los demás canales se siguen creando
        NotificacionEnviada.objects.all().delete()
        mock_urlopen.side_effect = TimeoutError()
        despachar_notificacion_multicanal(alerta)
        reg_fail = NotificacionEnviada.objects.get(alerta=alerta, canal="TELEGRAM")
        self.assertEqual(reg_fail.estado, "FALLIDO")
        self.assertIn("5 s", reg_fail.detalle_error)
        self.assertTrue(NotificacionEnviada.objects.filter(alerta=alerta).exclude(canal="TELEGRAM").exists())


class EmailServicioTests(TestCase):
    """Pruebas del canal Email con locmem (mail.outbox), omisiones y errores SMTP."""

    @override_settings(
        EMAIL_HOST_USER="alertas@gmail.com",
        EMAIL_HOST_PASSWORD="CLAVE_APP_SECRETA",
        DEFAULT_FROM_EMAIL="AutoSen <alertas@gmail.com>",
        SITE_URL="http://localhost:8080",
    )
    def test_envia_email_texto_y_html_con_autoescape(self):
        c = crear_cliente(correo="cliente@ejemplo.com", nombre="Ana <script>", apellido="Gómez")
        v = crear_vehiculo(c, nombre="Mazda 3", placa="XYZ789")
        alerta = crear_alerta(
            v.pk,
            nivel=85,
            tipo="falla",
            nombre_sensor="Temperatura <b>ECT</b>",
            tipo_sensor="ECT",
            mensaje="Sobrecalentamiento > 110°C",
            fecha=datetime(2026, 11, 20, 16, 0, 0),
        )
        NotificacionEnviada.objects.all().delete()
        mail.outbox.clear()

        despachar_notificacion_multicanal(alerta)

        self.assertEqual(len(mail.outbox), 1)
        enviado = mail.outbox[0]
        self.assertEqual(enviado.to, ["cliente@ejemplo.com"])
        self.assertIn("FALLA CRÍTICA", enviado.subject)
        self.assertIn("XYZ789", enviado.subject)
        self.assertEqual(len(enviado.alternatives), 1)
        html_enviado, mime = enviado.alternatives[0]
        self.assertEqual(mime, "text/html")
        self.assertIn("#dc2626", html_enviado)
        self.assertIn("http://localhost:8080/dashboard", html_enviado)
        # Autoescape de Django activo
        self.assertIn("Ana &lt;script&gt;", html_enviado)
        self.assertIn("Temperatura &lt;b&gt;ECT&lt;/b&gt;", html_enviado)
        self.assertNotIn("<script>", html_enviado)

        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="EMAIL")
        self.assertEqual(reg.estado, "ENVIADO")
        self.assertIsNone(reg.detalle_error)

    @override_settings(EMAIL_HOST_USER="alertas@gmail.com", EMAIL_HOST_PASSWORD="CLAVE_APP_SECRETA")
    def test_color_naranja_para_advertencia(self):
        c = crear_cliente(correo="cliente@ejemplo.com")
        v = crear_vehiculo(c, placa="ADV123")
        alerta = crear_alerta(v.pk, nivel=50, tipo="advertencia")
        mail.outbox.clear()
        despachar_notificacion_multicanal(alerta)
        html_enviado, _ = mail.outbox[0].alternatives[0]
        self.assertIn("#ea580c", html_enviado)

    @override_settings(EMAIL_HOST_USER="alertas@gmail.com", EMAIL_HOST_PASSWORD="CLAVE_APP_SECRETA")
    def test_cliente_sin_correo_queda_omitido(self):
        c = crear_cliente(correo="   ")
        v = crear_vehiculo(c)
        alerta = crear_alerta(v.pk, nivel=75, tipo="falla")
        NotificacionEnviada.objects.all().delete()
        mail.outbox.clear()

        despachar_notificacion_multicanal(alerta)

        self.assertEqual(len(mail.outbox), 0)
        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="EMAIL")
        self.assertEqual(reg.estado, "OMITIDO")
        self.assertIn("sin correo", reg.detalle_error.lower())

    @override_settings(EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD="")
    def test_email_no_configurado_queda_omitido(self):
        c = crear_cliente(correo="cliente@ejemplo.com")
        v = crear_vehiculo(c)
        alerta = crear_alerta(v.pk, nivel=75, tipo="falla")
        NotificacionEnviada.objects.all().delete()

        despachar_notificacion_multicanal(alerta)

        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="EMAIL")
        self.assertEqual((reg.estado, reg.detalle_error), ("OMITIDO", "Email no configurado"))

    @override_settings(EMAIL_HOST_USER="alertas@gmail.com", EMAIL_HOST_PASSWORD="CLAVE_APP_SECRETA")
    @mock.patch("core.servicios_externos.EmailMultiAlternatives.send")
    def test_error_smtp_simulado_queda_fallido_sin_filtrar_clave(self, mock_send):
        mock_send.side_effect = smtplib.SMTPAuthenticationError(535, b"Invalid credentials CLAVE_APP_SECRETA")
        c = crear_cliente(correo="cliente@ejemplo.com")
        v = crear_vehiculo(c)
        alerta = crear_alerta(v.pk, nivel=80, tipo="falla")
        NotificacionEnviada.objects.all().delete()

        with self.assertLogs("autosen.externos", level="ERROR") as logs:
            despachar_notificacion_multicanal(alerta)

        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="EMAIL")
        self.assertEqual(reg.estado, "FALLIDO")
        self.assertIn("SMTP", reg.detalle_error)
        self.assertNotIn("CLAVE_APP_SECRETA", reg.detalle_error)
        for linea in logs.output:
            self.assertNotIn("CLAVE_APP_SECRETA", linea)

        # También verificamos socket.timeout directo en enviar_email
        mock_send.side_effect = TimeoutError("timeout")
        exito, detalle = enviar_email("cliente@ejemplo.com", "Asunto", "Texto", "<p>HTML</p>")
        self.assertFalse(exito)
        self.assertIn("SMTP", detalle)


class WhatsAppNormalizacionYServicioTests(TestCase):
    """Pruebas de normalización de teléfonos y de WhatsApp Cloud API de Meta."""

    def test_normalizacion_telefonos(self):
        self.assertEqual(normalizar_telefono_whatsapp("3001234567"), "573001234567")
        self.assertEqual(normalizar_telefono_whatsapp("+57 300 123 4567"), "573001234567")
        self.assertEqual(normalizar_telefono_whatsapp("300-123-4567"), "573001234567")
        self.assertEqual(normalizar_telefono_whatsapp("+1 305 555 0199"), "13055550199")
        for invalido in (None, "", "   ", "12345", "abcdefghij", "2001234567", "+57 2001234567", "00573001234567",
                         "99999999999999999"):
            self.assertIsNone(normalizar_telefono_whatsapp(invalido), msg=str(invalido))

    @override_settings(
        WHATSAPP_TOKEN="META_TOKEN_SUPER_SECRETO",
        WHATSAPP_PHONE_NUMBER_ID="10987654321",
        WHATSAPP_API_VERSION="v21.0",
    )
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_envio_exitoso_meta_y_formato_peticion(self, mock_urlopen):
        mock_urlopen.return_value = _respuesta_http({"messages": [{"id": "wamid.HBgM"}]})
        exito, detalle = enviar_whatsapp("+57 300 123 4567", "Hola *Joel*")
        self.assertTrue(exito)
        self.assertIn("WhatsApp", detalle)

        peticion = mock_urlopen.call_args[0][0]
        self.assertEqual(peticion.full_url, "https://graph.facebook.com/v21.0/10987654321/messages")
        self.assertEqual(peticion.get_header("Authorization"), "Bearer META_TOKEN_SUPER_SECRETO")
        self.assertEqual(mock_urlopen.call_args[1]["timeout"], 5)
        cuerpo = json.loads(peticion.data.decode("utf-8"))
        self.assertEqual(cuerpo, {
            "messaging_product": "whatsapp",
            "to": "573001234567",
            "type": "text",
            "text": {"preview_url": False, "body": "Hola *Joel*"},
        })

    @override_settings(
        WHATSAPP_TOKEN="META_TOKEN_SUPER_SECRETO",
        WHATSAPP_PHONE_NUMBER_ID="10987654321",
        WHATSAPP_API_VERSION="v21.0",
    )
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_errores_meta_131047_131030_401_y_timeout_sin_exponer_token(self, mock_urlopen):
        casos = [
            (400, {"error": {"code": 131047, "message": "Re-engagement message"}},
             "últimas 24 horas"),
            (400, {"error": {"code": 131030, "message": "Recipient phone number not in allowed list"}},
             "lista de destinatarios permitidos"),
            (401, {"error": {"code": 190, "message": "Invalid OAuth access token META_TOKEN_SUPER_SECRETO"}},
             "Token de WhatsApp inválido o vencido."),
        ]
        for http_code, payload, texto_esperado in casos:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="https://graph.facebook.com/v21.0/10987654321/messages",
                code=http_code,
                msg="Error",
                hdrs=None,
                fp=io.BytesIO(json.dumps(payload).encode("utf-8")),
            )
            with self.assertLogs("autosen.externos", level="ERROR") as logs:
                exito, detalle = enviar_whatsapp("3001234567", "Prueba")
            self.assertFalse(exito)
            self.assertIn(texto_esperado, detalle)
            self.assertNotIn("META_TOKEN_SUPER_SECRETO", detalle)
            for linea in logs.output:
                self.assertNotIn("META_TOKEN_SUPER_SECRETO", linea)

        mock_urlopen.side_effect = TimeoutError()
        exito, detalle = enviar_whatsapp("3001234567", "Prueba")
        self.assertFalse(exito)
        self.assertIn("5 s", detalle)

    @override_settings(
        WHATSAPP_TOKEN="META_TOKEN_SUPER_SECRETO",
        WHATSAPP_PHONE_NUMBER_ID="10987654321",
        WHATSAPP_API_VERSION="v21.0",
    )
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_despacho_sin_telefono_telefono_invalido_y_exitoso(self, mock_urlopen):
        # 1. Cliente sin teléfono -> OMITIDO
        c = crear_cliente(correo="wa@ejemplo.com")
        v = crear_vehiculo(c, placa="WAA111")
        alerta = crear_alerta(v.pk, nivel=75, tipo="falla")
        NotificacionEnviada.objects.all().delete()

        despachar_notificacion_multicanal(alerta)
        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="WHATSAPP")
        self.assertEqual(reg.estado, "OMITIDO")

        # 2. Cliente con teléfono inválido -> FALLIDO ("Teléfono inválido")
        c.telefono = "123-malo"
        c.save()
        NotificacionEnviada.objects.all().delete()
        despachar_notificacion_multicanal(alerta)
        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="WHATSAPP")
        self.assertEqual((reg.estado, reg.detalle_error), ("FALLIDO", "Teléfono inválido"))

        # 3. Cliente con celular colombiano de 10 dígitos -> ENVIADO a 57300...
        c.telefono = "3001234567"
        c.save()
        NotificacionEnviada.objects.all().delete()
        mock_urlopen.return_value = _respuesta_http({"messages": [{"id": "wamid.1"}]})
        despachar_notificacion_multicanal(alerta)
        reg = NotificacionEnviada.objects.get(alerta=alerta, canal="WHATSAPP")
        self.assertEqual(reg.estado, "ENVIADO")
        self.assertEqual(reg.destinatario, "573001234567")
        self.assertIn("Revisa tu panel de AutoSen", reg.mensaje)
        self.assertIsNone(reg.detalle_error)


class NavegadorNotificacionesTests(TestCase):
    """Pruebas del canal NAVEGADOR, endpoint /mostrada y filtrado de /api/alertas/en-vivo."""

    def test_canal_navegador_se_crea_en_cola_y_mostrada_pasa_a_enviado(self):
        dueno = crear_cliente(correo="dueno@ejemplo.com")
        otro = crear_cliente(correo="otro@ejemplo.com")
        v_dueno = crear_vehiculo(dueno, placa="OWN123")
        v_otro = crear_vehiculo(otro, placa="OTH999")

        alerta_dueno = crear_alerta(v_dueno.pk, nivel=85, tipo="falla", nombre_sensor="Sensor O2")
        alerta_otro = crear_alerta(v_otro.pk, nivel=72, tipo="falla", nombre_sensor="Sensor MAP")
        NotificacionEnviada.objects.all().delete()

        despachar_notificacion_multicanal(alerta_dueno)
        despachar_notificacion_multicanal(alerta_otro)

        reg = NotificacionEnviada.objects.get(alerta=alerta_dueno, canal="NAVEGADOR")
        self.assertEqual(reg.estado, "EN_COLA")

        # Sin sesión -> 403
        sin_sesion = Client(enforce_csrf_checks=True)
        sin_sesion.get("/login")
        csrf_anon = sin_sesion.cookies["csrftoken"].value
        r_anon = sin_sesion.post(
            f"/api/alertas/{alerta_dueno.pk}/mostrada",
            HTTP_X_CSRFTOKEN=csrf_anon,
        )
        self.assertEqual(r_anon.status_code, 403)

        # Otro cliente intenta marcar alerta ajena -> 403 y sigue EN_COLA
        cli_otro = Client(enforce_csrf_checks=True)
        login_cliente(cli_otro, otro)
        cli_otro.get("/dashboard")
        csrf_otro = cli_otro.cookies["csrftoken"].value
        r_ajena = cli_otro.post(
            f"/api/alertas/{alerta_dueno.pk}/mostrada",
            HTTP_X_CSRFTOKEN=csrf_otro,
        )
        self.assertEqual(r_ajena.status_code, 403)
        reg.refresh_from_db()
        self.assertEqual(reg.estado, "EN_COLA")

        # Sin token CSRF falla con 403
        cli_dueno = Client(enforce_csrf_checks=True)
        login_cliente(cli_dueno, dueno)
        r_sin_csrf = cli_dueno.post(f"/api/alertas/{alerta_dueno.pk}/mostrada")
        self.assertEqual(r_sin_csrf.status_code, 403)

        # El dueño legítimo con CSRF la marca como ENVIADO
        cli_dueno.get("/dashboard")
        csrf_dueno = cli_dueno.cookies["csrftoken"].value
        r_ok = cli_dueno.post(
            f"/api/alertas/{alerta_dueno.pk}/mostrada",
            HTTP_X_CSRFTOKEN=csrf_dueno,
        )
        self.assertEqual(r_ok.status_code, 200)
        self.assertEqual(r_ok.json(), {"ok": True, "estado": "ENVIADO"})
        reg.refresh_from_db()
        self.assertEqual(reg.estado, "ENVIADO")

        # Alerta inexistente -> 404
        r_404 = cli_dueno.post("/api/alertas/999999/mostrada", HTTP_X_CSRFTOKEN=csrf_dueno)
        self.assertEqual(r_404.status_code, 404)

    def test_alertas_en_vivo_filtra_por_cliente_y_admin_ve_todas(self):
        c1 = crear_cliente(correo="c1@ejemplo.com")
        c2 = crear_cliente(correo="c2@ejemplo.com")
        v1 = crear_vehiculo(c1, placa="AAA111")
        v2 = crear_vehiculo(c2, placa="BBB222")
        a1 = crear_alerta(v1.pk, nivel=80, tipo="falla", nombre_sensor="O2")
        a2 = crear_alerta(v2.pk, nivel=85, tipo="falla", nombre_sensor="ECT")

        # Sin sesión -> 403
        self.assertEqual(self.client.get("/api/alertas/en-vivo").status_code, 403)

        # Cliente 1 solo ve las alertas de su vehículo AAA111
        cli1 = Client()
        login_cliente(cli1, c1)
        datos_c1 = cli1.get("/api/alertas/en-vivo").json()
        self.assertEqual([x["id"] for x in datos_c1["alertas"]], [a1.pk])

        # Incluso si envía ?modo=admin no puede ver las de otro cliente
        datos_c1_forzado = cli1.get("/api/alertas/en-vivo?modo=admin").json()
        self.assertEqual([x["id"] for x in datos_c1_forzado["alertas"]], [a1.pk])

        # Administrador ve todas las alertas
        cli_admin = Client()
        login_admin(cli_admin, crear_usuario(rol="ADMIN"))
        datos_admin = cli_admin.get("/api/alertas/en-vivo?modo=admin").json()
        self.assertEqual({x["id"] for x in datos_admin["alertas"]}, {a1.pk, a2.pk})


class SegundoPlanoYPanelAdminYComandoTests(TestCase):
    """Pruebas de vistas admin (Probar canales y Reintentar), auditoría y comando probar_canales."""

    def test_probar_canales_y_reintentar_solo_admin_y_solo_post(self):
        c = crear_cliente()
        v = crear_vehiculo(c)
        alerta = crear_alerta(v.pk, nivel=80, tipo="falla")
        notif = NotificacionEnviada.objects.create(
            canal="TELEGRAM",
            destinatario="-100111",
            asunto="Alerta",
            mensaje="<b>Falla</b>",
            estado="FALLIDO",
            detalle_error="Timeout previo",
            alerta=alerta,
        )

        # Sin sesión redirige a /admin/login
        self.assertRedirects(
            self.client.post("/admin/notificaciones/probar", {"canal": "TELEGRAM"}),
            "/admin/login",
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.post(f"/admin/notificaciones/{notif.pk}/reintentar"),
            "/admin/login",
            fetch_redirect_response=False,
        )

        # Con sesión de cliente tampoco puede entrar
        login_cliente(self.client, c)
        self.assertRedirects(
            self.client.post("/admin/notificaciones/probar", {"canal": "TELEGRAM"}),
            "/admin/login",
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.post(f"/admin/notificaciones/{notif.pk}/reintentar"),
            "/admin/login",
            fetch_redirect_response=False,
        )

        # Con sesión de admin pero método GET -> 405 Method Not Allowed
        cli_admin = Client()
        admin = crear_usuario(correo="admin@autosen.com", rol="ADMIN")
        login_admin(cli_admin, admin)
        self.assertEqual(cli_admin.get("/admin/notificaciones/probar").status_code, 405)
        self.assertEqual(cli_admin.get(f"/admin/notificaciones/{notif.pk}/reintentar").status_code, 405)

    @override_settings(
        TELEGRAM_BOT_TOKEN="TOK",
        TELEGRAM_CHAT_ID="-100222",
        EMAIL_HOST_USER="admin@autosen.com",
        EMAIL_HOST_PASSWORD="CLAVE",
        WHATSAPP_TOKEN="WA_TOK",
        WHATSAPP_PHONE_NUMBER_ID="999",
        WHATSAPP_API_VERSION="v21.0",
    )
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_probar_canales_reintentar_filtros_y_auditoria(self, mock_urlopen):
        cli_admin = Client(enforce_csrf_checks=True)
        admin = crear_usuario(correo="admin@autosen.com", rol="SUPERADMIN")
        login_admin(cli_admin, admin)

        # Probar Telegram con CSRF
        mock_urlopen.return_value = _respuesta_http({"ok": True})
        cli_admin.get("/admin/notificaciones")
        csrf = cli_admin.cookies["csrftoken"].value
        r_tg = cli_admin.post(
            "/admin/notificaciones/probar",
            {"canal": "TELEGRAM", "csrfmiddlewaretoken": csrf},
            follow=True,
        )
        self.assertContains(r_tg, "Telegram:")

        # Probar Email
        mail.outbox.clear()
        csrf = cli_admin.cookies["csrftoken"].value
        r_em = cli_admin.post(
            "/admin/notificaciones/probar",
            {"canal": "EMAIL", "csrfmiddlewaretoken": csrf},
            follow=True,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Prueba de conexión AutoSen", mail.outbox[0].subject)
        self.assertContains(r_em, "Correo enviado correctamente")

        # Probar WhatsApp con teléfono inválido y luego válido
        csrf = cli_admin.cookies["csrftoken"].value
        r_wa_bad = cli_admin.post(
            "/admin/notificaciones/probar",
            {"canal": "WHATSAPP", "telefono": "abc", "csrfmiddlewaretoken": csrf},
            follow=True,
        )
        self.assertContains(r_wa_bad, "Teléfono inválido")

        mock_urlopen.return_value = _respuesta_http({"messages": [{"id": "wamid.test"}]})
        csrf = cli_admin.cookies["csrftoken"].value
        r_wa_ok = cli_admin.post(
            "/admin/notificaciones/probar",
            {"canal": "WHATSAPP", "telefono": "3001234567", "csrfmiddlewaretoken": csrf},
            follow=True,
        )
        self.assertContains(r_wa_ok, "Mensaje enviado por WhatsApp")

        # Reintentar notificación FALLIDA pasa a ENVIADO y registra auditoría
        c = crear_cliente()
        v = crear_vehiculo(c)
        alerta = crear_alerta(v.pk, nivel=80, tipo="falla")
        notif = NotificacionEnviada.objects.create(
            canal="TELEGRAM",
            destinatario="-100222",
            asunto="Alerta",
            mensaje="<b>Reintento</b>",
            estado="FALLIDO",
            detalle_error="Error temporal",
            alerta=alerta,
        )
        mock_urlopen.return_value = _respuesta_http({"ok": True})
        csrf = cli_admin.cookies["csrftoken"].value
        r_retry = cli_admin.post(
            f"/admin/notificaciones/{notif.pk}/reintentar",
            {"csrfmiddlewaretoken": csrf},
            follow=True,
        )
        notif.refresh_from_db()
        self.assertEqual(notif.estado, "ENVIADO")
        self.assertIsNone(notif.detalle_error)
        self.assertContains(r_retry, "Enviado correctamente")
        self.assertTrue(RegistroAuditoria.objects.filter(accion="REINTENTAR", entidad="NOTIFICACION").exists())

        # Verificar filtro por canal y por estado en la vista
        r_filtro = cli_admin.get("/admin/notificaciones?canal=TELEGRAM&estado=ENVIADO")
        self.assertEqual(r_filtro.status_code, 200)
        self.assertEqual(len(r_filtro.context["notificaciones"]), 1)

    @override_settings(
        TELEGRAM_BOT_TOKEN="TOK",
        TELEGRAM_CHAT_ID="-100333",
        EMAIL_HOST_USER="bot@autosen.com",
        EMAIL_HOST_PASSWORD="CLAVE",
        WHATSAPP_TOKEN="WA_TOK",
        WHATSAPP_PHONE_NUMBER_ID="888",
        WHATSAPP_API_VERSION="v21.0",
    )
    @mock.patch("core.servicios_externos.urllib.request.urlopen")
    def test_comando_probar_canales_con_servicios_simulados(self, mock_urlopen):
        def _side_effect(req, timeout=5):
            if "telegram.org" in req.full_url:
                return _respuesta_http({"ok": True})
            return _respuesta_http({"messages": [{"id": "wamid.cli"}]})

        mock_urlopen.side_effect = _side_effect
        mail.outbox.clear()
        salida = io.StringIO()
        call_command("probar_canales", "--email", "destino@ejemplo.com", "--whatsapp", "3001234567", stdout=salida)
        texto = salida.getvalue()
        self.assertIn("TELEGRAM", texto)
        self.assertIn("EMAIL", texto)
        self.assertIn("WHATSAPP", texto)
        self.assertEqual(texto.count("ENVIADO"), 3)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["destino@ejemplo.com"])


class DespachoAsincronoTransactionTests(TransactionTestCase):
    """Verifica que NOTIFICACIONES_ASINCRONAS=True despache en un hilo tras on_commit y cierre la conexión."""

    @override_settings(NOTIFICACIONES_ASINCRONAS=True)
    def test_envio_en_segundo_plano_con_on_commit_y_thread(self):
        from api.obd2 import crear_alerta_si_corresponde

        c = crear_cliente(correo="async@ejemplo.com")
        v = crear_vehiculo(c, placa="ASY123")

        evento_fin = mock.MagicMock()
        hilos_creados = []
        thread_real = __import__("threading").Thread

        def _crear_hilo(*args, **kwargs):
            hilo = thread_real(*args, **kwargs)
            hilos_creados.append(hilo)
            return hilo

        with mock.patch("core.notificaciones.threading.Thread", side_effect=_crear_hilo):
            alerta = crear_alerta_si_corresponde(v.pk, "Sensor O2", "O2", 0.95, 85, " V")
            for h in hilos_creados:
                h.join(timeout=5)

        self.assertEqual(len(hilos_creados), 1)
        self.assertTrue(hilos_creados[0].daemon)
        self.assertEqual(NotificacionEnviada.objects.filter(alerta=alerta).count(), 4)
        self.assertEqual(
            NotificacionEnviada.objects.get(alerta=alerta, canal="NAVEGADOR").estado,
            "EN_COLA",
        )
