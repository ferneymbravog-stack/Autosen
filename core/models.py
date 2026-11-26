"""
Modelos de AutoSen (equivalen a las entidades JPA de com.example.sensores_vsc.model).

Tablas y columnas conservan los nombres de la base MySQL original (db_table y
db_column); PostgreSQL los cita, así que mayúsculas y la "ñ" de Tipo_daño se respetan.
Meta.ordering por clave primaria reproduce el orden en que MySQL devolvía los findAll().
"""
from django.db import models


class Usuario(models.Model):
    """Administrador del sistema (tabla usuario)."""

    id_usuario = models.AutoField(primary_key=True, db_column="Id_usuario")
    nombre = models.CharField(max_length=50, db_column="Nombre")
    correo = models.CharField(max_length=100, db_column="Correo")
    contrasena = models.CharField(max_length=100, db_column="Contrasena")
    # Texto libre (S2): en MySQL era enum('admin'), pero el panel crea ADMIN/SUPERADMIN/SOPORTE.
    rol = models.CharField(max_length=20, db_column="Rol")

    class Meta:
        db_table = "usuario"
        ordering = ["id_usuario"]

    def __str__(self):
        return self.correo


class Cliente(models.Model):
    """Propietario de vehículos que entra a la web y a la app (tabla cliente)."""

    id_cliente = models.AutoField(primary_key=True, db_column="Id_cliente")
    nombre_cliente = models.CharField(max_length=60, db_column="Nombre_cliente")
    apellido_cliente = models.CharField(max_length=60, db_column="Apellido_cliente")
    contrasena = models.CharField(max_length=100, db_column="Contrasena")
    correo = models.CharField(max_length=70, db_column="Correo")
    # Java no usa esta columna; se conserva por los datos importados. Al borrar el admin queda vacía.
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column="Id_usuario", related_name="clientes"
    )
    estado = models.CharField(max_length=10, null=True, blank=True, default="activo", db_column="Estado")
    telefono = models.CharField(max_length=25, null=True, blank=True, db_column="Telefono")

    class Meta:
        db_table = "cliente"
        ordering = ["id_cliente"]

    def __str__(self):
        return self.correo


class Vehiculo(models.Model):
    """Vehículo de un cliente (tabla vehiculo)."""

    id_vehiculo = models.AutoField(primary_key=True, db_column="Id_vehiculo")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, db_column="Id_cliente", related_name="vehiculos")
    nombre_vehiculo = models.CharField(max_length=60, db_column="Nombre_vehiculo")
    color = models.CharField(max_length=25, db_column="Color")
    marca = models.CharField(max_length=50, db_column="Marca")
    # Guarda "AAAA-01-01", como el proyecto Java.
    modelo = models.CharField(max_length=20, null=True, blank=True, db_column="Modelo")
    placa = models.CharField(max_length=10, null=True, blank=True, db_column="Placa")
    tipo_placa = models.CharField(max_length=60, db_column="Tipo_placa")
    # Dirección MAC del ELM327 Bluetooth asociado al vehículo (F6).
    elm_mac = models.CharField(max_length=50, null=True, blank=True, db_column="elm_mac")

    class Meta:
        db_table = "vehiculo"
        ordering = ["id_vehiculo"]

    def __str__(self):
        return f"{self.nombre_vehiculo} {self.placa}"


class Sensor(models.Model):
    """Sensor de un vehículo; nivel = porcentaje de desgaste 0–100 (tabla sensores)."""

    id_sensor = models.AutoField(primary_key=True, db_column="Id_sensor")
    nombre_sensor = models.CharField(max_length=200, db_column="Nombre_sensor")
    tipo_sensor = models.CharField(max_length=50, db_column="Tipo_sensor")
    # Admite NULL (F4): el panel permite dejarlo vacío.
    tipo_dano = models.CharField(max_length=90, null=True, blank=True, db_column="Tipo_daño")
    nivel = models.IntegerField(default=0, db_column="Nivel")
    estado = models.CharField(max_length=20, null=True, blank=True, db_column="Estado")
    # CASCADE equivale al CascadeType.ALL de Vehiculo.sensores en JPA.
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.CASCADE, null=True, blank=True, db_column="Id_vehiculo", related_name="sensores"
    )

    class Meta:
        db_table = "sensores"
        ordering = ["id_sensor"]

    def __str__(self):
        return self.nombre_sensor


class Lectura(models.Model):
    """Medición recibida del escáner OBD2 (tabla lecturas)."""

    id_lectura = models.AutoField(primary_key=True, db_column="Id_lectura")
    # SET_NULL conserva el historial cuando se elimina el vehículo (F3).
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, db_column="Id_vehiculo", related_name="lecturas"
    )
    placa_historica = models.CharField(max_length=10, null=True, blank=True)
    nombre_sensor = models.CharField(max_length=120, db_column="Nombre_sensor")
    tipo_sensor = models.CharField(max_length=50, db_column="Tipo_sensor")
    valor = models.FloatField(db_column="Valor")
    unidad = models.CharField(max_length=20, default="", db_column="Unidad")
    nivel = models.IntegerField(default=0, db_column="Nivel")
    estado = models.CharField(max_length=20, default="OK", db_column="Estado")
    fecha_lectura = models.DateTimeField(db_column="Fecha_lectura")

    class Meta:
        db_table = "lecturas"
        ordering = ["id_lectura"]

    def __str__(self):
        return f"{self.nombre_sensor} = {self.valor}"


class Alerta(models.Model):
    """Alerta generada por una lectura con nivel de advertencia o falla (tabla alertas)."""

    id_alerta = models.AutoField(primary_key=True, db_column="Id_alerta")
    # SET_NULL conserva el historial cuando se elimina el vehículo (F3).
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, db_column="Id_vehiculo", related_name="alertas"
    )
    placa_historica = models.CharField(max_length=10, null=True, blank=True)
    nombre_sensor = models.CharField(max_length=120, db_column="Nombre_sensor")
    tipo_sensor = models.CharField(max_length=50, db_column="Tipo_sensor")
    valor = models.FloatField(db_column="Valor")
    nivel = models.IntegerField(db_column="Nivel")
    tipo = models.CharField(max_length=20, db_column="Tipo")
    mensaje = models.CharField(max_length=255, db_column="Mensaje")
    leida = models.SmallIntegerField(null=True, blank=True, default=0, db_column="Leida")
    fecha_alerta = models.DateTimeField(db_column="Fecha_alerta")

    class Meta:
        db_table = "alertas"
        ordering = ["id_alerta"]

    def __str__(self):
        return self.mensaje


class RegistroAuditoria(models.Model):
    """Registro inmutable de auditoría para acciones de administradores y acceso al panel."""

    id_auditoria = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="registros_auditoria"
    )
    usuario_correo = models.CharField(max_length=100)
    usuario_rol = models.CharField(max_length=30)
    accion = models.CharField(max_length=30)  # CREAR, EDITAR, ELIMINAR, CALIBRAR, BLOQUEAR, ACTIVAR, LOGIN
    entidad = models.CharField(max_length=30)  # CLIENTE, VEHICULO, SENSOR, USUARIO, SISTEMA
    entidad_id = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField()
    ip = models.CharField(max_length=45, default="127.0.0.1")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "registro_auditoria"
        ordering = ["-fecha"]

    def __str__(self):
        return f"[{self.fecha:%Y-%m-%d %H:%M}] {self.usuario_correo} ({self.accion}): {self.descripcion}"


class NotificacionEnviada(models.Model):
    """Historial de notificaciones multicanal (Email, WhatsApp, Telegram, Navegador)."""

    id_notificacion = models.AutoField(primary_key=True)
    canal = models.CharField(max_length=20)  # EMAIL, WHATSAPP, TELEGRAM, NAVEGADOR
    destinatario = models.CharField(max_length=100)
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, default="ENVIADO")  # ENVIADO, FALLIDO, OMITIDO, EN_COLA
    detalle_error = models.TextField(null=True, blank=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    alerta = models.ForeignKey(Alerta, on_delete=models.SET_NULL, null=True, blank=True, related_name="notificaciones")

    class Meta:
        db_table = "notificaciones_enviadas"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"[{self.canal}] {self.destinatario}: {self.asunto}"
