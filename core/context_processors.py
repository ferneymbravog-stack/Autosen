from core.auth import admin_actual, rol_usuario


def admin_correo(request):
    """Datos y rol del administrador en sesión."""
    usuario = getattr(request, "admin", None)
    if usuario is None:
        usuario = admin_actual(request)
    correo = usuario.correo if usuario else ""
    nombre = usuario.nombre if usuario else ""
    rol = rol_usuario(usuario) if usuario else ""
    return {
        "admin_correo": correo,
        "admin_nombre": nombre,
        "admin_rol": rol,
        "admin_usuario": usuario,
        "es_superadmin": rol == "SUPERADMIN",
        "es_admin": rol == "ADMIN",
        "es_soporte": rol == "SOPORTE",
    }
