# AutoSen — Metodología Scrum y Gestión con GitHub Projects

Este documento define la aplicación formal del marco ágil **Scrum** y su integración con **GitHub Projects** para el desarrollo y evolución del sistema **AutoSen (Telemetría Vehicular OBD2 y Diagnóstico Predictivo)**, basado en la Guía Oficial de Scrum y las mejores prácticas de la Guía SBOK (SCRUMstudy).

---

## 1. Fundamentos: Agilidad, Scrum y GitHub

* **Agilidad:** Manera de trabajar basada en iteraciones cortas, retroalimentación temprana, colaboración y capacidad de responder al cambio sobre seguir un plan rígido.
* **Scrum:** Marco de trabajo ligero que genera valor mediante tres responsabilidades claras, cinco eventos oficiales, tres artefactos y tres compromisos formales.
* **GitHub & GitHub Projects:** Herramienta tecnológica de soporte para almacenar el repositorio, registrar el historial de versiones (Git), rastrear el trabajo mediante Issues, gestionar tableros visuales (Projects), validar mediante Pull Requests y automatizar integración continua (GitHub Actions).

### Pilares del Empirismo y Valores de Scrum
1. **Transparencia:** Todo el trabajo real, el estado de los sensores, alertas y fallas es visible en el tablero y el sistema.
2. **Inspección:** Se revisa continuamente el incremento de software y los datos de telemetría sin maquillar resultados.
3. **Adaptación:** El plan del Sprint se ajusta ante bloqueos técnicos o nuevos hallazgos.
4. **Cinco Valores:** Compromiso, Foco, Franqueza, Respeto y Coraje.

---

## 2. Equipo Scrum y Responsabilidades

| Rol / Responsabilidad | Nombre / Asignación | Función en AutoSen |
| :--- | :--- | :--- |
| **Product Owner (PO)** | Equipo de Producto AutoSen | Maximiza el valor del producto, define el **Objetivo del Producto**, prioriza el Product Backlog según impacto en usuarios y talleres. |
| **Scrum Master (SM)** | Facilitador Ágil | Asegura la correcta aplicación de Scrum, remueve impedimentos técnicos del equipo y fomenta la mejora continua. |
| **Developers (Desarrolladores)** | Equipo Técnico / Full Stack | Diseñan, codifican, configuran la base de datos, escriben pruebas unitarias e integran el incremento cumpliendo la **DoD**. |
| **Stakeholders (Interesados)** | Conductores, Clientes, Administradores, Técnicos de Soporte y Talleres | Aportan necesidades reales de telemetría vehicular, validan alertas y utilizan los reportes. |

---

## 3. Artefactos y Compromisos de Scrum

```
+---------------------------------------------------------------------------------------+
|  ARTEFACTO OFICIAL          |  COMPROMISO ASOCIADO        |  PREGUNTA CLAVE           |
+-----------------------------+-----------------------------+---------------------------+
|  1. Product Backlog         |  Objetivo del Producto      |  ¿Qué valor a largo plazo |
|                             |  (Product Goal)             |  queremos alcanzar?       |
|-----------------------------+-----------------------------+---------------------------|
|  2. Sprint Backlog          |  Objetivo del Sprint        |  ¿Qué lograremos en este  |
|                             |  (Sprint Goal)              |  ciclo de trabajo?        |
|-----------------------------+-----------------------------+---------------------------|
|  3. Increment (Incremento)  |  Definición de Terminado    |  ¿Cumple con la calidad   |
|                             |  (Definition of Done - DoD) |  exigida para producción? |
+---------------------------------------------------------------------------------------+
```

---

## 4. Paso a Paso: Del Problema al Incremento de Software

### Paso 1: Objetivo del Producto (Product Goal)
> **"Empoderar a propietarios de vehículos y técnicos automotrices mediante una plataforma web conectada por OBD2/Bluetooth, que ofrece monitoreo de telemetría en tiempo real, detección temprana de fallas críticas y despacho automático de alertas multicanal (Email, WhatsApp, Telegram y Web Push) para prevenir averías costosas y garantizar la seguridad vehicular."**

---

### Paso 2: Product Backlog Priorizado (PBIs)

| ID | PBI (Elemento de Trabajo) | Descripción / Necesidad de Usuario | Prioridad | Estado |
| :---: | :--- | :--- | :---: | :---: |
| **#1** | **Monitoreo de Sensores OBD2** | Lectura, calibración y semaforización de sensores (ECT, MAP, RPM, TPS, O2, Nivel de Combustible). | **Alta** | `Done` |
| **#2** | **Despacho Multicanal de Alertas** | Envío automático de notificaciones ante desgaste ≥40% o falla ≥70% vía Email, WhatsApp (al número del cliente), Telegram y Web Push. | **Alta** | `Done` |
| **#3** | **Seguridad y Control de Acceso por Roles** | Dashboards diferenciados con permisos específicos: `SUPERADMIN`, `ADMIN`, `SOPORTE` y portal `CLIENTE`. | **Alta** | `Done` |
| **#4** | **Registro de Auditoría del Sistema** | Trazabilidad inmutable de altas, bajas, modificaciones, bloqueos y accesos técnicos. | **Media** | `Done` |
| **#5** | **Exportación de Reportes Técnicos** | Generación de informes en formato PDF descargables e imprimibles de sensores, clientes y flota. | **Media** | `Done` |
| **#6** | **Integración de Telemetría GPS en Vivo** | Mapeo geográfico de trayectos y ubicación del vehículo ante emergencias. | **Baja** | `Backlog` |

---

### Paso 3: Historias de Usuario (Formato Estándar)

#### Historia de Usuario #1 — Notificación Directa por WhatsApp
```markdown
COMO cliente y propietario de un vehículo,
QUIERO recibir una notificación inmediata a mi número personal de WhatsApp cuando un sensor detecte una falla crítica,
PARA tomar acciones mecánicas antes de que el motor sufra un daño grave o el vehículo quede varado.
```

#### Historia de Usuario #2 — Diagnóstico Operativo de Soporte Técnico
```markdown
COMO técnico de soporte automotriz,
QUIERO disponer de un panel de diagnóstico en tiempo real con alertas sonoras y notificaciones Web Push,
PARA atender prioritariamente los sensores con desgaste superior al 70% sin perder tiempo navegando menús administrativos.
```

---

### Paso 4: Criterios de Aceptación (Acceptance Criteria)

Para el PBI **#2 (Despacho Multicanal y WhatsApp al número del cliente)**:
* **Criterio 1:** Si el cliente tiene un número registrado al crear la cuenta o registrarse, las alertas de WhatsApp se despachan a dicho número (`https://api.whatsapp.com/send?phone=...`).
* **Criterio 2:** Si el cliente no registra número telefónico, el canal WhatsApp se omite de forma limpia sin generar excepciones y los demás canales (Email, Telegram, Web Push) se entregan con éxito.
* **Criterio 3:** En el panel de notificaciones (`/admin/notificaciones`), cada mensaje de WhatsApp incluye un enlace directo para abrir el chat en WhatsApp Web.
* **Criterio 4:** Si el desgaste del sensor es menor a 40%, no se genera alerta crítica para evitar saturación de mensajes.

---

### Paso 5: Planificación del Sprint 1 (Sprint Planning)

* **Objetivo del Sprint (Sprint Goal):**
  > *"Construir el núcleo operativo funcional de AutoSen en Django con base de datos PostgreSQL, garantizando la telemetría vehicular OBD2, despacho de notificaciones multicanal (Email, WhatsApp al cliente, Telegram, Web Push), auditoría global y paneles administrativos protegidos por rol."*
* **PBIs seleccionados:** #1, #2, #3, #4, #5.
* **Plan técnico de los Desarrolladores:**
  1. Configuración de modelos ORM (`Cliente`, `Vehiculo`, `Sensor`, `Alerta`, `RegistroAuditoria`, `NotificacionEnviada`).
  2. Implementación de patrones de diseño GoF: Observador (despacho de alertas), Estrategia (cálculo de niveles OBD2), Fábrica (sensores base) y Singleton.
  3. Creación de plantillas HTML responsivas con soporte de tema oscuro/claro.
  4. Redacción y ejecución de pruebas unitarias con el test runner de Django.

---

### Paso 6: Tablero de GitHub Projects (Flujo Visual Kanban)

El tablero de GitHub Projects para AutoSen se estructura con 5 columnas oficiales y campos de seguimiento:

```
+---------------------------------------------------------------------------------------------------+
|                           TABLERO GITHUB PROJECTS — AUTOSEN OBD2                                  |
+-------------------+-------------------+-------------------+-------------------+-------------------+
|  1. BACKLOG       |  2. READY         |  3. IN PROGRESS   |  4. IN REVIEW     |  5. DONE          |
+-------------------+-------------------+-------------------+-------------------+-------------------+
| #6 GPS en vivo    | Refinadas y con   | Tareas en         | Pull Requests     | Incremento        |
| (Baja prioridad)  | criterios de      | codificación      | abiertos con      | verificado que    |
|                   | aceptación        | activa en una     | revisión y tests  | cumple la DoD     |
|                   | aprobados         | rama feature      | automáticos       | al 100%           |
+-------------------+-------------------+-------------------+-------------------+-------------------+
```

* **Campos Mínimos en GitHub Projects:**
  * `Status`: Backlog, Ready, In Progress, In Review, Done.
  * `Priority`: P0 (Crítica / Urgente), P1 (Alta), P2 (Media), P3 (Baja).
  * `Linked Pull Request`: Enlace bidireccional al PR correspondiente.

---

### Paso 7: Estrategia de Ramas y Commits (Git Workflow)

* **Rama Principal:** `main` (código estable que cumple con la Definición de Terminado).
* **Ramas de Trabajo:** `feature/<nombre-en-ingles>` o `fix/<nombre-en-ingles>`.
  * Ejemplo: `feature/multichannel-notifications-whatsapp`
  * Ejemplo: `feature/role-based-dashboards`
* **Formato de Commits:** En inglés, imperativo, conciso y rastreable:
  ```bash
  git commit -m "feat(notifications): dispatch whatsapp alerts to customer phone"
  git commit -m "feat(auth): add role-based permission control for superadmin, admin and support"
  git commit -m "test(core): add automated tests for client registration and notification dispatch"
  ```

---

### Paso 8: Definición de Terminado (Definition of Done - DoD)

Un PBI o Pull Request solo puede marcarse como **`Done`** si cumple rigurosamente con esta lista de verificación:

- [x] **Ejecución Limpia:** La aplicación inicia con `python manage.py runserver` sin errores ni advertencias de configuración.
- [x] **Base de Datos:** Migraciones ejecutadas y aplicadas limpiamente en PostgreSQL (`python manage.py migrate`).
- [x] **Pruebas Automatizadas:** Todas las pruebas unitarias y de integración pasan al 100% (`python manage.py test`).
- [x] **Criterios de Aceptación:** Cada criterio de aceptación de la historia de usuario ha sido comprobado en caliente.
- [x] **Seguridad:** No existen claves de API, contraseñas ni archivos `.env` versionados en Git.
- [x] **Trazabilidad:** Cada cambio está respaldado por su Issue, Pull Request y commit descriptivo.
- [x] **Documentación:** El `README.md` y guías técnicas explican cómo instalar, configurar y verificar la funcionalidad.

---

### Paso 9: Eventos de Cierre del Sprint

#### Sprint Review (Revisión del Sprint)
* **Objetivo:** Inspeccionar el incremento de software funcional con los interesados.
* **Demostración en vivo:**
  1. Registro de nuevo cliente con correo y número telefónico (`/register`).
  2. Inicio de sesión como cliente y consulta de telemetría vehicular (`/dashboard`).
  3. Ingreso como `SUPERADMIN` (`/admin`), supervisión del registro de auditoría (`/admin/auditoria`).
  4. Ingreso como `SOPORTE` y monitoreo de fallas en vivo con sonido y Web Push.
  5. Despacho de alerta crítica y comprobación de la notificación de WhatsApp y Email.
* **Resultado:** Incremento aceptado satisfactoriamente por cumplir todos los criterios y la DoD.

#### Sprint Retrospective (Retrospectiva del Sprint)
* **¿Qué funcionó bien?**
  * La separación de roles y permisos facilitó interfaces limpias y adaptadas a cada perfil.
  * El desacoplamiento del sistema de alertas usando el patrón Observador permitió agregar nuevos canales sin tocar la lógica del sensor.
* **¿Qué nos frenó?**
  * Requerir números con formato internacional para WhatsApp obligó a flexibilizar la validación para admitir entradas locales y con prefijo de país.
* **¿Qué cambiaremos en el próximo Sprint?**
  * Incorporar un validador en tiempo real con selector de país en la interfaz web para mayor comodidad del usuario.

---

## 5. Glosario Bilingüe de Términos (Scrum · GitHub · SBOK)

| Término en Inglés | Equivalencia en Español | Definición / Sentido Ágil |
| :--- | :--- | :--- |
| **Product Goal** | Objetivo del Producto | Compromiso a largo plazo que define el propósito y valor global del sistema. |
| **Product Backlog** | Lista de Producto | Lista única, ordenada y evolutiva de todo lo necesario para mejorar el producto. |
| **Product Backlog Item (PBI)** | Elemento del Product Backlog | Unidad de trabajo o necesidad desglosada en el backlog. |
| **Sprint Goal** | Objetivo del Sprint | Compromiso concreto acordado por el equipo para el ciclo de trabajo actual. |
| **Sprint Backlog** | Lista del Sprint | Subconjunto de PBIs elegidos + el plan técnico de los desarrolladores para construirlos. |
| **Increment** | Incremento | Versión concreta, integrada, utilizable e inspeccionable del producto que cumple la DoD. |
| **Definition of Done (DoD)** | Definición de Terminado | Conjunto formal de criterios de calidad que garantizan que el software está listo para usarse. |
| **Issue** | Asunto / Incidencia | Registro rastreable en GitHub para describir una necesidad, tarea o corrección técnica. |
| **Pull Request (PR)** | Solicitud de Integración | Mecanismo formal en GitHub para revisar, discutir y validar código antes de fusionarlo a `main`. |
| **Scrumboard / Project** | Tablero Visual / Proyecto | Tablero Kanban en GitHub para visualizar el flujo de trabajo (`Backlog` -> `Done`). |
| **Daily Scrum** | Scrum Diario | Evento diario de 15 minutos de los Developers para inspeccionar el progreso hacia el Sprint Goal. |
| **Sprint Review** | Revisión del Sprint | Evento colaborativo para inspeccionar el incremento y recopilar retroalimentación de los interesados. |
| **Sprint Retrospective** | Retrospectiva del Sprint | Evento de mejora continua para analizar procesos, relaciones y herramientas del equipo. |
