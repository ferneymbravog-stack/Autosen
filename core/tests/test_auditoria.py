"""Pruebas automatizadas de auditoría conectada a Usuario, login/logout/fallos y filtros."""
from datetime import datetime
from importlib import import_module
import io
from contextlib import redirect_stdout

from django.apps import apps as django_apps
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext

from core.models import Cliente, RegistroAuditoria, Usuario
from core.tests.fabricas import CLAVE, _post_con_csrf, crear_cliente, crear_usuario, login_admin

enlazar_auditoria_con_usuarios = import_module(
    "core.migrations.0012_enlazar_auditoria_usuarios"
).enlazar_auditoria_con_usuarios


class AuditoriaAutenticacionYAccionesTests(TestCase):
    """Verifica FK de administrador, LOGIN, LOGIN_FALLIDO sin clave, LOGOUT y preservación histórica."""

    def test_login_exitoso_queda_con_admin_y_no_como_sistema(self):
        admin = crear_usuario(correo="jefe@autosen.com", nombre="Carlos Jefe", rol="SUPERADMIN")
        cli = Client()
        r = cli.post(
            "/admin/login",
            {"correo": "jefe@autosen.com", "contrasena": CLAVE},
            HTTP_X_FORWARDED_FOR="190.24.10.5, 10.0.0.1",
        )
        self.assertRedirects(r, "/admin", fetch_redirect_response=False)

        reg = RegistroAuditoria.objects.get(accion="LOGIN")
        self.assertEqual(reg.usuario, admin)
        self.assertEqual(reg.usuario_correo, "jefe@autosen.com")
        self.assertEqual(reg.usuario_rol, "SUPERADMIN")
        self.assertNotEqual(reg.usuario_correo, "Sistema")
        self.assertEqual(reg.ip, "190.24.10.5")

    def test_login_fallido_correo_inexistente_y_clave_incorrecta_nunca_guarda_clave(self):
        admin = crear_usuario(correo="soporte@autosen.com", nombre="Laura Soporte", rol="SOPORTE")
        clave_intentada = "ClaveSuperSecretaErronea999!"

        # 1. Correo que no existe -> usuario=None, rol NO_REGISTRADO
        r1 = self.client.post(
            "/admin/login",
            {"correo": "intruso@desconocido.com", "contrasena": clave_intentada},
            HTTP_X_FORWARDED_FOR="200.10.20.30",
        )
        self.assertRedirects(r1, "/admin/login?error", fetch_redirect_response=False)

        reg_inexistente = RegistroAuditoria.objects.get(usuario_correo="intruso@desconocido.com")
        self.assertEqual(reg_inexistente.accion, "LOGIN_FALLIDO")
        self.assertIsNone(reg_inexistente.usuario)
        self.assertEqual(reg_inexistente.usuario_rol, "NO_REGISTRADO")
        self.assertEqual(reg_inexistente.ip, "200.10.20.30")

        # 2. Correo existente pero contraseña mala -> usuario=admin
        r2 = self.client.post(
            "/admin/login",
            {"correo": "SOPORTE@autosen.com", "contrasena": clave_intentada},
        )
        self.assertRedirects(r2, "/admin/login?error", fetch_redirect_response=False)

        reg_clave_mala = RegistroAuditoria.objects.filter(accion="LOGIN_FALLIDO", usuario=admin).get()
        self.assertEqual(reg_clave_mala.usuario, admin)
        self.assertEqual(reg_clave_mala.usuario_correo, "soporte@autosen.com")

        # NUNCA debe aparecer la contraseña intentada en ningún campo de la auditoría
        for reg in RegistroAuditoria.objects.all():
            texto_completo = f"{reg.usuario_correo} {reg.usuario_rol} {reg.accion} {reg.entidad} {reg.descripcion}"
            self.assertNotIn(clave_intentada, texto_completo)

    def test_logout_y_acciones_panel_guardan_fk_y_borrar_admin_conserva_historial(self):
        superadmin = crear_usuario(correo="super@autosen.com", nombre="Super Uno", rol="SUPERADMIN")
        operador = crear_usuario(correo="operador@autosen.com", nombre="Operador Dos", rol="ADMIN")

        # El operador inicia sesión, crea un cliente y cierra sesión
        cli_op = Client()
        login_admin(cli_op, operador)
        cli_op.post(
            "/admin/cliente/crear",
            {"nombre": "Mario", "apellido": "Ruiz", "correo": "mario@test.com", "contrasena": "clave123"},
        )
        cli_op.post("/admin/logout")

        acciones_op = list(
            RegistroAuditoria.objects.filter(usuario=operador).values_list("accion", flat=True)
        )
        self.assertIn("LOGIN", acciones_op)
        self.assertIn("CREAR", acciones_op)
        self.assertIn("LOGOUT", acciones_op)

        # El superadmin elimina al operador -> sus registros quedan con usuario=None y correo intacto
        cli_super = Client()
        login_admin(cli_super, superadmin)
        cli_super.post(f"/admin/usuario/{operador.pk}/eliminar")
        self.assertFalse(Usuario.objects.filter(pk=operador.pk).exists())

        regs_huerfanos = list(RegistroAuditoria.objects.filter(usuario_correo="operador@autosen.com"))
        self.assertEqual(len(regs_huerfanos), 3)
        for reg in regs_huerfanos:
            self.assertIsNone(reg.usuario)
            self.assertEqual(reg.usuario_correo, "operador@autosen.com")
            self.assertEqual(reg.usuario_rol, "ADMIN")

    def test_migracion_0012_enlaza_por_correo_sin_distinguir_mayusculas(self):
        admin = crear_usuario(correo=" Ana.Admin@AutoSen.com ", nombre="Ana", rol="ADMIN")
        r_match = RegistroAuditoria.objects.create(
            usuario=None,
            usuario_correo="ana.admin@autosen.com",
            usuario_rol="ADMIN",
            accion="CREAR",
            entidad="CLIENTE",
            entidad_id="1",
            descripcion="Creación histórica",
        )
        r_sin_match = RegistroAuditoria.objects.create(
            usuario=None,
            usuario_correo="exempleado@autosen.com",
            usuario_rol="ADMIN",
            accion="EDITAR",
            entidad="CLIENTE",
            entidad_id="1",
            descripcion="Edición histórica",
        )

        salida = io.StringIO()
        with redirect_stdout(salida):
            enlazar_auditoria_con_usuarios(django_apps, None)

        r_match.refresh_from_db()
        r_sin_match.refresh_from_db()
        self.assertEqual(r_match.usuario, admin)
        self.assertIsNone(r_sin_match.usuario)
        self.assertIn("1", salida.getvalue())


class VistaAuditoriaFiltrosYSelectRelatedTests(TestCase):
    """Verifica etiquetas visuales, filtros (admin, acción, fechas) y ausencia de N+1 en /admin/auditoria."""

    def setUp(self):
        self.superadmin = crear_usuario(correo="root@autosen.com", nombre="Root Principal", rol="SUPERADMIN")
        self.otro_admin = crear_usuario(correo="ana@autosen.com", nombre="Ana Gestora", rol="ADMIN")
        login_admin(self.client, self.superadmin)

    def test_muestra_nombre_fk_etiquetas_eliminado_no_registrado_y_filtros(self):
        # 1. Registro de otro_admin activo
        r_activo = RegistroAuditoria.objects.create(
            usuario=self.otro_admin,
            usuario_correo=self.otro_admin.correo,
            usuario_rol="ADMIN",
            accion="CREAR",
            entidad="VEHICULO",
            entidad_id="10",
            descripcion="Alta vehículo",
        )
        RegistroAuditoria.objects.filter(pk=r_activo.pk).update(fecha=datetime(2026, 11, 10, 9, 0, 0))

        # 2. Registro de un usuario ya eliminado (usuario=None, rol ADMIN)
        r_eliminado = RegistroAuditoria.objects.create(
            usuario=None,
            usuario_correo="borrado@autosen.com",
            usuario_rol="ADMIN",
            accion="ELIMINAR",
            entidad="SENSOR",
            entidad_id="5",
            descripcion="Baja sensor",
        )
        RegistroAuditoria.objects.filter(pk=r_eliminado.pk).update(fecha=datetime(2026, 11, 15, 14, 0, 0))

        # 3. Registro de LOGIN_FALLIDO de correo no registrado
        r_no_reg = RegistroAuditoria.objects.create(
            usuario=None,
            usuario_correo="hacker@externo.com",
            usuario_rol="NO_REGISTRADO",
            accion="LOGIN_FALLIDO",
            entidad="SESION",
            entidad_id="",
            descripcion="Intento fallido",
        )
        RegistroAuditoria.objects.filter(pk=r_no_reg.pk).update(fecha=datetime(2026, 11, 20, 18, 30, 0))

        # Vista completa muestra nombre desde FK y etiquetas diferenciadas
        resp = self.client.get("/admin/auditoria")
        self.assertContains(resp, "Ana Gestora")
        self.assertContains(resp, "(usuario eliminado)")
        self.assertContains(resp, "(no registrado)")

        # Filtro por administrador específico
        r_por_admin = self.client.get(f"/admin/auditoria?usuario={self.otro_admin.pk}")
        self.assertEqual([x.pk for x in r_por_admin.context["registros"]], [r_activo.pk])

        # Filtro por acción LOGIN_FALLIDO
        r_por_accion = self.client.get("/admin/auditoria?accion=LOGIN_FALLIDO")
        self.assertEqual([x.pk for x in r_por_accion.context["registros"]], [r_no_reg.pk])

        # Filtro por rango de fechas (solo del 14 al 16 de noviembre -> r_eliminado)
        r_por_fechas = self.client.get("/admin/auditoria?fecha_desde=2026-11-14&fecha_hasta=2026-11-16")
        self.assertEqual([x.pk for x in r_por_fechas.context["registros"]], [r_eliminado.pk])

        # Verificar select_related("usuario"): agregar 15 registros más NO incrementa el número de queries
        with CaptureQueriesContext(connection) as q_antes:
            self.assertEqual(self.client.get("/admin/auditoria").status_code, 200)
        for i in range(15):
            RegistroAuditoria.objects.create(
                usuario=self.otro_admin,
                usuario_correo=self.otro_admin.correo,
                usuario_rol="ADMIN",
                accion="EDITAR",
                entidad="SENSOR",
                entidad_id=str(i),
                descripcion=f"Ajuste {i}",
            )
        with CaptureQueriesContext(connection) as q_despues:
            self.assertEqual(self.client.get("/admin/auditoria").status_code, 200)
        self.assertEqual(len(q_despues), len(q_antes))
