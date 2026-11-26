"""Módulo de auditoría inmutable para acciones de administradores y autenticación del panel."""
from core.auth import admin_actual
from core.models import RegistroAuditoria, Usuario


def obtener_ip_cliente(request) -> str:
    """Obtiene la dirección IP del cliente priorizando X-Forwarded-For."""
    if not request:
        return "127.0.0.1"
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


def registrar_auditoria(
    request,
    accion: str,
    entidad: str,
    entidad_id,
    descripcion: str,
    usuario: Usuario | None = None,
) -> RegistroAuditoria:
    """Registra una acción administrativa en la bitácora inmutable junto con la FK del administrador."""
    admin = usuario or getattr(request, "admin", None) or admin_actual(request)
    if admin is not None:
        usuario_correo = admin.correo or "admin@autosen.com"
        usuario_rol = admin.rol or "ADMIN"
    else:
        usuario_correo = "Sistema"
        usuario_rol = "SISTEMA"

    return RegistroAuditoria.objects.create(
        usuario=admin,
        usuario_correo=usuario_correo,
        usuario_rol=str(usuario_rol).upper(),
        accion=str(accion).upper(),
        entidad=str(entidad).upper(),
        entidad_id=str(entidad_id) if entidad_id is not None else "",
        descripcion=descripcion,
        ip=obtener_ip_cliente(request),
    )


def auditar_autenticacion(
    request,
    usuario_correo: str,
    exito: bool,
    usuario: Usuario | None = None,
) -> RegistroAuditoria:
    """Registra eventos de autenticación del panel administrativo sin almacenar jamás la contraseña."""
    correo_limpio = (usuario_correo or "").strip() or "(sin correo)"
    if exito and usuario is not None:
        accion = "LOGIN"
        rol = (usuario.rol or "ADMIN").upper()
        descripcion = f"Inicio de sesión exitoso como {usuario.rol} ({usuario.correo})"
        correo_guardar = usuario.correo
    else:
        accion = "LOGIN_FALLIDO"
        if usuario is not None:
            rol = (usuario.rol or "ADMIN").upper()
            descripcion = f"Intento fallido de inicio de sesión para administrador existente ({correo_limpio})"
            correo_guardar = usuario.correo
        else:
            rol = "NO_REGISTRADO"
            descripcion = f"Intento fallido de inicio de sesión con correo no registrado ({correo_limpio})"
            correo_guardar = correo_limpio

    return RegistroAuditoria.objects.create(
        usuario=usuario,
        usuario_correo=correo_guardar[:100],
        usuario_rol=rol[:30],
        accion=accion,
        entidad="SESION",
        entidad_id=str(usuario.pk) if usuario is not None else "",
        descripcion=descripcion,
        ip=obtener_ip_cliente(request),
    )
