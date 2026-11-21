"""Vistas del panel de administración (equivalen a AdminController)."""
from django.shortcuts import get_object_or_404, redirect, render

from core.auditoria import registrar_auditoria
from core.auth import (admin_requerido, cerrar_sesion_admin, cifrar_contrasena,
                       gestion_admin_requerido, iniciar_sesion_admin, superadmin_requerido,
                       verificar_contrasena)
from core.consultas import igual_mysql, placa_duplicada
from core.http import metodos, parametro
from core.models import Cliente, NotificacionEnviada, RegistroAuditoria, Sensor, Usuario, Vehiculo
from core.normalizacion import normalizar_modelo, normalizar_placa, normalizar_tipo_placa
from core.patrones.singleton import UmbralesReporte
from core.validaciones import validar_largos, validar_persona, validar_vehiculo

PLACA_DUPLICADA = "Ya existe un vehículo registrado con esa placa."


# ---------------------------------------------------------------------------
# Login (formLogin de la cadena de seguridad de /admin/**)
# ---------------------------------------------------------------------------
@metodos("GET", "POST")
def login(request):
    """Equivale a AdminController.loginPage + formLogin de Spring (AdminUserDetailsService)."""
    if request.method != "POST":
        return render(request, "admin/login.html")
    correo = request.POST.get("correo", "").strip()
    contrasena = request.POST.get("contrasena", "")
    usuario = igual_mysql(Usuario.objects.all(), "correo", correo).first()
    if usuario is None or not verificar_contrasena(contrasena, usuario.contrasena):
        return redirect("/admin/login?error")
    iniciar_sesion_admin(request, usuario)
    registrar_auditoria(request, "LOGIN", "SISTEMA", usuario.id_usuario,
                        f"Inicio de sesión exitoso como {usuario.rol} ({usuario.correo})")
    return redirect("/admin")


def logout(request):
    """Equivale al logout de Spring en /admin/logout."""
    cerrar_sesion_admin(request)
    return redirect("/admin/login")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def cargar_totales(contexto: dict) -> None:
    """Equivale a AdminController.cargarTotales."""
    sensores = list(Sensor.objects.all())
    umbrales = UmbralesReporte.INSTANCIA
    total_fallas = sum(1 for s in sensores if s.nivel is not None and umbrales.es_falla(s.nivel))
    total_advertencias = sum(1 for s in sensores if s.nivel is not None and umbrales.es_advertencia(s.nivel))
    usuarios = list(Usuario.objects.all())
    superadmins_count = sum(1 for u in usuarios if u.rol and "SUPER" in u.rol.upper())
    soporte_count = sum(1 for u in usuarios if u.rol and "SOPORTE" in u.rol.upper())
    admins_count = len(usuarios) - superadmins_count - soporte_count
    sensores_atencion = [s for s in sensores if s.nivel is not None and s.nivel >= 40]
    sensores_atencion.sort(key=lambda s: s.nivel or 0, reverse=True)
    contexto.update({
        "totalClientes": Cliente.objects.count(),
        "totalVehiculos": Vehiculo.objects.count(),
        "totalSensores": len(sensores),
        "totalUsuarios": len(usuarios),
        "superadminsCount": superadmins_count,
        "adminsCount": admins_count,
        "soporteCount": soporte_count,
        "totalFallas": total_fallas,
        "totalAdvertencias": total_advertencias,
        "sensoresOk": len(sensores) - total_fallas - total_advertencias,
        "sensoresAtencion": sensores_atencion,
        "totalAuditorias": RegistroAuditoria.objects.count(),
        "totalNotificaciones": NotificacionEnviada.objects.count(),
        "ultimasAuditorias": list(RegistroAuditoria.objects.all()[:6]),
        "ultimasNotificaciones": list(NotificacionEnviada.objects.all()[:6]),
    })


@admin_requerido
@metodos("GET")
def index(request):
    """Equivale a AdminController.index."""
    contexto = {
        "clientes": list(Cliente.objects.all()),
        "vehiculos": list(Vehiculo.objects.all()),
        "sensores": list(Sensor.objects.all()),
        "usuarios": list(Usuario.objects.all()),
    }
    cargar_totales(contexto)
    return render(request, "admin/dashboard.html", contexto)


@admin_requerido
@metodos("GET")
def nosotros(request):
    """Equivale a AdminController.nosotrosPage."""
    return render(request, "paginas/nosotros.html")


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------
def contrasena_nueva(contrasena: str | None) -> str | None:
    """Al editar, una contraseña vacía o solo con espacios conserva la actual."""
    return None if contrasena is None or contrasena.strip() == "" else contrasena


@gestion_admin_requerido
@metodos("POST")
def cliente_estado(request, id):
    """Equivale a AdminController.cambiarEstado."""
    cliente = get_object_or_404(Cliente, pk=id)
    cliente.estado = "bloqueado" if cliente.estado == "activo" else "activo"
    cliente.save()
    registrar_auditoria(request, "BLOQUEAR" if cliente.estado == "bloqueado" else "ACTIVAR", "CLIENTE", cliente.id_cliente,
                        f"Estado del cliente '{cliente.nombre_cliente} {cliente.apellido_cliente}' cambiado a {cliente.estado}")
    return redirect("/admin")


@admin_requerido
@metodos("GET")
def cliente_nuevo(request):
    """Equivale a AdminController.nuevoCliente."""
    return render(request, "admin/crear-cliente.html", {"error": ""})


@admin_requerido
@metodos("POST")
def cliente_crear(request):
    """Equivale a AdminController.crearCliente, con las validaciones comunes (lote A)."""
    nombre = parametro(request, "nombre").strip()
    apellido = parametro(request, "apellido").strip()
    correo = parametro(request, "correo").strip()
    telefono = parametro(request, "telefono", requerido=False)
    contrasena = parametro(request, "contrasena")
    error = validar_persona([nombre, apellido], correo, contrasena) or validar_largos(
        Cliente, {"nombre_cliente": nombre, "apellido_cliente": apellido, "correo": correo})
    if error is None and igual_mysql(Cliente.objects.all(), "correo", correo).exists():
        error = "Ya existe un cliente con ese correo."
    if error:
        return render(request, "admin/crear-cliente.html", {"error": error})
    c = Cliente.objects.create(
        nombre_cliente=nombre,
        apellido_cliente=apellido,
        correo=correo,
        telefono=telefono.strip() if telefono else "",
        contrasena=cifrar_contrasena(contrasena),
        estado="activo",
    )
    registrar_auditoria(request, "CREAR", "CLIENTE", c.id_cliente,
                        f"Cliente '{nombre} {apellido}' creado ({correo})")
    return redirect("/admin")


@gestion_admin_requerido
@metodos("POST")
def cliente_eliminar(request, id):
    """Equivale a AdminController.eliminarCliente: borra sus vehículos (y sensores) y luego al cliente (F3)."""
    cliente = Cliente.objects.filter(pk=id).first()
    nombre_c = f"{cliente.nombre_cliente} {cliente.apellido_cliente}" if cliente else f"ID {id}"
    for vehiculo in Vehiculo.objects.filter(cliente_id=id):
        vehiculo.delete()
    Cliente.objects.filter(pk=id).delete()
    registrar_auditoria(request, "ELIMINAR", "CLIENTE", id,
                        f"Cliente '{nombre_c}' y sus vehículos asociados fueron eliminados")
    return redirect("/admin")


@admin_requerido
@metodos("GET", "POST")
def cliente_editar(request, id):
    """Equivale a AdminController.showEditarCliente / editarCliente, con las validaciones comunes (lote A)."""
    if request.method != "POST":
        cliente = get_object_or_404(Cliente, pk=id)
        return render(request, "admin/editar-cliente.html", {"cliente": cliente, "error": ""})
    nombre = parametro(request, "nombre").strip()
    apellido = parametro(request, "apellido").strip()
    correo = parametro(request, "correo").strip()
    telefono = parametro(request, "telefono", requerido=False)
    contrasena = contrasena_nueva(parametro(request, "contrasena", requerido=False))
    cliente = get_object_or_404(Cliente, pk=id)
    error = validar_persona([nombre, apellido], correo, contrasena, contrasena_obligatoria=False) or validar_largos(
        Cliente, {"nombre_cliente": nombre, "apellido_cliente": apellido, "correo": correo})
    if error is None and igual_mysql(Cliente.objects.exclude(pk=cliente.pk), "correo", correo).exists():
        error = "Ya existe un cliente con ese correo."
    if error:
        return render(request, "admin/editar-cliente.html", {"cliente": cliente, "error": error})

    cliente.nombre_cliente = nombre
    cliente.apellido_cliente = apellido
    cliente.correo = correo
    cliente.telefono = telefono.strip() if telefono else ""
    if contrasena is not None:
        cliente.contrasena = cifrar_contrasena(contrasena)
    cliente.save()
    registrar_auditoria(request, "EDITAR", "CLIENTE", cliente.id_cliente,
                        f"Datos del cliente '{nombre} {apellido}' actualizados")
    return redirect("/admin")


# ---------------------------------------------------------------------------
# Vehículos
# ---------------------------------------------------------------------------
def opcional(texto: str | None) -> str | None:
    """"campo == null || campo.isBlank() ? null : campo.trim()" de Java."""
    return None if texto is None or texto.strip() == "" else texto.strip()


@gestion_admin_requerido
@metodos("POST")
def vehiculo_eliminar(request, id):
    """Equivale a AdminController.eliminarVehiculo: sensores en cascada, lecturas conservadas (F3)."""
    v = Vehiculo.objects.filter(pk=id).first()
    info_v = f"{v.nombre_vehiculo} ({v.placa})" if v else f"ID {id}"
    Vehiculo.objects.filter(pk=id).delete()
    registrar_auditoria(request, "ELIMINAR", "VEHICULO", id,
                        f"Vehículo '{info_v}' y sus sensores asociados fueron eliminados")
    return redirect("/admin")


@admin_requerido
@metodos("GET")
def vehiculo_nuevo(request):
    """Equivale a AdminController.nuevoVehiculo."""
    return render(request, "admin/crear-vehiculo.html", {"clientes": list(Cliente.objects.all()), "error": ""})


@admin_requerido
@metodos("POST")
def vehiculo_crear(request):
    """Equivale a AdminController.crearVehiculo, con las validaciones comunes (lote A).
    Desde el panel no se crean sensores por defecto."""
    cliente_id = parametro(request, "clienteId", int)
    nombre_vehiculo = parametro(request, "nombreVehiculo").strip()
    marca = parametro(request, "marca").strip()
    modelo = (parametro(request, "modelo", requerido=False) or "").strip()
    color = parametro(request, "color").strip()
    placa = normalizar_placa(parametro(request, "placa"))
    tipo_placa = parametro(request, "tipoPlaca")
    elm_mac = parametro(request, "elmMac", requerido=False)

    error = validar_vehiculo(nombre_vehiculo, marca, modelo, color, placa, tipo_placa) or validar_largos(
        Vehiculo, {"nombre_vehiculo": nombre_vehiculo, "marca": marca, "color": color, "elm_mac": opcional(elm_mac)})
    if error is None and placa_duplicada(placa):
        error = PLACA_DUPLICADA
    cliente = Cliente.objects.filter(pk=cliente_id).first()
    if error is None and cliente is None:
        error = "Selecciona un cliente válido."
    if error:
        return render(request, "admin/crear-vehiculo.html", {"clientes": list(Cliente.objects.all()), "error": error})
    v = Vehiculo.objects.create(
        cliente=cliente,
        nombre_vehiculo=nombre_vehiculo,
        marca=marca,
        modelo=normalizar_modelo(modelo),
        color=color,
        placa=placa,
        tipo_placa=normalizar_tipo_placa(tipo_placa),
        elm_mac=opcional(elm_mac),
    )
    registrar_auditoria(request, "CREAR", "VEHICULO", v.id_vehiculo,
                        f"Vehículo '{nombre_vehiculo}' placa {placa} asignado a cliente '{cliente.nombre_cliente}'")
    return redirect("/admin")


@admin_requerido
@metodos("GET", "POST")
def vehiculo_editar(request, id):
    """Equivale a AdminController.showEditarVehiculo / editarVehiculo, con las validaciones comunes (lote A).
    Un modelo vacío conserva el actual."""
    if request.method != "POST":
        vehiculo = get_object_or_404(Vehiculo, pk=id)
        return render(request, "admin/editar-vehiculo.html",
                      {"vehiculo": vehiculo, "clientes": list(Cliente.objects.all()), "error": ""})
    cliente_id = parametro(request, "clienteId", int, requerido=False)
    nombre_vehiculo = parametro(request, "nombreVehiculo").strip()
    marca = parametro(request, "marca").strip()
    modelo = opcional(parametro(request, "modelo", requerido=False))
    color = parametro(request, "color").strip()
    placa = normalizar_placa(parametro(request, "placa"))
    tipo_placa = parametro(request, "tipoPlaca")
    elm_mac = parametro(request, "elmMac", requerido=False)
    vehiculo = get_object_or_404(Vehiculo, pk=id)

    error = validar_vehiculo(nombre_vehiculo, marca, modelo, color, placa, tipo_placa,
                             modelo_obligatorio=False) or validar_largos(
        Vehiculo, {"nombre_vehiculo": nombre_vehiculo, "marca": marca, "color": color, "elm_mac": opcional(elm_mac)})
    if error is None and placa_duplicada(placa, vehiculo):
        error = PLACA_DUPLICADA
    if error:
        return render(request, "admin/editar-vehiculo.html",
                      {"vehiculo": vehiculo, "clientes": list(Cliente.objects.all()), "error": error})

    vehiculo.nombre_vehiculo = nombre_vehiculo
    vehiculo.marca = marca
    if modelo is not None:
        vehiculo.modelo = normalizar_modelo(modelo)
    vehiculo.color = color
    vehiculo.placa = placa
    vehiculo.tipo_placa = normalizar_tipo_placa(tipo_placa)
    vehiculo.elm_mac = opcional(elm_mac)
    if cliente_id is not None and vehiculo.cliente_id != cliente_id:
        nuevo_cliente = Cliente.objects.filter(pk=cliente_id).first()
        if nuevo_cliente is not None:
            vehiculo.cliente = nuevo_cliente
    vehiculo.save()
    registrar_auditoria(request, "EDITAR", "VEHICULO", vehiculo.id_vehiculo,
                        f"Vehículo '{nombre_vehiculo}' placa {placa} modificado")
    return redirect("/admin")


# ---------------------------------------------------------------------------
# Sensores
# ---------------------------------------------------------------------------
def estado_desde_nivel(nivel: int) -> str:
    """Equivale a AdminController.estadoDesdeNivel."""
    if nivel >= 70:
        return "FALLA"
    if nivel >= 40:
        return "ADVERTENCIA"
    return "OK"


@admin_requerido
@metodos("POST")
def sensor_eliminar(request, id):
    """Equivale a AdminController.eliminarSensor."""
    s = Sensor.objects.filter(pk=id).first()
    info_s = s.nombre_sensor if s else f"ID {id}"
    Sensor.objects.filter(pk=id).delete()
    registrar_auditoria(request, "ELIMINAR", "SENSOR", id,
                        f"Sensor '{info_s}' eliminado")
    return redirect("/admin")


@admin_requerido
@metodos("GET")
def sensor_nuevo(request):
    """Equivale a AdminController.nuevoSensor."""
    return render(request, "admin/crear-sensor.html", {"vehiculos": list(Vehiculo.objects.all()), "error": ""})


def _validar_sensor(nombre_sensor, tipo_sensor, nivel, vehiculo_id, tipo_dano):
    """Validaciones comunes de crearSensor/editarSensor: devuelve (mensaje de error, vehículo)."""
    if nombre_sensor.strip() == "" or tipo_sensor.strip() == "" or nivel is None:
        return "Todos los campos obligatorios deben estar completos.", None
    if nivel < 0 or nivel > 100:
        return "El nivel debe estar entre 0 y 100.", None
    largo = validar_largos(Sensor, {"nombre_sensor": nombre_sensor.strip(), "tipo_sensor": tipo_sensor.strip(),
                                    "tipo_dano": opcional(tipo_dano)})
    if largo:
        return largo, None
    vehiculo = Vehiculo.objects.filter(pk=vehiculo_id).first()
    if vehiculo is None:
        return "Selecciona un vehículo válido.", None
    return None, vehiculo


@admin_requerido
@metodos("POST")
def sensor_crear(request):
    """Equivale a AdminController.crearSensor (tipo de daño opcional, F4)."""
    vehiculo_id = parametro(request, "vehiculoId", int)
    nombre_sensor = parametro(request, "nombreSensor")
    tipo_sensor = parametro(request, "tipoSensor")
    nivel = parametro(request, "nivel", int)
    tipo_dano = parametro(request, "tipoDano", requerido=False)
    mensaje, vehiculo = _validar_sensor(nombre_sensor, tipo_sensor, nivel, vehiculo_id, tipo_dano)
    if mensaje:
        return render(request, "admin/crear-sensor.html", {"vehiculos": list(Vehiculo.objects.all()), "error": mensaje})
    s = Sensor.objects.create(
        vehiculo=vehiculo,
        nombre_sensor=nombre_sensor.strip(),
        tipo_sensor=tipo_sensor.strip(),
        nivel=nivel,
        tipo_dano=opcional(tipo_dano),
        estado=estado_desde_nivel(nivel),
    )
    registrar_auditoria(request, "CREAR", "SENSOR", s.id_sensor,
                        f"Sensor '{s.nombre_sensor}' creado para {vehiculo.nombre_vehiculo} ({vehiculo.placa})")
    return redirect("/admin")


@admin_requerido
@metodos("GET", "POST")
def sensor_editar(request, id):
    """Equivale a AdminController.showEditarSensor / editarSensor."""
    if request.method != "POST":
        sensor = get_object_or_404(Sensor, pk=id)
        return render(request, "admin/editar-sensor.html",
                      {"vehiculos": list(Vehiculo.objects.all()), "sensor": sensor, "error": ""})
    vehiculo_id = parametro(request, "vehiculoId", int)
    nombre_sensor = parametro(request, "nombreSensor")
    tipo_sensor = parametro(request, "tipoSensor")
    nivel = parametro(request, "nivel", int)
    tipo_dano = parametro(request, "tipoDano", requerido=False)
    sensor = get_object_or_404(Sensor, pk=id)
    mensaje, vehiculo = _validar_sensor(nombre_sensor, tipo_sensor, nivel, vehiculo_id, tipo_dano)
    if mensaje:
        return render(request, "admin/editar-sensor.html",
                      {"vehiculos": list(Vehiculo.objects.all()), "sensor": sensor, "error": mensaje})
    nivel_previo = sensor.nivel
    sensor.vehiculo = vehiculo
    sensor.nombre_sensor = nombre_sensor.strip()
    sensor.tipo_sensor = tipo_sensor.strip()
    sensor.nivel = nivel
    sensor.tipo_dano = opcional(tipo_dano)
    sensor.estado = estado_desde_nivel(nivel)
    sensor.save()
    if nivel >= 40:
        from api.obd2 import crear_alerta_si_corresponde
        crear_alerta_si_corresponde(
            vehiculo.id_vehiculo, sensor.nombre_sensor, sensor.tipo_sensor,
            valor=float(nivel), nivel=nivel, sufijo_unidad="%"
        )
    accion = "CALIBRAR" if nivel != nivel_previo else "EDITAR"
    registrar_auditoria(request, accion, "SENSOR", sensor.id_sensor,
                        f"Sensor '{sensor.nombre_sensor}' de {vehiculo.nombre_vehiculo} ({vehiculo.placa}) calibrado a {nivel}% ({sensor.estado})")
    return redirect("/admin")


# ---------------------------------------------------------------------------
# Usuarios administradores
# ---------------------------------------------------------------------------
@superadmin_requerido
@metodos("GET")
def usuario_nuevo(request):
    """Equivale a AdminController.nuevoUsuario."""
    return render(request, "admin/crear-usuario.html", {"error": ""})


@superadmin_requerido
@metodos("POST")
def usuario_crear(request):
    """Equivale a AdminController.crearUsuario (el rol es texto libre, S2), con las validaciones comunes (lote A)."""
    nombre = parametro(request, "nombre").strip()
    correo = parametro(request, "correo").strip()
    contrasena = parametro(request, "contrasena")
    rol = parametro(request, "rol")
    error = validar_persona([nombre], correo, contrasena) or validar_largos(
        Usuario, {"nombre": nombre, "correo": correo, "rol": rol.strip()})
    if error is None and igual_mysql(Usuario.objects.all(), "correo", correo).exists():
        error = "Ya existe un usuario con ese correo."
    if error:
        return render(request, "admin/crear-usuario.html", {"error": error})
    u = Usuario.objects.create(
        nombre=nombre,
        correo=correo,
        contrasena=cifrar_contrasena(contrasena),
        rol="ADMIN" if rol.strip() == "" else rol.strip(),
    )
    registrar_auditoria(request, "CREAR", "USUARIO", u.id_usuario,
                        f"Administrador '{nombre}' creado con rol {u.rol} ({correo})")
    return redirect("/admin")


@superadmin_requerido
@metodos("GET", "POST")
def usuario_editar(request, id):
    """Equivale a AdminController.showEditarUsuario / editarUsuario, con las validaciones comunes (lote A)."""
    if request.method != "POST":
        usuario = get_object_or_404(Usuario, pk=id)
        return render(request, "admin/editar-usuario.html", {"usuario": usuario, "error": ""})
    nombre = parametro(request, "nombre").strip()
    correo = parametro(request, "correo").strip()
    contrasena = contrasena_nueva(parametro(request, "contrasena", requerido=False))
    rol = parametro(request, "rol")
    usuario = get_object_or_404(Usuario, pk=id)
    error = validar_persona([nombre], correo, contrasena, contrasena_obligatoria=False) or validar_largos(
        Usuario, {"nombre": nombre, "correo": correo, "rol": rol.strip()})
    if error is None and igual_mysql(Usuario.objects.exclude(pk=usuario.pk), "correo", correo).exists():
        error = "Ya existe un usuario con ese correo."
    if error:
        return render(request, "admin/editar-usuario.html", {"usuario": usuario, "error": error})

    usuario.nombre = nombre
    usuario.correo = correo
    if contrasena is not None:
        usuario.contrasena = cifrar_contrasena(contrasena)
    usuario.rol = usuario.rol if rol.strip() == "" else rol.strip()
    usuario.save()
    registrar_auditoria(request, "EDITAR", "USUARIO", usuario.id_usuario,
                        f"Administrador '{nombre}' modificado (rol: {usuario.rol})")
    return redirect("/admin")


@superadmin_requerido
@metodos("POST")
def usuario_eliminar(request, id):
    """Equivale a AdminController.eliminarUsuario: no se borra a sí mismo ni al último administrador."""
    total_usuarios = Usuario.objects.count()
    usuario = get_object_or_404(Usuario, pk=id)
    if request.admin_correo.lower() == usuario.correo.lower() or total_usuarios <= 1:
        return redirect("/admin")
    nombre_u = usuario.nombre
    usuario.delete()
    registrar_auditoria(request, "ELIMINAR", "USUARIO", id,
                        f"Administrador '{nombre_u}' eliminado del sistema")
    return redirect("/admin")


# ---------------------------------------------------------------------------
# Auditoría y Notificaciones
# ---------------------------------------------------------------------------
@superadmin_requerido
@metodos("GET")
def auditoria_lista(request):
    """Muestra la bitácora completa de auditoría del sistema."""
    accion_filtro = request.GET.get("accion", "").strip().upper()
    entidad_filtro = request.GET.get("entidad", "").strip().upper()

    registros = RegistroAuditoria.objects.all()
    if accion_filtro:
        registros = registros.filter(accion=accion_filtro)
    if entidad_filtro:
        registros = registros.filter(entidad=entidad_filtro)

    contexto = {
        "registros": list(registros[:200]),
        "total": registros.count(),
        "accion_filtro": accion_filtro,
        "entidad_filtro": entidad_filtro,
        "acciones": ["CREAR", "EDITAR", "ELIMINAR", "CALIBRAR", "BLOQUEAR", "ACTIVAR", "LOGIN", "TEST"],
        "entidades": ["CLIENTE", "VEHICULO", "SENSOR", "USUARIO", "SISTEMA", "ALERTA"],
    }
    return render(request, "admin/auditoria.html", contexto)


@admin_requerido
@metodos("GET")
def notificaciones_lista(request):
    """Muestra el historial de notificaciones multicanal despachadas."""
    canal_filtro = request.GET.get("canal", "").strip().upper()
    notificaciones = NotificacionEnviada.objects.all()
    if canal_filtro:
        notificaciones = notificaciones.filter(canal=canal_filtro)

    contexto = {
        "notificaciones": list(notificaciones[:200]),
        "total": notificaciones.count(),
        "canal_filtro": canal_filtro,
        "canales": ["EMAIL", "WHATSAPP", "TELEGRAM", "WEB_PUSH"],
    }
    return render(request, "admin/notificaciones.html", contexto)


@admin_requerido
@metodos("POST")
def simular_alerta(request):
    """Crea una alerta de prueba en caliente para verificar el despacho multicanal y Web Push."""
    from api.obd2 import crear_alerta_si_corresponde
    v = Vehiculo.objects.first()
    if not v:
        c = Cliente.objects.first()
        if not c:
            c = Cliente.objects.create(
                nombre_cliente="Prueba", apellido_cliente="AutoSen",
                correo="cliente@autosen.com", contrasena=cifrar_contrasena("cliente123"), estado="activo"
            )
        v = Vehiculo.objects.create(
            cliente=c, nombre_vehiculo="Vehículo de Prueba", marca="Chevrolet",
            modelo="2022-01-01", placa="TEST-999", color="Negro", tipo_placa="particular"
        )

    sensor = Sensor.objects.filter(vehiculo=v).first()
    sensor_nombre = sensor.nombre_sensor if sensor else "Sensor ECT (Temperatura)"
    sensor_tipo = sensor.tipo_sensor if sensor else "ECT"

    alerta = crear_alerta_si_corresponde(
        id_vehiculo=v.id_vehiculo,
        nombre_sensor=sensor_nombre,
        tipo_sensor=sensor_tipo,
        valor=98.0,
        nivel=85,
        sufijo_unidad=" °C"
    )
    registrar_auditoria(
        request, "TEST", "ALERTA", alerta.id_alerta if alerta else 0,
        f"Simulación de alerta crítica ejecutada para {v.nombre_vehiculo} ({v.placa}) - Notificaciones multicanal enviadas"
    )
    return redirect("/admin?alerta_simulada=1")
