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
2. Completa tu nombre, apellido, correo electrónico, **teléfono/WhatsApp** (ej: `3001234567` o `+57 300 123 4567`) y contraseña.
3. Haz clic en **Registrarse**. Recibirás alertas automáticas en ese correo y número de WhatsApp cuando alguno de tus vehículos presente fallas o advertencias.

### 2.2 Dashboard, Bluetooth y Cómo Activar las Notificaciones del Navegador
1. Ingresa a `http://localhost:8080/dashboard` para ver el resumen de tus sensores (Óptimos, Advertencias y Fallas) y conectar la simulación Bluetooth (`◉ CONECTAR BLUETOOTH`).
2. En la esquina superior derecha haz clic en **🔔 Activar notificaciones** y acepta el permiso del navegador.
   * Cuando ocurra una advertencia o falla crítica en **tus vehículos** (nunca recibirás alertas de vehículos de otros clientes), aparecerá una notificación nativa como `AutoSen: FALLA CRÍTICA — Placa ABC123 - Sensor O2 85%`.
   * Al hacer clic sobre la notificación, el navegador enfocará automáticamente tu pestaña de AutoSen.
   * Si tu navegador no soporta la API `Notification` o bloqueaste el permiso anteriormente, verás un aviso discreto debajo del encabezado indicando cómo volver a habilitarlo desde el ícono de permisos junto a la URL.

---

## 3. Guía para el Personal Técnico (Soporte)

1. Inicia sesión con tus credenciales de soporte en `http://localhost:8080/admin/login`.
2. En tu **Centro de Diagnóstico Técnico**:
   * **Incidencias Activas:** Lista destacada de sensores con desgaste crítico (≥70%) o advertencia (40%-69%).
   * **Calibrar Sensor:** Haz clic en *Calibrar / Diagnosticar Sensor* para ajustar niveles de sensores y disparar diagnósticos preventivos.
   * **Notificaciones del Navegador:** Presiona **🔔 Activar notificaciones** en la barra superior para recibir avisos sonoros, tarjetas emergentes (*toasts*) y notificaciones nativas de escritorio de toda la flota monitoreada.

---

## 4. Guía de la Bandeja de Notificaciones (`/admin/notificaciones`)

Disponible para `SUPERADMIN`, `ADMIN` y `SOPORTE`:

### 4.1 Consultar el Estado de las Notificaciones
1. En el menú superior del panel entra a **Notificaciones**.
2. Usa los selectores **Canal** (`EMAIL`, `WHATSAPP`, `TELEGRAM`, `NAVEGADOR`) y **Estado** para filtrar el historial:
   * 🟢 **`ENVIADO`** *(verde)*: entregado y confirmado por la API externa o mostrado en el navegador.
   * 🔴 **`FALLIDO`** *(rojo)*: ocurrió un error de red, credenciales o validación (debajo de la insignia verás el motivo exacto en `detalle_error`, como la regla de 24 horas de WhatsApp o un teléfono inválido).
   * ⚪ **`OMITIDO`** *(gris)*: el canal no está configurado en `.env` o el cliente no tiene correo/teléfono registrado.
   * 🔵 **`EN_COLA`** *(azul)*: alerta pendiente de mostrarse en el navegador activo.

### 4.2 Usar "Probar canales" y "Reintentar"
* **Sección "🔌 Probar canales":**
  * **🤖 Probar Telegram:** envía `✅ Prueba de conexión AutoSen` con fecha y hora al chat/grupo configurado.
  * **📧 Probar Email:** envía un correo de verificación a la dirección del administrador actualmente en sesión.
  * **💬 Probar WhatsApp:** escribe un número de celular válido (ej. `3001234567`) y haz clic en *Probar WhatsApp*.
  * Tras cada prueba aparece un mensaje flash verde o rojo en la parte superior indicando el resultado exacto, y la acción queda registrada en la auditoría.
* **Botón "↻ Reintentar":**
  * En cualquier fila de Telegram, Email o WhatsApp que tenga estado **`FALLIDO`**, haz clic en el botón **↻ Reintentar** para volver a despachar el mensaje una vez corregido el problema (por ejemplo, tras renovar el token de Meta o luego de que el cliente escriba al número de prueba).
  * Para los registros de WhatsApp también se conserva como respaldo manual el enlace **Abrir chat WhatsApp →**.

---

## 5. Guía para Administradores y SuperAdministradores

* **Gestión de Clientes y Flota (`/admin`):** creación y edición de clientes/vehículos, y botón **Bloquear / Activar** para suspender o reactivar cuentas (`ADMIN` y `SUPERADMIN`).
* **Reportes (`/admin/reportes`):** filtrado por fechas o cliente y descarga en **PDF**, **Excel** o **CSV**.
* **Gestión de Administradores (`/admin/usuario/nuevo`) y Auditoría (`/admin/auditoria`):** exclusivos para `SUPERADMIN`, permitiendo auditar altas, bajas, inicios de sesión, pruebas de canales y reintentos de notificaciones con fecha, usuario e IP.
