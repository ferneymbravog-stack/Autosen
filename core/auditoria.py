"""Módulo de auditoría para AutoSen."""
from core.models import RegistroAuditoria


def registrar_auditoria(request, accion: str, entidad: str, entidad_id, descripcion: str) -> RegistroAuditoria:
    """Registra una acción en la bitácora de auditoría del sistema."""
    usuario_correo = "Sistema"
    usuario_rol = "SISTEMA"

    admin = getattr(request, "admin", None)
    if admin:
        usuario_correo = getattr(admin, "correo", "admin@autosen.com")
        usuario_rol = getattr(admin, "rol", "ADMIN")
    else:
        cliente = getattr(request, "cliente", None)
        if cliente:
            usuario_correo = getattr(cliente, "correo", "cliente@autosen.com")
            usuario_rol = "CLIENTE"

    ip = "127.0.0.1"
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "127.0.0.1")

    return RegistroAuditoria.objects.create(
        usuario_correo=usuario_correo,
        usuario_rol=str(usuario_rol).upper(),
        accion=str(accion).upper(),
        entidad=str(entidad).upper(),
        entidad_id=str(entidad_id) if entidad_id is not None else "",
        descripcion=descripcion,
        ip=ip,
    )


def auditar_autenticacion(request, usuario_correo: str, rol: str, exito: bool) -> RegistroAuditoria:
    """Registra eventos de autenticación exitosa o intentos fallidos."""
    accion = "LOGIN_OK" if exito else "LOGIN_FALLIDO"
    descripcion = f"Inicio de sesión exitoso ({rol})" if exito else f"Intento fallido de autenticación ({rol})"
    ip = request.META.get("REMOTE_ADDR", "127.0.0.1") if request else "127.0.0.1"
    return RegistroAuditoria.objects.create(
        usuario_correo=usuario_correo,
        usuario_rol=rol.upper(),
        accion=accion,
        entidad="SESION",
        entidad_id="0",
        descripcion=descripcion,
        ip=ip,
    )

