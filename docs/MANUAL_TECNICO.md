# Manual Técnico de la Aplicación — AutoSen (Django)

> **Issue asociado:**
> - `[DOC-09] Reescribir el Manual Técnico para Django (#9)`

---

## 1. Stack Tecnológico
* **Lenguaje:** Python 3.12+ (compatible con Python 3.14 / 3.15)
* **Framework Web:** Django 6.1+
* **Base de Datos:** PostgreSQL 18
* **Conector:** `psycopg[binary] >= 3.2.0`
* **Seguridad de Claves:** `bcrypt >= 4.2.0`
* **Integración HTTP Externa:** `urllib.request` de la librería estándar de Python (timeout estricto de 5 s) + `EmailMultiAlternatives` (SMTP TLS)
* **Exportación de Documentos:** `reportlab >= 4.2.0` (PDFs vectoriales) y `openpyxl >= 3.1.5` (Excel)
* **Protocolo de Comunicación:** OBD-II (SAE J1979 / ISO 15765-4 CAN) vía Bluetooth SPP

---

## 2. Variables de Entorno (`.env`)

Todas las credenciales viven exclusivamente en `.env` (excluido en `.gitignore`):

```ini
SECRET_KEY=clave_secreta_django_larga_y_segura
DEBUG=True

# Conexión a Base de Datos PostgreSQL
DB_NAME=vehiculos
DB_USER=postgres
DB_PASSWORD=tu_clave_postgres
DB_HOST=127.0.0.1
DB_PORT=5432
ALLOWED_HOSTS_EXTRA=

# Telegram Bot API
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Gmail SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
EMAIL_TIMEOUT=10
SITE_URL=http://localhost:8080

# WhatsApp Cloud API de Meta (usar la versión mostrada en el panel de Meta, p. ej. v21.0)
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_API_VERSION=

# Despacho en segundo plano (True en ejecución normal; en manage.py test fuerza False)
NOTIFICACIONES_ASINCRONAS=True
```

---

## 3. Estructura de Módulos Django

```
autosen/
├── autosen/                 # Configuración global del proyecto (settings, urls, wsgi)
├── core/                    # Modelos de BD, patrones GoF, auditoría, normalización y middleware
│   ├── patrones/            # Implementación GoF: Strategy, Observer, Factory, Singleton
│   ├── management/commands/ # Comandos CLI: importar_mysql y probar_canales
│   ├── servicios_externos.py# Clientes reales para Telegram Bot API, Gmail SMTP y WhatsApp Cloud API
│   └── notificaciones.py    # Orquestador multicanal, plantillas de mensajes, reintentos e hilos
├── web/                     # Portal de usuario / cliente (vistas, URLs, plantillas)
├── panel/                   # Panel administrativo (roles SuperAdmin/Admin/Soporte, pruebas y reintentos)
├── api/                     # Endpoints JSON para telemetría OBD2, alertas en vivo y app Android
├── reportes/                # Generador de reportes con filtros y exportación PDF/Excel/CSV
├── templates/               # Plantillas HTML5 responsivas y plantilla de correo (templates/emails/alerta.html)
└── static/                  # Archivos estáticos (CSS, JS, modo claro/oscuro)
```

---

## 4. Integración con Servicios Externos (`core/servicios_externos.py`)

El módulo `core/servicios_externos.py` centraliza todas las salidas hacia APIs externas cumpliendo las siguientes garantías:
* Cada función devuelve `tuple[bool, str] = (exito, detalle)` y **jamás propaga excepciones** hacia el flujo principal.
* Todas las operaciones se registran mediante el logger `autosen.externos`, sanitizando cualquier token o contraseña con `_ocultar_secretos()` para que nunca aparezcan en logs, base de datos ni mensajes de error.
* Las peticiones HTTP usan `urllib.request.urlopen(..., timeout=5)` sin añadir dependencias externas.
* En `NotificacionEnviada` se persiste el estado real (`ENVIADO`, `FALLIDO`, `OMITIDO` o `EN_COLA`) junto con `detalle_error`.

### 4.1 Telegram Bot API (`enviar_telegram`)
* **Endpoint consumido:** `POST https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage`
* **Petición (`application/json`):**
  ```json
  {
    "chat_id": "-100123456789",
    "text": "🤖 <b>AutoSen Telemetría Bot</b>...",
    "parse_mode": "HTML",
    "disable_web_page_preview": true
  }
  ```
  El texto se escapa con `html.escape` en todos los campos dinámicos y se recorta a un máximo de 4000 caracteres.
* **Respuesta esperada:** HTTP 200 con `{"ok": true, "result": {...}}`.
* **Manejo de errores:** Captura `HTTPError` (extrayendo `"description"` del JSON de error de Telegram), `URLError`, `TimeoutError` y JSON inválido. Si faltan variables en `.env`, retorna `(False, "Telegram no configurado")` y se registra como `OMITIDO`.

### 4.2 Gmail SMTP (`enviar_email`)
* **Servidor:** `smtp.gmail.com:587` con `STARTTLS` (`EMAIL_USE_TLS=True`, `EMAIL_TIMEOUT=10`). Si `EMAIL_HOST_USER` o `EMAIL_HOST_PASSWORD` están vacíos, `settings.py` activa el backend de consola y el despacho registra `OMITIDO` (`"Email no configurado"`).
* **Formato:** `EmailMultiAlternatives` con cuerpo en texto plano y alternativa `text/html` generada con `templates/emails/alerta.html` (encabezado rojo `#dc2626` para falla, naranja `#ea580c` para advertencia, tabla de telemetría y enlace al dashboard, protegidos por el autoescape de Django).
* **Manejo de errores:** Captura `smtplib.SMTPException`, `socket.timeout` y `OSError`. Si el cliente no tiene correo, se registra como `OMITIDO`.

### 4.3 WhatsApp Cloud API de Meta (`enviar_whatsapp`)
* **Endpoint consumido:** `POST https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages`
* **Encabezados:** `Authorization: Bearer <WHATSAPP_TOKEN>`, `Content-Type: application/json`
* **Petición (`application/json`):**
  ```json
  {
    "messaging_product": "whatsapp",
    "to": "573001234567",
    "type": "text",
    "text": {"preview_url": false, "body": "🚨 *AutoSen OBD2 Alerta*..."}
  }
  ```
  Antes de enviar, `normalizar_telefono_whatsapp` (`core/normalizacion.py`) limpia espacios, guiones y `+`, y antepone `57` a celulares colombianos de 10 dígitos iniciados en `3`. Si el teléfono no es válido, guarda `FALLIDO` con `"Teléfono inválido"`.
* **Respuesta esperada:** HTTP 200 con lista `"messages": [{"id": "wamid..."}]`.
* **Manejo de errores:** Extrae `error.code` y `error.message` de Meta y traduce al español los errores habituales:
  * `131047`: ventana de atención de 24 horas cerrada (el destinatario debe escribir primero al número de prueba).
  * `131030`: destinatario no incluido en la lista de números verificados de prueba en Meta.
  * `HTTP 401` / código `190`: token inválido o vencido.

### 4.4 Envío en Segundo Plano y Canal Navegador
* Cuando se registra una alerta en `crear_alerta_si_corresponde`, la señal GoF `alerta_critica` invoca `despachar_en_segundo_plano(alerta)` (cuando `NOTIFICACIONES_ASINCRONAS=True`).
* Mediante `transaction.on_commit`, una vez confirmada la alerta en PostgreSQL se lanza un `threading.Thread(daemon=True)` que ejecuta el envío por los canales externos sin bloquear la respuesta HTTP hacia la app Android ni hacia el dashboard web, cerrando siempre la conexión del hilo con `django.db.connection.close()`. En las pruebas automatizadas (`manage.py test`), `NOTIFICACIONES_ASINCRONAS` es `False` y las credenciales externas quedan vacías por defecto para garantizar determinismo y cero llamadas reales.
* El canal `NAVEGADOR` se registra inicialmente en estado `EN_COLA`; cuando el dashboard muestra la notificación nativa (`new Notification(...)`), confirma su visualización en `POST /api/alertas/<id>/mostrada`, pasando el registro a `ENVIADO`.

---

## 5. Integridad Referencial e Historial de Auditoría (`core/auditoria.py`)

* **Trazabilidad histórica en `Lectura` y `Alerta`:** ambas tablas referencian `vehiculo("Id_vehiculo")` mediante `ForeignKey(..., on_delete=models.SET_NULL)` y almacenan `placa_historica`. Al eliminar un vehículo, su historial de telemetría y alertas permanece intacto con `vehiculo = NULL` y sin romper el contrato JSON de `/api/**` consumido por la app Android.
* **Auditoría administrativa inmutable (`RegistroAuditoria`):**
  * Enlaza cada acción con `Usuario` (`on_delete=models.SET_NULL`) y conserva además la instantánea `usuario_correo` y `usuario_rol`.
  * Registra inicios de sesión exitosos (`LOGIN`) con el administrador real, cierres de sesión (`LOGOUT`) e intentos fallidos (`LOGIN_FALLIDO`) tanto de correos existentes como inexistentes, capturando la IP (`X-Forwarded-For` / `REMOTE_ADDR`) y **sin almacenar jamás la contraseña intentada**.
  * La vista `/admin/auditoria` utiliza `select_related("usuario")` y ofrece filtros por administrador, acción, entidad y rango de fechas.

---

## 6. Endpoints Principales de la API (`/api/`)

| Método | Ruta | Autenticación / Seguridad | Descripción |
| :---: | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Pública (App Android) | Registra una nueva cuenta de cliente. |
| `POST` | `/api/auth/login` | Pública (App Android) | Autentica a un cliente desde la app móvil. |
| `GET` | `/api/cliente/<correo>` | Pública (App Android) | Retorna vehículos, sensores y estadísticas del cliente. |
| `POST` | `/api/vehiculos/crear` | Pública (App Android) | Registra un vehículo y crea sus sensores por defecto. |
| `POST` | `/api/obd2/lecturas` | Pública (App Android) | Recibe lecturas ELM327, calcula desgaste y dispara alertas. |
| `POST` | `/api/obd2/conectar` | Sesión de cliente | Simula lecturas Bluetooth desde el dashboard del cliente. |
| `GET` | `/api/alertas/en-vivo` | Sesión (filtra por cliente; admin ve todas) | Sondeo de alertas recientes para notificaciones del navegador. |
| `POST` | `/api/alertas/<id>/mostrada` | Sesión + CSRF + dueño o admin | Marca como `ENVIADO` la notificación `NAVEGADOR` mostrada. |

---

## 7. Comandos de Gestión y Mantenimiento

* **Ejecutar servidor:**
  ```bash
  python manage.py runserver 0.0.0.0:8080
  ```
* **Aplicar migraciones:**
  ```bash
  python manage.py migrate
  ```
* **Probar integración con canales externos:**
  ```bash
  python manage.py probar_canales --email destino@correo.com --whatsapp 3001234567
  ```
* **Ejecutar suite de pruebas automatizadas:**
  ```bash
  python manage.py test
  ```
* **Importar datos de MySQL a PostgreSQL:**
  ```bash
  python manage.py importar_mysql "datos/dump.sql" --limpiar
  ```
