# Catálogo Oficial de Issues para GitHub — AutoSen

Este documento contiene la definición completa de las 20 Issues oficiales del proyecto para crearlas en [GitHub Issues](https://github.com/ferneymbravog-stack/Autosen/issues) o sincronizarlas con el [Tablero de GitHub Projects](https://github.com/users/ferneymbravog-stack/projects/4).

---

## 📋 Grupo 1: Documentación y Consolidación (Issues #1 a #12)

### Issue #1 · [DOC-01] Inventariar las diferencias entre la documentación y el código
* **Título:** `[DOC-01] Inventariar las diferencias entre la documentación y el código`
* **Etiquetas:** `documentation`, `sprint-1`, `consolidacion`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Revisar y documentar todas las diferencias y mejoras resultantes de la migración del proyecto original en Java Spring Boot a Python Django + PostgreSQL.

  ### Criterios de Aceptación
  - [x] Comparar modelos, rutas y controladores entre Java y Django.
  - [x] Registrar la paridad de funcionalidades y las mejoras añadidas (WhatsApp, WebPush, Auditoría).
  - [x] Documentado formalmente en `docs/INVENTARIO_Y_CONSOLIDACION.md`.
  ```

---

### Issue #2 · [DOC-02] Actualizar el Documento de Especificación de Arquitectura
* **Título:** `[DOC-02] Actualizar el Documento de Especificación de Arquitectura`
* **Etiquetas:** `architecture`, `documentation`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Definir la arquitectura modular MVT en Django, la capa de persistencia en PostgreSQL 18 y la integración de patrones de diseño GoF.

  ### Criterios de Aceptación
  - [x] Especificar arquitectura en capas: Web, Panel, Core, API y Reportes.
  - [x] Detallar patrones GoF: Strategy, Observer, Factory y Singleton.
  - [x] Documentado formalmente en `docs/ARQUITECTURA.md`.
  ```

---

### Issue #3 · [DOC-03] Actualizar los requisitos funcionales (RQF)
* **Título:** `[DOC-03] Actualizar los requisitos funcionales (RQF)`
* **Etiquetas:** `requirements`, `documentation`
* **Asignado a:** `Gonzalez82ZG`, `jadir-dev`
* **Descripción:**
  ```markdown
  ### Contexto
  Formalizar los requisitos funcionales del sistema AutoSen para telemetría OBD2, roles, alertas y auditoría.

  ### Criterios de Aceptación
  - [x] Redactar RQF-01 a RQF-15 con descripción y prioridad.
  - [x] Incluir el nuevo flujo de registro con teléfono/WhatsApp y despacho multicanal.
  - [x] Documentado formalmente en `docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`.
  ```

---

### Issue #4 · [DOC-04] Actualizar los requisitos no funcionales (RNF)
* **Título:** `[DOC-04] Actualizar los requisitos no funcionales (RNF)`
* **Etiquetas:** `requirements`, `security`, `performance`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Definir los atributos de calidad, rendimiento, seguridad, concurrencia y tolerancia a fallos del sistema.

  ### Criterios de Aceptación
  - [x] Especificar RNF-01 a RNF-08 (tiempos de respuesta <200ms, bcrypt, CSRF, ACID).
  - [x] Documentado formalmente en `docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`.
  ```

---

### Issue #5 · [DOC-05] Actualizar y completar las historias de usuario
* **Título:** `[DOC-05] Actualizar y completar las historias de usuario`
* **Etiquetas:** `user-story`, `scrum`
* **Asignado a:** `Gonzalez82ZG`, `jadir-dev`
* **Descripción:**
  ```markdown
  ### Contexto
  Estructurar las historias de usuario oficiales en formato estándar ("Como... quiero... para...") con criterios de aceptación.

  ### Criterios de Aceptación
  - [x] HU-01: Auto-registro con Teléfono y WhatsApp.
  - [x] HU-02: Diagnóstico Operativo para Soporte Técnico.
  - [x] HU-03: Auditoría y Control para SuperAdmin.
  - [x] HU-04: Despacho Multicanal de Alertas Críticas.
  - [x] Documentado formalmente en `docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md`.
  ```

---

### Issue #6 · [DOC-06] Actualizar los casos de uso y sus diagramas
* **Título:** `[DOC-06] Actualizar los casos de uso y sus diagramas`
* **Etiquetas:** `use-cases`, `diagrams`
* **Asignado a:** `Gonzalez82ZG`, `jadir-dev`
* **Descripción:**
  ```markdown
  ### Contexto
  Elaborar el diagrama general de casos de uso del sistema integrando los actores: Cliente, Administrador, SuperAdmin, Soporte y App Android.

  ### Criterios de Aceptación
  - [x] Incluir CU-01 al CU-10 con relaciones y actores.
  - [x] Generar diagrama interactivo en Mermaid.
  - [x] Documentado formalmente en `docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md`.
  ```

---

### Issue #7 · [DOC-07] Actualizar el modelo de datos (MER, MR, diccionario y scripts SQL)
* **Título:** `[DOC-07] Actualizar el modelo de datos (MER, MR, diccionario y scripts SQL)`
* **Etiquetas:** `database`, `postgresql`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Actualizar el Modelo Entidad-Relación y el Modelo Relacional para PostgreSQL 18, incluyendo las tablas de notificaciones, auditoría y teléfono del cliente.

  ### Criterios de Aceptación
  - [x] Diagrama Mermaid ER de todas las entidades.
  - [x] Diccionario de datos completo con tipos de datos, llaves foráneas y restricciones.
  - [x] Documentado formalmente en `docs/MODELO_DE_DATOS.md`.
  ```

---

### Issue #8 · [DOC-08] Rehacer los diagramas de clases, paquetes, componentes y despliegue
* **Título:** `[DOC-08] Rehacer los diagramas de clases, paquetes, componentes y despliegue`
* **Etiquetas:** `uml`, `diagrams`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Rehacer los diagramas UML para representar la estructura modular de Django, el flujo OBD2 Bluetooth y la infraestructura de despliegue.

  ### Criterios de Aceptación
  - [x] Diagrama de Paquetes y Módulos.
  - [x] Diagrama de Clases del Dominio.
  - [x] Diagrama de Despliegue Físico.
  - [x] Documentado formalmente en `docs/ARQUITECTURA.md`.
  ```

---

### Issue #9 · [DOC-09] Reescribir el Manual Técnico para Django
* **Título:** `[DOC-09] Reescribir el Manual Técnico para Django`
* **Etiquetas:** `technical-manual`, `django`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Elaborar el manual técnico integral explicando configuración de variables de entorno, endpoints de API REST, migración de base de datos y comandos de despliegue.

  ### Criterios de Aceptación
  - [x] Stack tecnológico y dependencias.
  - [x] Tabla de endpoints `/api/` y parámetros de entrada.
  - [x] Comandos de gestión y pruebas.
  - [x] Documentado formalmente en `docs/MANUAL_TECNICO.md`.
  ```

---

### Issue #10 · [DOC-10] Actualizar el Manual de Usuario
* **Título:** `[DOC-10] Actualizar el Manual de Usuario`
* **Etiquetas:** `user-manual`
* **Asignado a:** `Gonzalez82ZG`, `jadir-dev`
* **Descripción:**
  ```markdown
  ### Contexto
  Redactar el manual de usuario con guías operativas paso a paso para cada uno de los 4 perfiles del sistema.

  ### Criterios de Aceptación
  - [x] Guía del Cliente: registro con WhatsApp, gestión vehicular y lecturas.
  - [x] Guía de Soporte Técnico: centro de diagnóstico, Web Push y calibración.
  - [x] Guía de Administrador y SuperAdmin: gestión de equipo y auditoría.
  - [x] Documentado formalmente en `docs/MANUAL_DE_USUARIO.md`.
  ```

---

### Issue #11 · [DOC-11] Actualizar la Documentación de Calidad (Ítem 8)
* **Título:** `[DOC-11] Actualizar la Documentación de Calidad (Ítem 8)`
* **Etiquetas:** `qa`, `testing`, `ci-cd`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Documentar la estrategia de calidad, cobertura de pruebas unitarias automatizadas y el pipeline de Integración Continua con GitHub Actions.

  ### Criterios de Aceptación
  - [x] Tabla de suites de prueba por módulo.
  - [x] Configuración de GitHub Actions con PostgreSQL (`.github/workflows/django-tests.yml`).
  - [x] Matriz de cumplimiento de la Definición de Terminado (DoD).
  - [x] Documentado formalmente en `docs/CALIDAD_Y_PRUEBAS.md`.
  ```

---

### Issue #12 · [DOC-12] Alinear la descripción, el README y la presentación, y consolidar la entrega
* **Título:** `[DOC-12] Alinear la descripción, el README y la presentación, y consolidar la entrega`
* **Etiquetas:** `readme`, `delivery`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Alinear el README.md principal del repositorio incorporando la metodología Scrum, Product Goal, Sprint Backlog y enlaces a todos los documentos generados.

  ### Criterios de Aceptación
  - [x] Actualizar `README.md` con metodología Scrum y tabla de issues.
  - [x] Verificar enlaces e índices a documentos técnicos.
  - [x] Documentado formalmente en `docs/INVENTARIO_Y_CONSOLIDACION.md` y `README.md`.
  ```

---

## 🚀 Grupo 2: Características y Módulos Técnicos (Issues #13 a #20)

### Issue #13 · [FEAT-01] Integrar API REST de telemetría OBD2 y códigos DTC de falla
* **Título:** `[FEAT-01] Integrar API REST de telemetría OBD2 y códigos DTC de falla`
* **Etiquetas:** `feature`, `obd2`, `api`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Integrar el servicio REST de telemetría vehicular para recepción de tramas desde escáneres ELM327 Bluetooth y agregar catálogo de códigos de diagnóstico DTC estándar (P0100 a P0500).

  ### Criterios de Aceptación
  - [x] Endpoint `/api/obd2/actualizar` procesa niveles y valores en tiempo real.
  - [x] Helper `diagnostico_dtc` interpreta códigos de falla automotriz en español.
  - [x] Implementado en `api/obd2.py`.
  ```

---

### Issue #14 · [FEAT-02] Control de acceso granular y decoradores de seguridad por rol
* **Título:** `[FEAT-02] Control de acceso granular y decoradores de seguridad por rol`
* **Etiquetas:** `feature`, `auth`, `security`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Implementar decoradores de seguridad en Django para restringir vistas según los roles `SUPERADMIN`, `ADMIN` y `SOPORTE`.

  ### Criterios de Aceptación
  - [x] `@superadmin_requerido` restringe creación de administradores y auditoría.
  - [x] `@gestion_admin_requerido` previene acciones destructivas por parte de técnicos.
  - [x] `@soporte_requerido` garantiza acceso técnico a calibración y diagnóstico.
  - [x] Implementado en `core/auth.py`.
  ```

---

### Issue #15 · [FEAT-03] Despacho multicanal de alertas con enlace directo a WhatsApp Web
* **Título:** `[FEAT-03] Despacho multicanal de alertas con enlace directo a WhatsApp Web`
* **Etiquetas:** `feature`, `notifications`, `whatsapp`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Despachar automáticamente alertas críticas a Email, WhatsApp (al número del cliente), Telegram y Web Push, incluyendo enlaces directos click-to-chat.

  ### Criterios de Aceptación
  - [x] WhatsApp extrae dinámicamente `cliente.telefono` y genera el enlace prellenado.
  - [x] Si el cliente no tiene teléfono, omite WhatsApp sin generar errores.
  - [x] Bandeja `/admin/notificaciones` incluye botón *"Abrir chat WhatsApp →"*.
  - [x] Implementado en `core/notificaciones.py` y `templates/admin/notificaciones.html`.
  ```

---

### Issue #16 · [FEAT-04] Sistema de auditoría inmutable de operaciones y eventos de autenticación
* **Título:** `[FEAT-04] Sistema de auditoría inmutable de operaciones y eventos de autenticación`
* **Etiquetas:** `feature`, `audit`, `security`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Registrar en la base de datos cada operación de alta, baja, modificación, bloqueo y autenticación con fecha, hora, usuario e IP.

  ### Criterios de Aceptación
  - [x] Registro automático mediante `registrar_auditoria` y `auditar_autenticacion`.
  - [x] Vista `/admin/auditoria` exclusiva para SuperAdmin con tabla inmutable.
  - [x] Implementado en `core/auditoria.py` y `templates/admin/auditoria.html`.
  ```

---

### Issue #17 · [FEAT-05] Generador de reportes técnicos avanzados con exportación PDF/Excel/CSV
* **Título:** `[FEAT-05] Generador de reportes técnicos avanzados con exportación PDF/Excel/CSV`
* **Etiquetas:** `feature`, `reports`, `pdf`
* **Asignado a:** `Gonzalez82ZG`
* **Descripción:**
  ```markdown
  ### Contexto
  Permitir a administradores filtrar telemetría por fechas y clientes, y descargar informes técnicos vectoriales listos para imprimir.

  ### Criterios de Aceptación
  - [x] Exportador PDF vectorial con ReportLab (`/reportes/exportar/pdf`).
  - [x] Exportador Excel con OpenPyXL y CSV con codificación UTF-8 BOM.
  - [x] Implementado en `reportes/exportar.py` y `reportes/views.py`.
  ```

---

### Issue #18 · [FEAT-06] Portal de usuario con auto-registro de teléfono y switch de tema
* **Título:** `[FEAT-06] Portal de usuario con auto-registro de teléfono y switch de tema`
* **Etiquetas:** `feature`, `ui`, `theme`
* **Asignado a:** `jadir-dev`
* **Descripción:**
  ```markdown
  ### Contexto
  Ofrecer a los clientes una interfaz moderna con captura de teléfono/WhatsApp en `/register`, dashboard personal y alternador de tema claro/oscuro.

  ### Criterios de Aceptación
  - [x] Formulario de registro captura nombre, apellido, teléfono, correo y clave.
  - [x] Preserva valores ante errores de validación sin borrar lo escrito.
  - [x] Alternador de tema persistente en localStorage.
  - [x] Implementado en `templates/paginas/register.html` y `static/js/theme-toggle.js`.
  ```

---

### Issue #19 · [PERF-01] Optimización de consultas ORM de sensores y pool de conexiones PostgreSQL
* **Título:** `[PERF-01] Optimización de consultas ORM de sensores y pool de conexiones PostgreSQL`
* **Etiquetas:** `performance`, `orm`, `database`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Optimizar el tiempo de respuesta de las consultas del dashboard mediante índices, `select_related` y consultas agregadas en PostgreSQL.

  ### Criterios de Aceptación
  - [x] Dashboard carga conteos agregados de sensores en una única consulta.
  - [x] Índices creados en columnas de búsqueda frecuente (`placa`, `correo`, `tipo_sensor`).
  - [x] Implementado en `panel/views.py` y `core/models.py`.
  ```

---

### Issue #20 · [SEC-01] Endurecimiento de seguridad: protección CSRF y contraseñas cifradas con bcrypt
* **Título:** `[SEC-01] Endurecimiento de seguridad: protección CSRF y contraseñas cifradas con bcrypt`
* **Etiquetas:** `security`, `hardening`
* **Asignado a:** `ferneymbravog-stack`
* **Descripción:**
  ```markdown
  ### Contexto
  Garantizar el almacenamiento seguro de credenciales con factor de coste de trabajo bcrypt y protección estricta contra falsificación de peticiones en sitios cruzados.

  ### Criterios de Aceptación
  - [x] Hashes de contraseña con prefijo `$2a$` y costo 10 compatibles con Spring Boot.
  - [x] Validación obligatoria de tokens CSRF en todos los formularios web.
  - [x] Implementado en `core/auth.py` y `autosen/settings.py`.
  ```
