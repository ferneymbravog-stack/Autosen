# AutoSen (Django)

AutoSen es un sistema de monitoreo vehicular. Permite:

- Registrar clientes, vehículos y sensores.
- Recibir lecturas OBD2 (desde la app Android o con la simulación del dashboard web).
- Generar alertas cuando un sensor pasa a advertencia (nivel ≥ 40) o a falla (nivel ≥ 70).
- Consultar y exportar reportes en PDF, Excel y CSV.

Esta es la migración a **Python/Django + PostgreSQL** del proyecto original en Spring Boot.
Conserva las mismas pantallas, rutas, reglas de negocio y la API que usa la app Android.

| Documento | Contenido | Issue Vinculado |
|---|---|:---:|
| [`docs/SCRUM.md`](docs/SCRUM.md) | Metodología Scrum oficial, Product Goal, Product Backlog, DoD y guía de GitHub Projects | `#12` |
| [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) | Arquitectura Django, capas MVT, patrones GoF, diagramas de clases, paquetes y despliegue | `#2`, `#8` |
| [`docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`](docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md) | Requisitos funcionales (RQF) y no funcionales (RNF) del sistema | `#3`, `#4` |
| [`docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md`](docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md) | Historias de usuario con criterios de aceptación y diagrama de casos de uso | `#5`, `#6` |
| [`docs/MODELO_DE_DATOS.md`](docs/MODELO_DE_DATOS.md) | Modelo Entidad-Relación (MER), Modelo Relacional (MR) y Diccionario de datos | `#7` |
| [`docs/MANUAL_TECNICO.md`](docs/MANUAL_TECNICO.md) | Manual técnico para Django, stack, endpoints API, settings y comandos de despliegue | `#9` |
| [`docs/MANUAL_DE_USUARIO.md`](docs/MANUAL_DE_USUARIO.md) | Manual de usuario por roles (`Cliente`, `SuperAdmin`, `Admin`, `Soporte`) | `#10` |
| [`docs/CALIDAD_Y_PRUEBAS.md`](docs/CALIDAD_Y_PRUEBAS.md) | Documentación de calidad, pruebas unitarias automatizadas y CI GitHub Actions | `#11` |
| [`docs/INVENTARIO_Y_CONSOLIDACION.md`](docs/INVENTARIO_Y_CONSOLIDACION.md) | Inventario de diferencias resueltas Java vs Django y consolidación final | `#1`, `#12` |
| [`PATRONES_GOF.md`](PATRONES_GOF.md) | Documentación de patrones de diseño GoF (Strategy, Factory, Singleton, Observer) | `#2` |

## Requisitos

- Python 3.12 o superior. Se probó con Python 3.15 y Django 6.1.2.
- PostgreSQL 18.

## Instalación

1. **Instalar PostgreSQL 18.** Guarda la contraseña del usuario `postgres`.

   ```bash
   winget install -e --id PostgreSQL.PostgreSQL.18
   ```

2. **Crear la base de datos `vehiculos`.** Pide la contraseña de `postgres`.

   ```bash
   "C:/Program Files/PostgreSQL/18/bin/createdb.exe" -h 127.0.0.1 -U postgres -E UTF8 -T template0 vehiculos
   ```

3. **Configurar el archivo `.env`.** Copia `.env.example` como `.env` y completa:
   - `SECRET_KEY`: una cadena larga y aleatoria.
   - `DB_PASSWORD`: la contraseña de PostgreSQL.

   `.env` no se sube a git.

4. **Crear el entorno virtual e instalar las dependencias.**

   ```bash
   python -m venv .venv
   .venv/Scripts/pip install --only-binary=:all: -r requirements.txt
   ```

5. **Crear las tablas.**

   ```bash
   .venv/Scripts/python manage.py migrate
   ```

6. **Importar los datos de MySQL.** Exporta la base `vehiculos` con phpMyAdmin (formato SQL) y guarda el archivo en `datos/`. Esa carpeta no se sube a git, porque el dump trae datos personales. Las contraseñas existentes siguen funcionando.

   ```bash
   .venv/Scripts/python manage.py importar_mysql "datos/vehiculos (10).sql"
   ```

   Para volver a importar un dump más reciente sobre una base con datos, añade `--limpiar` (borra los datos actuales antes de importar).

7. **Arrancar el servidor en el puerto 8080**, el que usa la app Android.

   ```bash
   .venv/Scripts/python manage.py runserver 0.0.0.0:8080
   ```

   - Web del cliente: http://localhost:8080/
   - Panel de administración: http://localhost:8080/admin

## App Android

La app apunta a `http://10.0.2.2:8080/`, que es la IP con la que el emulador de Android
ve tu PC. `10.0.2.2` ya está en `ALLOWED_HOSTS`, así que solo hay que arrancar el
servidor como en el paso 7.

Con un teléfono físico en la misma red:

1. Añade la IP de tu PC en `ALLOWED_HOSTS_EXTRA` dentro de `.env`.
2. Cambia `BASE_URL` en la app.

La API (`/api/**`) no usa sesión ni CSRF, igual que la espera la app (salvo los endpoints exclusivos del navegador web con sesión).

## Notificaciones reales

AutoSen consume servicios externos reales para despachar automáticamente las alertas de advertencia (`nivel >= 40`) y falla crítica (`nivel >= 70`), registrando el estado real (`ENVIADO`, `FALLIDO`, `OMITIDO` o `EN_COLA`) y el motivo en caso de error u omisión. Todas las credenciales se configuran únicamente en `.env` (ver `.env.example`).

### 1. Telegram (`Telegram Bot API`)
1. Abre Telegram, busca **`@BotFather`** y envía el comando `/newbot`. Sigue las instrucciones para darle nombre y usuario al bot y copia el **token** entregado (`TELEGRAM_BOT_TOKEN`).
2. Crea un grupo en Telegram, agrega tu bot al grupo y envía al menos un mensaje de texto dentro del grupo.
3. Abre en el navegador `https://api.telegram.org/bot<TOKEN>/getUpdates` (reemplazando `<TOKEN>` por tu token real) y busca el objeto `"chat":{"id": ...}`. Copia ese número en `TELEGRAM_CHAT_ID` (en los grupos el ID es **negativo**, por ejemplo `-1001234567890`).

### 2. Email (`Gmail SMTP`)
1. Entra a la cuenta de Google remitente y activa la **Verificación en dos pasos** (*Seguridad → Verificación en 2 pasos*).
2. En la misma sección de Seguridad, entra a **Contraseñas de aplicaciones**, genera una clave de 16 caracteres para *"Correo"* y cópiala en `EMAIL_HOST_PASSWORD` (**no uses tu contraseña normal de Gmail**).
3. Configura tu dirección en `EMAIL_HOST_USER` (y opcionalmente `DEFAULT_FROM_EMAIL`).

### 3. WhatsApp (`WhatsApp Cloud API de Meta`)
1. Ingresa a [developers.facebook.com](https://developers.facebook.com/), crea una aplicación de tipo **Empresa (Business)** y agrega el producto **WhatsApp**.
2. En *WhatsApp → Configuración de la API*, copia el **Identificador de número de teléfono** (`WHATSAPP_PHONE_NUMBER_ID`), el **Token de acceso** (`WHATSAPP_TOKEN`) y la versión del endpoint mostrada en el panel (`WHATSAPP_API_VERSION`, p. ej. `v21.0`).
3. En la sección *Para*, registra y verifica con código hasta **5 números de teléfono de prueba** destinatarios.
4. **Regla de las 24 horas:** en modo estándar sin plantillas aprobadas, el destinatario debe haber enviado primero un mensaje al número de prueba de WhatsApp dentro de las últimas **24 horas** para abrir la ventana de conversación.
5. **Vigencia del token:** el token temporal del panel de Meta **vence en 24 horas**. Para uso continuo o producción, crea un **Usuario del sistema** en el *Business Manager* de Meta, asígnale permisos sobre la app y la cuenta de WhatsApp Business (`whatsapp_business_messaging`) y genera un **token permanente**.

### 4. Navegador (`API Notification`)
1. Inicia sesión en el dashboard del cliente (`/dashboard`) o en el panel administrativo (`/admin`).
2. Presiona el botón **🔔 Activar notificaciones** en la parte superior derecha y acepta el permiso emergente del navegador.
3. Cuando ingrese una alerta nueva, aparecerá una notificación nativa del sistema operativo; al hacer clic sobre ella se enfocará la pestaña de AutoSen y el registro pasará de `EN_COLA` a `ENVIADO`.

### 5. Probar todos los canales por consola
Ejecuta el comando integrado para verificar tus credenciales reales antes de operar:

```bash
python manage.py probar_canales --email destino@correo.com --whatsapp 3001234567
```

## Pruebas

```bash
.venv/Scripts/python manage.py test
```

Las pruebas crean una base temporal `test_vehiculos`, así que el usuario de PostgreSQL
necesita permiso para crear bases de datos (el usuario `postgres` lo tiene).

## Metodología Ágil: Scrum & GitHub Projects

El proyecto se gestiona bajo el marco oficial **Scrum** complementado con **GitHub Projects** para la trazabilidad visual y gestión de tareas:

🔗 **Tablero Oficial en GitHub Projects:** [https://github.com/users/ferneymbravog-stack/projects/4](https://github.com/users/ferneymbravog-stack/projects/4)

---

### 1. Objetivo del Producto (Product Goal)
> **"Empoderar a propietarios de vehículos y técnicos automotrices mediante una plataforma web conectada por OBD2/Bluetooth, que ofrece monitoreo de telemetría en tiempo real, detección temprana de fallas críticas y despacho automático de alertas multicanal (Email, WhatsApp al número del cliente, Telegram y Web Push) para prevenir averías costosas y garantizar la seguridad vehicular."**

* **¿Por qué no es una tarea?** "Crear un CRUD o una vista" es un trabajo técnico. "Facilitar el monitoreo preventivo y alertas inmediatas ante fallas mecánicas" describe el valor real que entrega el producto al usuario.

---

### 2. Tareas del Sprint en GitHub Projects (Backlog del Sprint)

Las tareas planificadas en el tablero oficial de GitHub Projects ([Tablero #4](https://github.com/users/ferneymbravog-stack/projects/4)):

| # | Código / Tarea | Issue | Responsables | Estado |
| :---: | :--- | :---: | :--- | :---: |
| 1 | **[DOC-01]** Inventariar las diferencias entre la documentación y el código | `#1` | `ferneymbravog-stack` | `Backlog` |
| 2 | **[DOC-02]** Actualizar el Documento de Especificación de Arquitectura | `#2` | `ferneymbravog-stack` | `Backlog` |
| 3 | **[DOC-03]** Actualizar los requisitos funcionales (RQF) | `#3` | `Gonzalez82ZG`, `jadir-dev` | `Backlog` |
| 4 | **[DOC-04]** Actualizar los requisitos no funcionales (RNF) | `#4` | `ferneymbravog-stack` | `Backlog` |
| 5 | **[DOC-05]** Actualizar y completar las historias de usuario | `#5` | `Gonzalez82ZG`, `jadir-dev` | `Backlog` |
| 6 | **[DOC-06]** Actualizar los casos de uso y sus diagramas | `#6` | `Gonzalez82ZG`, `jadir-dev` | `Backlog` |
| 7 | **[DOC-07]** Actualizar el modelo de datos (MER, MR, diccionario y scripts SQL) | `#7` | `ferneymbravog-stack` | `Backlog` |
| 8 | **[DOC-08]** Rehacer los diagramas de clases, paquetes, componentes y despliegue | `#8` | `ferneymbravog-stack` | `Backlog` |
| 9 | **[DOC-09]** Reescribir el Manual Técnico para Django | `#9` | `ferneymbravog-stack` | `Backlog` |
| 10 | **[DOC-10]** Actualizar el Manual de Usuario | `#10` | `Gonzalez82ZG`, `jadir-dev` | `Backlog` |
| 11 | **[DOC-11]** Actualizar la Documentación de Calidad (Ítem 8) | `#11` | `ferneymbravog-stack` | `Backlog` |
| 12 | **[DOC-12]** Alinear la descripción, el README y la presentación, y consolidar la entrega | `#12` | `ferneymbravog-stack` | `Backlog` |

#### Tareas Técnicas y Funcionalidades Integradas (Backlog Técnico):

| # | Código / Tarea | Issue | Responsables | Estado |
| :---: | :--- | :---: | :--- | :---: |
| 13 | **[FEAT-01]** Integrar API REST de telemetría OBD2 y códigos DTC de falla | `#13` | `ferneymbravog-stack` | `Done` |
| 14 | **[FEAT-02]** Implementar control de acceso y decoradores por rol (`SUPERADMIN`, `ADMIN`, `SOPORTE`) | `#14` | `ferneymbravog-stack` | `Done` |
| 15 | **[FEAT-03]** Despacho multicanal de alertas con enlace directo a WhatsApp Web | `#15` | `ferneymbravog-stack` | `Done` |
| 16 | **[FEAT-04]** Módulo de auditoría inmutable de operaciones y eventos de autenticación | `#16` | `ferneymbravog-stack` | `Done` |
| 17 | **[FEAT-05]** Generador de reportes técnicos avanzados con exportación PDF/Excel/CSV | `#17` | `Gonzalez82ZG` | `Done` |
| 18 | **[FEAT-06]** Portal de usuario con auto-registro de teléfono y switch de tema oscuro/claro | `#18` | `jadir-dev` | `Done` |
| 19 | **[PERF-01]** Optimización de consultas ORM de sensores y pool de conexiones PostgreSQL | `#19` | `ferneymbravog-stack` | `Done` |
| 20 | **[SEC-01]** Endurecimiento de seguridad: protección CSRF y contraseñas cifradas con bcrypt | `#20` | `ferneymbravog-stack` | `Done` |

---

### 3. Historias de Usuario y Criterios de Aceptación

#### Historia de Usuario #1 — Notificaciones de Alerta por WhatsApp
```text
COMO propietario de un vehículo (cliente),
QUIERO recibir alertas automáticas a mi número personal de WhatsApp cuando un sensor detecte fallas críticas (≥70%),
PARA atender oportunamente el vehículo antes de que sufra daños mecánicos graves o quede varado.
```
* **Criterios de Aceptación:**
  - **Criterio 1:** Si el cliente registra un teléfono al crear la cuenta o registrarse, el mensaje de WhatsApp se despacha a ese número (`https://api.whatsapp.com/send?phone=...`).
  - **Criterio 2:** Si el cliente no registra número telefónico, el canal WhatsApp se omite de forma limpia sin generar excepciones y los demás canales (Email, Telegram, Web Push) se envían con éxito.
  - **Criterio 3:** En la bandeja de notificaciones (`/admin/notificaciones`), cada mensaje de WhatsApp incluye el botón directo **"Abrir chat WhatsApp →"**.

#### Historia de Usuario #2 — Diagnóstico Técnico de Sensores en Vivo
```text
COMO técnico de soporte automotriz,
QUIERO disponer de un panel especializado con alertas visuales, sonoras y notificaciones Web Push,
PARA supervisar y calibrar rápidamente los sensores en estado de falla o advertencia sin menús innecesarios.
```
* **Criterios de Aceptación:**
  - **Criterio 1:** El rol `SOPORTE` accede directamente a su panel de telemetría destacando las incidencias técnicas activas.
  - **Criterio 2:** Las alertas sonoras y toasts Web Push se disparan en tiempo real cuando un sensor supera el 40% de desgaste.
  - **Criterio 3:** Los técnicos pueden calibrar y editar el estado de los sensores directamente desde su dashboard.

---

### 4. Sprint 1 Backlog & Sprint Goal (Incremento Entregado)

* **Objetivo del Sprint (Sprint Goal):**
  > *"Construir el núcleo operativo funcional de AutoSen en Django con base de datos PostgreSQL, garantizando la telemetría vehicular OBD2, despacho de notificaciones multicanal (Email, WhatsApp al número del cliente, Telegram, Web Push), registro de auditoría global y paneles administrativos protegidos por rol."*
* **PBIs Incluidos en el Sprint 1:** PBIs #1, #2, #3, #4 y #5.
* **Incremento Entregado y Verificado:**
  - Portal público y registro de clientes con validación de teléfono y correo (`/register`, `/login`).
  - Dashboard del cliente para consulta de flota vehicular y estado de sensores (`/dashboard`, `/vehiculos`).
  - Paneles administrativos por rol (`SUPERADMIN`, `ADMIN`, `SOPORTE`).
  - Despacho multicanal desacoplado con el patrón GoF Observador.
  - Módulo de auditoría del sistema (`/admin/auditoria`).
  - Generación de reportes PDF técnicos y administrativos (`/admin/reportes`).

---

### 5. Tablero GitHub Projects (Flujo Visual Kanban)

El flujo de trabajo se gestiona en GitHub Projects mediante 5 columnas oficiales y campos de seguimiento:

```
+---------------------------------------------------------------------------------------------------+
|                           TABLERO GITHUB PROJECTS — AUTOSEN OBD2                                  |
+-------------------+-------------------+-------------------+-------------------+-------------------+
|  1. BACKLOG       |  2. READY         |  3. IN PROGRESS   |  4. IN REVIEW     |  5. DONE          |
+-------------------+-------------------+-------------------+-------------------+-------------------+
| #6 GPS en vivo    | PBIs refinados    | Tareas en         | Pull Requests     | Incremento        |
| (Baja prioridad)  | y con criterios   | desarrollo activo | abiertos con      | verificado que    |
|                   | de aceptación     | en ramas feature  | revisión y tests  | cumple la DoD     |
|                   | aprobados         |                   | automáticos       | al 100%           |
+-------------------+-------------------+-------------------+-------------------+-------------------+
```

* **Campos Mínimos de Configuración:**
  * `Status` (Estado): Backlog, Ready, In Progress, In Review, Done.
  * `Priority` (Prioridad): P0 (Urgente / Crítica), P1 (Alta), P2 (Media), P3 (Baja).
  * `Linked Pull Request`: Enlace directo al PR que implementa la historia.

---

### 6. Definición de Terminado (Definition of Done - DoD)

Un PBI o Pull Request solo se mueve a **`Done`** si cumple rigurosamente con esta lista de verificación transversal:

- [x] **Arranque Limpio:** La aplicación inicia con `python manage.py runserver` sin advertencias ni fallos.
- [x] **Base de Datos:** Migraciones ejecutadas y aplicadas limpiamente en PostgreSQL (`python manage.py migrate`).
- [x] **Pruebas Automatizadas:** 100% de las pruebas unitarias y de integración pasan satisfactoriamente (`python manage.py test`).
- [x] **Criterios de Aceptación:** Cada criterio de aceptación de la historia de usuario fue probado y verificado en caliente.
- [x] **Seguridad:** No existen claves, contraseñas ni archivos `.env` expuestos en el repositorio.
- [x] **Trazabilidad:** Cada cambio cuenta con su Issue, rama `feature/...`, commit descriptivo y Pull Request.
- [x] **Documentación:** El `README.md` explica la instalación, configuración y arquitectura del proyecto.

---

### 7. Eventos de Scrum

* **Planificación del Sprint (Sprint Planning):** El equipo define *por qué* es valioso el Sprint (Sprint Goal), *qué* elementos del Product Backlog se seleccionan y *cómo* se construirán técnicamente.
* **Scrum Diario (Daily Scrum):** Inspección diaria de 15 minutos de los Developers para revisar el avance hacia el Objetivo del Sprint y resolver impedimentos técnicos.
* **Revisión del Sprint (Sprint Review):** Demostración del incremento de software funcional frente a los interesados (propietarios, técnicos y administradores) para recopilar retroalimentación real.
* **Retrospectiva del Sprint (Sprint Retrospective):** Sesión del equipo para analizar qué funcionó bien, qué nos frenó y qué compromisos de mejora se aplicarán en el siguiente ciclo.

---

### 8. Glosario Bilingüe Scrum / SBOK / GitHub

| Término en Inglés | Equivalencia en Español | Definición / Sentido Ágil |
| :--- | :--- | :--- |
| **Product Goal** | Objetivo del Producto | Compromiso a largo plazo que define el propósito y valor global del sistema AutoSen. |
| **Product Backlog** | Lista de Producto | Lista única, ordenada y evolutiva de todo lo que el producto necesita. |
| **Product Backlog Item (PBI)** | Elemento del Backlog | Necesidad de usuario, funcionalidad o mejora desglosada en el backlog. |
| **Sprint Goal** | Objetivo del Sprint | Meta concreta acordada por el equipo para el ciclo de trabajo actual. |
| **Sprint Backlog** | Lista del Sprint | PBIs seleccionados + el plan técnico de los Developers para construirlos. |
| **Increment** | Incremento | Versión concreta, integrada y utilizable del producto que cumple la DoD. |
| **Definition of Done (DoD)** | Definición de Terminado | Criterios de calidad transversales que garantizan que el incremento está listo. |
| **Issue** | Asunto / Incidencia | Registro rastreable en GitHub para describir una necesidad, tarea o error técnico. |
| **Pull Request (PR)** | Solicitud de Integración | Mecanismo en GitHub para revisar, verificar y fusionar cambios de código a `main`. |
| **Scrumboard / Project** | Tablero Visual / Proyecto | Tablero Kanban en GitHub para visualizar el flujo (`Backlog` -> `Done`). |
| **Daily Scrum** | Scrum Diario | Reunión diaria de 15 minutos para inspeccionar el progreso hacia el Sprint Goal. |
| **Sprint Review** | Revisión del Sprint | Sesión colaborativa para inspeccionar el incremento y recopilar retroalimentación. |
| **Sprint Retrospective** | Retrospectiva del Sprint | Evento de mejora continua para evaluar la forma de trabajo del equipo. |

---

## Estructura

| Carpeta | Contenido | Equivale en Java a |
|---|---|---|
| `autosen/` | configuración del proyecto (`settings.py`, `urls.py`) | `application.properties`, `SecurityConfig` |
| `core/` | modelos, login de cliente y admin, utilidades, middleware de tema, patrones GoF, importador | `model/`, `service/`, `config/`, `patrones/` |
| `web/` | web del cliente | `AuthController`, `DashboardController`, `VehiculoController` |
| `panel/` | panel de administración | `AdminController` |
| `reportes/` | reportes, filtros y exportaciones | `ReporteController`, exportaciones de `AdminController` |
| `api/` | API JSON de la app Android | `ApiController`, `Obd2Controller` |
| `templates/` | plantillas HTML | plantillas Thymeleaf |
| `static/` | CSS y JS del botón de tema | `static/` |
