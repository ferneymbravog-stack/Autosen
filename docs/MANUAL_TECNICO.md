# Manual Técnico de la Aplicación — AutoSen (Django)

> **Issue asociado:**
> - `[DOC-09] Reescribir el Manual Técnico para Django (#9)`

---

## 1. Stack Tecnológico
* **Lenguaje:** Python 3.12+ (compatible con Python 3.15)
* **Framework Web:** Django 6.1.2
* **Base de Datos:** PostgreSQL 18
* **Conector:** `psycopg[binary] >= 3.2.0`
* **Seguridad de Claves:** `bcrypt >= 4.2.0`
* **Exportación de Documentos:** `reportlab >= 4.2.0` (PDFs vectoriales) y `openpyxl >= 3.1.5` (Excel)
* **Protocolo de Comunicación:** OBD-II (SAE J1979 / ISO 15765-4 CAN) vía Bluetooth SPP

---

## 2. Variables de Entorno (`.env`)

```ini
# Clave criptográfica de Django
SECRET_KEY=clave_secreta_django_larga_y_segura

# Modo de ejecución (False para producción)
DEBUG=True

# Conexión a Base de Datos PostgreSQL
DB_NAME=vehiculos
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

# Hosts permitidos
ALLOWED_HOSTS=localhost,127.0.0.1,10.0.2.2
```

---

## 3. Estructura de Módulos Django

```
autosen/
├── autosen/          # Configuración global del proyecto (settings, urls, wsgi)
├── core/             # Modelos de BD, patrones GoF, auditoría y middleware
│   ├── patrones/     # Implementación GoF: Strategy, Observer, Factory, Singleton
│   ├── migrations/   # Migraciones de base de datos
│   └── notificaciones.py # Despacho multicanal reactivo
├── web/              # Portal de usuario / cliente (vistas, URLs, plantillas)
├── panel/            # Panel administrativo (vistas por rol SuperAdmin/Admin/Soporte)
├── api/              # Endpoints JSON para telemetría OBD2 y app Android
├── reportes/         # Generador de reportes con filtros y exportación PDF/Excel
├── templates/        # Plantillas HTML5 responsivas con Bootstrap/Tailwind custom CSS
└── static/           # Archivos estáticos (CSS, JS, logos e iconos)
```

---

## 4. Endpoints Principales de la API (`/api/`)

| Método | Ruta | Parámetros / Body | Descripción |
| :---: | :--- | :--- | :--- |
| `POST` | `/api/login` | `correo`, `contrasena` | Autentica a un cliente desde la app Android. |
| `GET` | `/api/vehiculos` | `id_cliente` | Retorna el listado de vehículos asociados a un cliente. |
| `POST` | `/api/vehiculo/crear` | Datos del vehículo | Registra un nuevo vehículo desde la app móvil. |
| `POST` | `/api/obd2/vincular` | `id_vehiculo`, `elm_mac` | Asocia la dirección MAC del escáner ELM327. |
| `POST` | `/api/obd2/actualizar` | `id_vehiculo`, `sensor`, `valor` | Recibe lecturas de sensores y evalúa desgaste en tiempo real. |
| `GET` | `/api/alertas/en-vivo` | `desde_id` (opcional) | Sondeo en tiempo real de alertas para Web Push. |

---

## 5. Comandos de Gestión y Mantenimiento

* **Ejecutar servidor:**
  ```bash
  python manage.py runserver 0.0.0.0:8080
  ```
* **Aplicar migraciones:**
  ```bash
  python manage.py migrate
  ```
* **Ejecutar suite de pruebas (100% éxito):**
  ```bash
  python manage.py test
  ```
* **Importar datos de MySQL a PostgreSQL:**
  ```bash
  python manage.py importar_mysql "datos/dump.sql" --limpiar
  ```
