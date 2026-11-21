# Manual de Usuario del Sistema — AutoSen

> **Issue asociado:**
> - `[DOC-10] Actualizar el Manual de Usuario (#10)`

---

## 1. Perfiles de Usuario en AutoSen

AutoSen cuenta con cuatro roles claramente diferenciados para garantizar la seguridad y operatividad:

```
+---------------------------------------------------------------------------------------+
|  ROL              |  ACCESO PRINCIPAL     |  RESPONSABILIDADES Y ALCANCE              |
+-------------------+-----------------------+-------------------------------------------+
|  1. CLIENTE       |  /dashboard           |  Monitoreo de sus vehículos y sensores.   |
|  2. SOPORTE       |  /admin (Filtro tec)  |  Diagnóstico en vivo, alertas y pruebas.  |
|  3. ADMIN         |  /admin               |  Gestión de clientes, flota y reportes.   |
|  4. SUPERADMIN    |  /admin (Super Panel) |  Control total: equipo técnico y auditoría|
+---------------------------------------------------------------------------------------+
```

---

## 2. Guía para el Cliente

### 2.1 Registro de Cuenta
1. Ingresa a `http://localhost:8080/register`.
2. Completa tu nombre, apellido, correo electrónico, **teléfono/WhatsApp** (ej: `+57 300 123 4567`) y contraseña.
3. Haz clic en **Registrarse**. La cuenta se creará inmediatamente y podrás iniciar sesión.

### 2.2 Dashboard y Monitoreo de Vehículos
* En `http://localhost:8080/dashboard` verás el resumen de tus sensores (Óptimos, Advertencias y Fallas).
* En `http://localhost:8080/vehiculos` puedes registrar nuevos autos o editar los existentes.
* Al conectar el escáner Bluetooth de tu auto con la app móvil, tus sensores se actualizarán en vivo.

---

## 3. Guía para el Personal Técnico (Soporte)

1. Inicia sesión con tus credenciales de soporte en `http://localhost:8080/admin/login`.
2. Tu pantalla principal es el **Centro de Diagnóstico Técnico**:
   * **Incidencias Activas:** Lista destacada de sensores con desgaste crítico (≥70%) o advertencia (40%-69%).
   * **Calibrar Sensor:** Haz clic en *Calibrar / Diagnosticar Sensor* para ingresar valores de prueba y verificar el comportamiento del vehículo.
   * **Alertas Sonoras y Web Push:** Haz clic en el botón superior **🔔 Activar Web Push** para recibir notificaciones emergentes con sonido ante cualquier falla en carretera.

---

## 4. Guía para Administradores

* **Gestión de Clientes:** En la tabla de clientes puedes dar de alta clientes, editar su información o presionar **Bloquear / Activar** para pausar temporalmente su servicio.
* **Gestión de Flota:** Visualiza toda la flota registrada, placas y el escáner MAC vinculado a cada vehículo.
* **Reportes:** En `http://localhost:8080/admin/reportes` puedes filtrar telemetría por fechas o cliente y descargar reportes oficiales en **PDF**, **Excel** o **CSV**.

---

## 5. Guía para SuperAdministradores

El rol `SUPERADMIN` dispone de dos módulos exclusivos:

1. **Gestión de Administradores (`/admin/usuario/nuevo`):**
   * Permite crear nuevos colaboradores asignándoles el rol adecuado (`Administrador`, `Super Administrador` o `Soporte Técnico`).
2. **Registro de Auditoría (`/admin/auditoria`):**
   * Consulta el registro cronológico inmutable de todas las operaciones realizadas en el sistema (quién creó, editó, bloqueó o eliminó cualquier registro, con fecha, hora e IP).
3. **Bandeja de Notificaciones (`/admin/notificaciones`):**
   * Supervisa los mensajes enviados por Email, Telegram, Web Push y WhatsApp (con botón directo para abrir el chat en WhatsApp Web).
