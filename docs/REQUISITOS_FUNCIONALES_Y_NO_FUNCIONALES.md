# Especificación de Requisitos Funcionales y No Funcionales — AutoSen

> **Issues asociados:**
> - `[DOC-03] Actualizar los requisitos funcionales (RQF) (#3)`
> - `[DOC-04] Actualizar los requisitos no funcionales (RNF) (#4)`

---

## 1. Requisitos Funcionales (RQF)

| Código | Módulo | Nombre del Requisito | Descripción | Prioridad |
| :---: | :--- | :--- | :--- | :---: |
| **RQF-01** | Autenticación | **Registro de Clientes con Teléfono** | El sistema permite el auto-registro de clientes capturando nombre, apellido, correo, teléfono/WhatsApp y contraseña cifrada. | Alta |
| **RQF-02** | Autenticación | **Control de Acceso Multi-Rol** | Inicio de sesión diferenciado para roles `SUPERADMIN`, `ADMIN`, `SOPORTE` y `CLIENTE`, restringiendo vistas según permisos. | Alta |
| **RQF-03** | Vehículos | **Gestión de Flota Vehicular** | Registro, edición, listado y desvinculación de vehículos con validación de placa colombiana (AAA123 o AAA-123). | Alta |
| **RQF-04** | Telemetría | **Lectura y Diagnóstico OBD2** | Recepción de tramas de telemetría vehicular desde escáneres ELM327 Bluetooth (ECT, MAP, RPM, TPS, O2, Combustible). | Alta |
| **RQF-05** | Telemetría | **Semaforización de Desgaste** | Evaluación automática de niveles de desgaste: Óptimo (<40%), Advertencia (40%-69%) y Falla Crítica (≥70%). | Alta |
| **RQF-06** | Telemetría | **Calibración Manual de Sensores** | Los técnicos de soporte pueden forzar o recalibrar niveles y valores de sensores para diagnóstico preventivo. | Media |
| **RQF-07** | Alertas | **Envío Real por Telegram Bot API** | Cuando se genera una alerta (≥40%), el sistema consume `Telegram Bot API` enviando el resumen HTML escapado al chat configurado y guardando el estado (`ENVIADO`, `FALLIDO` u `OMITIDO`). | Alta |
| **RQF-08** | Alertas | **Envío Real de Correo por Gmail SMTP** | El sistema envía al correo del cliente propietario un mensaje multiparte (texto plano + plantilla HTML con autoescape y colores por severidad) mediante `Gmail SMTP`. | Alta |
| **RQF-09** | Alertas | **Envío Real por WhatsApp Cloud API** | El sistema normaliza el teléfono del cliente a formato internacional (anteponiendo `57` a celulares colombianos) y consume `WhatsApp Cloud API` de Meta, traduciendo códigos de error (`131047`, `131030`, `190`). | Alta |
| **RQF-10** | Alertas | **Notificaciones Nativas del Navegador** | Los paneles de cliente y administrador permiten activar la `API Notification` del navegador, mostrando alertas exclusivas de los vehículos del cliente en sesión y marcándolas como `ENVIADO` en `/api/alertas/<id>/mostrada`. | Media |
| **RQF-11** | Alertas | **Prueba de Canales y Reintento Manual** | El panel administrativo (`/admin/notificaciones`) y el comando `probar_canales` permiten probar las APIs externas, filtrar por canal/estado y reintentar notificaciones `FALLIDAS`. | Media |
| **RQF-12** | Administración | **Gestión de Administradores y Bloqueo** | `SUPERADMIN` gestiona cuentas del equipo técnico; `ADMIN` y `SUPERADMIN` pueden bloquear o reactivar cuentas de clientes. | Alta |
| **RQF-13** | Auditoría | **Auditoría Inmutable y Control de Accesos Fallidos** | Registro histórico obligatorio enlazado por llave foránea al administrador (`ON DELETE SET NULL`) de cada acción del panel (`CREAR`, `EDITAR`, `ELIMINAR`, `BLOQUEAR`, `CALIBRAR`, `TEST`, `REINTENTAR`), así como eventos `LOGIN`, `LOGOUT` e intentos de acceso fallidos (`LOGIN_FALLIDO`) con fecha, IP y correo intentado (sin guardar nunca la contraseña), consultables con filtros por administrador, acción y fechas. | Alta |
| **RQF-14** | Reportes | **Filtros Avanzados y Exportación** | Consulta de telemetría con filtros por cliente, vehículo, sensor y fechas, exportable en PDF vectorial, Excel y CSV. | Media |
| **RQF-15** | Interfaz | **Soporte de Tema Oscuro y Claro** | Alternador visual persistente en toda la aplicación para comodidad del operador. | Baja |

---

## 2. Requisitos No Funcionales (RNF)

| Código | Categoría | Nombre del Requisito | Criterio de Aceptación / Métrica |
| :---: | :--- | :--- | :--- |
| **RNF-01** | **Rendimiento** | Tiempo de Respuesta y Envío en Segundo Plano | Las peticiones OBD2 responden sin esperar a las APIs externas: el despacho se ejecuta en segundo plano tras confirmar la transacción (`transaction.on_commit` + hilo demonio con cierre de conexión BD). |
| **RNF-02** | **Rendimiento** | Timeout Estricto en Servicios Externos | Toda petición HTTP hacia APIs externas (`Telegram Bot API` y `WhatsApp Cloud API`) aplica un timeout máximo de **5 segundos** (`urllib.request`), y `Gmail SMTP` un timeout de **10 segundos**. |
| **RNF-03** | **Tolerancia a Fallos** | Aislamiento entre Canales Externos | Un fallo, timeout o falta de configuración en cualquier servicio externo nunca impide guardar la alerta ni interrumpe el envío por los demás canales; el motivo se guarda en `detalle_error`. |
| **RNF-04** | **Seguridad** | Protección de Credenciales en `.env` | Tokens y contraseñas externas se leen únicamente desde `.env` (excluido en `.gitignore`) y jamás se escriben en código fuente, base de datos, mensajes de error ni logs. |
| **RNF-05** | **Seguridad** | Cifrado Bcrypt, CSRF y Escape de Contenido | Contraseñas cifradas con `bcrypt`; validación obligatoria de tokens CSRF en formularios POST y endpoints de sesión; escape estricto (`html.escape` y autoescape de Django) en todos los mensajes dinámicos. |
| **RNF-06** | **Disponibilidad e Integridad** | Persistencia Relacional e Historial Sin Pérdida | El motor PostgreSQL 18 garantiza integridad referencial real mediante llaves foráneas con `ON DELETE SET NULL` y `placa_historica` en `lecturas`, `alertas` y `registro_auditoria`, conservando todo el historial cuando se eliminan vehículos o administradores. |
| **RNF-07** | **Mantenibilidad** | Arquitectura Limpia GoF y Pruebas Aisladas | La lógica se desacopla mediante Strategy, Factory, Observer y Singleton; las pruebas automatizadas (`manage.py test`) simulan todos los servicios externos sin realizar llamadas reales en local ni en CI. |
| **RNF-08** | **Portabilidad** | Despliegue Multi-Entorno | La aplicación puede ejecutarse en Windows (PowerShell), Linux o contenedores Docker sin modificar el código fuente ni añadir librerías externas para el consumo HTTP. |
