"""
Script automatizado para crear todas las Issues oficiales en el repositorio de GitHub:
https://github.com/ferneymbravog-stack/Autosen

Uso:
  python scripts/crear_issues_github.py TU_TOKEN_DE_GITHUB
o:
  $env:GITHUB_TOKEN="tu_token"; python scripts/crear_issues_github.py
"""
import os
import sys
import json
import urllib.request
import urllib.error

REPO = "ferneymbravog-stack/Autosen"
API_URL = f"https://api.github.com/repos/{REPO}/issues"

ISSUES = [
    {
        "title": "[DOC-01] Inventariar las diferencias entre la documentación y el código",
        "body": "Revisar y documentar todas las diferencias y mejoras resultantes de la migración del proyecto original en Java Spring Boot a Python Django + PostgreSQL.\n\n### Criterios de Aceptación:\n- [x] Comparar modelos, rutas y controladores entre Java y Django.\n- [x] Registrar la paridad de funcionalidades y las mejoras añadidas (WhatsApp, WebPush, Auditoría).\n- [x] Documentado formalmente en `docs/INVENTARIO_Y_CONSOLIDACION.md`.",
        "labels": ["documentation", "sprint-1", "consolidacion"],
    },
    {
        "title": "[DOC-02] Actualizar el Documento de Especificación de Arquitectura",
        "body": "Definir la arquitectura modular MVT en Django, la capa de persistencia en PostgreSQL 18 y la integración de patrones de diseño GoF.\n\n### Criterios de Aceptación:\n- [x] Especificar arquitectura en capas: Web, Panel, Core, API y Reportes.\n- [x] Detallar patrones GoF: Strategy, Observer, Factory y Singleton.\n- [x] Documentado formalmente en `docs/ARQUITECTURA.md`.",
        "labels": ["architecture", "documentation"],
    },
    {
        "title": "[DOC-03] Actualizar los requisitos funcionales (RQF)",
        "body": "Formalizar los requisitos funcionales del sistema AutoSen para telemetría OBD2, roles, alertas y auditoría.\n\n### Criterios de Aceptación:\n- [x] Redactar RQF-01 a RQF-15 con descripción y prioridad.\n- [x] Incluir el nuevo flujo de registro con teléfono/WhatsApp y despacho multicanal.\n- [x] Documentado formalmente en `docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`.",
        "labels": ["requirements", "documentation"],
    },
    {
        "title": "[DOC-04] Actualizar los requisitos no funcionales (RNF)",
        "body": "Definir los atributos de calidad, rendimiento, seguridad, concurrencia y tolerancia a fallos del sistema.\n\n### Criterios de Aceptación:\n- [x] Especificar RNF-01 a RNF-08 (tiempos de respuesta <200ms, bcrypt, CSRF, ACID).\n- [x] Documentado formalmente en `docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md`.",
        "labels": ["requirements", "security", "performance"],
    },
    {
        "title": "[DOC-05] Actualizar y completar las historias de usuario",
        "body": "Estructurar las historias de usuario oficiales en formato estándar ('Como... quiero... para...') con criterios de aceptación.\n\n### Criterios de Aceptación:\n- [x] HU-01: Auto-registro con Teléfono y WhatsApp.\n- [x] HU-02: Diagnóstico Operativo para Soporte Técnico.\n- [x] HU-03: Auditoría y Control para SuperAdmin.\n- [x] HU-04: Despacho Multicanal de Alertas Críticas.\n- [x] Documentado formalmente en `docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md`.",
        "labels": ["user-story", "scrum"],
    },
    {
        "title": "[DOC-06] Actualizar los casos de uso y sus diagramas",
        "body": "Elaborar el diagrama general de casos de uso del sistema integrando los actores: Cliente, Administrador, SuperAdmin, Soporte y App Android.\n\n### Criterios de Aceptación:\n- [x] Incluir CU-01 al CU-10 con relaciones y actores.\n- [x] Generar diagrama interactivo en Mermaid.\n- [x] Documentado formalmente en `docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md`.",
        "labels": ["use-cases", "diagrams"],
    },
    {
        "title": "[DOC-07] Actualizar el modelo de datos (MER, MR, diccionario y scripts SQL)",
        "body": "Actualizar el Modelo Entidad-Relación y el Modelo Relacional para PostgreSQL 18, incluyendo las tablas de notificaciones, auditoría y teléfono del cliente.\n\n### Criterios de Aceptación:\n- [x] Diagrama Mermaid ER de todas las entidades.\n- [x] Diccionario de datos completo con tipos de datos, llaves foráneas y restricciones.\n- [x] Documentado formalmente en `docs/MODELO_DE_DATOS.md`.",
        "labels": ["database", "postgresql"],
    },
    {
        "title": "[DOC-08] Rehacer los diagramas de clases, paquetes, componentes y despliegue",
        "body": "Rehacer los diagramas UML para representar la estructura modular de Django, el flujo OBD2 Bluetooth y la infraestructura de despliegue.\n\n### Criterios de Aceptación:\n- [x] Diagrama de Paquetes y Módulos.\n- [x] Diagrama de Clases del Dominio.\n- [x] Diagrama de Despliegue Físico.\n- [x] Documentado formalmente en `docs/ARQUITECTURA.md`.",
        "labels": ["uml", "diagrams"],
    },
    {
        "title": "[DOC-09] Reescribir el Manual Técnico para Django",
        "body": "Elaborar el manual técnico integral explicando configuración de variables de entorno, endpoints de API REST, migración de base de datos y comandos de despliegue.\n\n### Criterios de Aceptación:\n- [x] Stack tecnológico y dependencias.\n- [x] Tabla de endpoints `/api/` y parámetros de entrada.\n- [x] Comandos de gestión y pruebas.\n- [x] Documentado formalmente en `docs/MANUAL_TECNICO.md`.",
        "labels": ["technical-manual", "django"],
    },
    {
        "title": "[DOC-10] Actualizar el Manual de Usuario",
        "body": "Redactar el manual de usuario con guías operativas paso a paso para cada uno de los 4 perfiles del sistema.\n\n### Criterios de Aceptación:\n- [x] Guía del Cliente: registro con WhatsApp, gestión vehicular y lecturas.\n- [x] Guía de Soporte Técnico: centro de diagnóstico, Web Push y calibración.\n- [x] Guía de Administrador y SuperAdmin: gestión de equipo y auditoría.\n- [x] Documentado formalmente en `docs/MANUAL_DE_USUARIO.md`.",
        "labels": ["user-manual"],
    },
    {
        "title": "[DOC-11] Actualizar la Documentación de Calidad (Ítem 8)",
        "body": "Documentar la estrategia de calidad, cobertura de pruebas unitarias automatizadas y el pipeline de Integración Continua con GitHub Actions.\n\n### Criterios de Aceptación:\n- [x] Tabla de suites de prueba por módulo.\n- [x] Configuración de GitHub Actions con PostgreSQL (`.github/workflows/django-tests.yml`).\n- [x] Matriz de cumplimiento de la Definición de Terminado (DoD).\n- [x] Documentado formalmente en `docs/CALIDAD_Y_PRUEBAS.md`.",
        "labels": ["qa", "testing", "ci-cd"],
    },
    {
        "title": "[DOC-12] Alinear la descripción, el README y la presentación, y consolidar la entrega",
        "body": "Alinear el README.md principal del repositorio incorporando la metodología Scrum, Product Goal, Sprint Backlog y enlaces a todos los documentos generados.\n\n### Criterios de Aceptación:\n- [x] Actualizar `README.md` con metodología Scrum y tabla de issues.\n- [x] Verificar enlaces e índices a documentos técnicos.\n- [x] Documentado formalmente en `docs/INVENTARIO_Y_CONSOLIDACION.md` y `README.md`.",
        "labels": ["readme", "delivery"],
    },
    {
        "title": "[FEAT-01] Integrar API REST de telemetría OBD2 y códigos DTC de falla",
        "body": "Integrar el servicio REST de telemetría vehicular para recepción de tramas desde escáneres ELM327 Bluetooth y agregar catálogo de códigos de diagnóstico DTC estándar (P0100 a P0500).\n\n### Criterios de Aceptación:\n- [x] Endpoint `/api/obd2/actualizar` procesa niveles y valores en tiempo real.\n- [x] Helper `diagnostico_dtc` interpreta códigos de falla automotriz en español.\n- [x] Implementado en `api/obd2.py`.",
        "labels": ["feature", "obd2", "api"],
    },
    {
        "title": "[FEAT-02] Control de acceso granular y decoradores de seguridad por rol",
        "body": "Implementar decoradores de seguridad en Django para restringir vistas según los roles `SUPERADMIN`, `ADMIN` y `SOPORTE`.\n\n### Criterios de Aceptación:\n- [x] `@superadmin_requerido` restringe creación de administradores y auditoría.\n- [x] `@gestion_admin_requerido` previene acciones destructivas por parte de técnicos.\n- [x] `@soporte_requerido` garantiza acceso técnico a calibración y diagnóstico.\n- [x] Implementado en `core/auth.py`.",
        "labels": ["feature", "auth", "security"],
    },
    {
        "title": "[FEAT-03] Despacho multicanal de alertas con enlace directo a WhatsApp Web",
        "body": "Despachar automáticamente alertas críticas a Email, WhatsApp (al número del cliente), Telegram y Web Push, incluyendo enlaces directos click-to-chat.\n\n### Criterios de Aceptación:\n- [x] WhatsApp extrae dinámicamente `cliente.telefono` y genera el enlace prellenado.\n- [x] Si el cliente no tiene teléfono, omite WhatsApp sin generar errores.\n- [x] Bandeja `/admin/notificaciones` incluye botón *'Abrir chat WhatsApp →'*.\n- [x] Implementado en `core/notificaciones.py` y `templates/admin/notificaciones.html`.",
        "labels": ["feature", "notifications", "whatsapp"],
    },
    {
        "title": "[FEAT-04] Sistema de auditoría inmutable de operaciones y eventos de autenticación",
        "body": "Registrar en la base de datos cada operación de alta, baja, modificación, bloqueo y autenticación con fecha, hora, usuario e IP.\n\n### Criterios de Aceptación:\n- [x] Registro automático mediante `registrar_auditoria` y `auditar_autenticacion`.\n- [x] Vista `/admin/auditoria` exclusiva para SuperAdmin con tabla inmutable.\n- [x] Implementado en `core/auditoria.py` y `templates/admin/auditoria.html`.",
        "labels": ["feature", "audit", "security"],
    },
    {
        "title": "[FEAT-05] Generador de reportes técnicos avanzados con exportación PDF/Excel/CSV",
        "body": "Permitir a administradores filtrar telemetría por fechas y clientes, y descargar informes técnicos vectoriales listos para imprimir.\n\n### Criterios de Aceptación:\n- [x] Exportador PDF vectorial con ReportLab (`/reportes/exportar/pdf`).\n- [x] Exportador Excel con OpenPyXL y CSV con codificación UTF-8 BOM.\n- [x] Implementado en `reportes/exportar.py` y `reportes/views.py`.",
        "labels": ["feature", "reports", "pdf"],
    },
    {
        "title": "[FEAT-06] Portal de usuario con auto-registro de teléfono y switch de tema",
        "body": "Ofrecer a los clientes una interfaz moderna con captura de teléfono/WhatsApp en `/register`, dashboard personal y alternador de tema claro/oscuro.\n\n### Criterios de Aceptación:\n- [x] Formulario de registro captura nombre, apellido, teléfono, correo y clave.\n- [x] Preserva valores ante errores de validación sin borrar lo escrito.\n- [x] Alternador de tema persistente en localStorage.\n- [x] Implementado en `templates/paginas/register.html` y `static/js/theme-toggle.js`.",
        "labels": ["feature", "ui", "theme"],
    },
    {
        "title": "[PERF-01] Optimización de consultas ORM de sensores y pool de conexiones PostgreSQL",
        "body": "Optimizar el tiempo de respuesta de las consultas del dashboard mediante índices, `select_related` y consultas agregadas en PostgreSQL.\n\n### Criterios de Aceptación:\n- [x] Dashboard carga conteos agregados de sensores en una única consulta.\n- [x] Índices creados en columnas de búsqueda frecuente (`placa`, `correo`, `tipo_sensor`).\n- [x] Implementado en `panel/views.py` y `core/models.py`.",
        "labels": ["performance", "orm", "database"],
    },
    {
        "title": "[SEC-01] Endurecimiento de seguridad: protección CSRF y contraseñas cifradas con bcrypt",
        "body": "Garantizar el almacenamiento seguro de credenciales con factor de coste de trabajo bcrypt y protección estricta contra falsificación de peticiones en sitios cruzados.\n\n### Criterios de Aceptación:\n- [x] Hashes de contraseña con prefijo `$2a$` y costo 10 compatibles con Spring Boot.\n- [x] Validación obligatoria de tokens CSRF en todos los formularios web.\n- [x] Implementado en `core/auth.py` y `autosen/settings.py`.",
        "labels": ["security", "hardening"],
    },
]


def crear_issue(token, issue):
    data = json.dumps(issue).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "AutoSen-Issue-Creator")

    try:
        with urllib.request.urlopen(req) as resp:
            resultado = json.loads(resp.read().decode("utf-8"))
            print(f"✅ Creada: #{resultado['number']} - {resultado['title']}")
            return resultado
    except urllib.error.HTTPError as err:
        print(f"❌ Error al crear '{issue['title']}': HTTP {err.code} - {err.read().decode('utf-8')}")
        return None


def main():
    token = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        print("Error: Debes proporcionar un GitHub Personal Access Token.")
        print("Ejemplo: python scripts/crear_issues_github.py ghp_tu_token_aqui")
        sys.exit(1)

    print(f"Iniciando creación de {len(ISSUES)} issues en {REPO}...")
    for item in ISSUES:
        crear_issue(token, item)
    print("\n¡Proceso de creación de issues finalizado!")


if __name__ == "__main__":
    main()
