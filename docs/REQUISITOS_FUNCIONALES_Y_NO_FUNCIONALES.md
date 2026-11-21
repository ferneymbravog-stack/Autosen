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
| **RQF-07** | Alertas | **Despacho Multicanal Inmediato** | Envío automático de notificaciones ante advertencias o fallas a través de Email, Telegram, WhatsApp y Web Push. | Alta |
| **RQF-08** | Alertas | **Notificación Directa a WhatsApp** | El mensaje de WhatsApp se envía directamente al número telefónico registrado por el cliente propietario del vehículo. | Alta |
| **RQF-09** | Alertas | **Notificaciones Web Push en Vivo** | Emisión de alertas emergentes en el navegador con sonido para técnicos en el centro de diagnóstico. | Media |
| **RQF-10** | Administración | **Gestión de Administradores** | Exclusivo para `SUPERADMIN`: creación, modificación de rol y eliminación de cuentas del equipo técnico. | Alta |
| **RQF-11** | Administración | **Bloqueo y Activación de Cuentas** | Los administradores pueden suspender o reactivar el acceso de clientes al sistema. | Media |
| **RQF-12** | Auditoría | **Registro Inmutable de Auditoría** | Registro histórico obligatorio de cada acción crítica (crear, editar, eliminar, bloquear) con fecha, usuario y detalle. | Media |
| **RQF-13** | Reportes | **Filtros Avanzados de Telemetría** | Consulta de registros filtrando por cliente, vehículo, tipo de sensor y rango de fechas. | Media |
| **RQF-14** | Reportes | **Exportación en PDF, Excel y CSV** | Generación de informes descargables listos para impresión con membrete institucional. | Media |
| **RQF-15** | Interfaz | **Soporte de Tema Oscuro y Claro** | Alternador visual persistente en toda la aplicación para comodidad del operador. | Baja |

---

## 2. Requisitos No Funcionales (RNF)

| Código | Categoría | Nombre del Requisito | Criterio de Aceptación / Métrica |
| :---: | :--- | :--- | :--- |
| **RNF-01** | **Rendimiento** | Tiempo de Respuesta | Las peticiones a la API OBD2 deben responder en menos de 200 ms en condiciones normales de red. |
| **RNF-02** | **Seguridad** | Cifrado de Credenciales | Todas las contraseñas se almacenan mediante el algoritmo `bcrypt` con hash irreversible; nunca en texto plano. |
| **RNF-03** | **Seguridad** | Protección CSRF y Sesiones | Las solicitudes POST web validan obligatoriamente tokens CSRF; las sesiones se manejan en backend con cookies seguras. |
| **RNF-04** | **Disponibilidad** | Persistencia Concurrente | El motor relacional PostgreSQL 18 garantiza aislamiento de transacciones (ACID) y soporte multi-conexión. |
| **RNF-05** | **Compatibilidad** | Soporte OBD2 / ELM327 | La API admite payloads JSON de escáneres OBD2 con tolerancia a datos incompletos o valores nulos sin generar excepciones 500. |
| **RNF-06** | **Tolerancia a Fallos** | Resiliencia Multicanal | Si un canal de notificación falla (ej. WhatsApp no tiene número), los canales restantes (Email, Telegram, Push) se despachan sin interrupciones. |
| **RNF-07** | **Mantenibilidad** | Arquitectura Limpia GoF | La lógica de alertas y sensores debe desacoplarse mediante los patrones Strategy, Factory, Observer y Singleton. |
| **RNF-08** | **Portabilidad** | Despliegue Multi-Entorno | La aplicación puede ejecutarse en Windows (PowerShell), Linux o contenedores Docker sin modificar el código fuente. |
