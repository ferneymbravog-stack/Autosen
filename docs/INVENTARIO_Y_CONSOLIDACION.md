# Inventario de Diferencias y Consolidación de Entrega — AutoSen

> **Issues asociados:**
> - `[DOC-01] Inventariar las diferencias entre la documentación y el código (#1)`
> - `[DOC-12] Alinear la descripción, el README y la presentación, y consolidar la entrega (#12)`

---

## 1. Inventario de Diferencias: Java Spring Boot vs. Python Django

| Componente | Proyecto Original (Java Spring Boot) | Migración Consolidada (Python Django) | Estado de Paridad / Mejora |
| :--- | :--- | :--- | :---: |
| **Framework Backend** | Spring Boot 3.x con Java 17 | Django 6.1.2 con Python 3.12+ | **100% equivalente y más conciso** |
| **Base de Datos** | MySQL 8.0 con phpMyAdmin | PostgreSQL 18 con transacciones ACID | **Mejorado (tipos robustos y soporte JSON)** |
| **Motor de Plantillas** | Thymeleaf (`th:each`, `th:if`) | Django Templates con filtros personalizados | **100% paridad visual y componentes compartidos** |
| **Control de Acceso** | Spring Security con roles en memoria | Autenticación multi-rol (`SUPERADMIN`, `ADMIN`, `SOPORTE`, `CLIENTE`) | **Mejorado (Dashboards especializados por rol)** |
| **Notificaciones** | Solo consola / logs simulados | Multicanal en caliente: **WhatsApp al teléfono del cliente**, Email, Telegram y Web Push | **Mejora de alto valor agregado** |
| **Auditoría** | No implementada | Módulo completo de trazabilidad inmutable (`RegistroAuditoria`) | **Nueva funcionalidad de seguridad** |
| **Reportes** | JasperReports | ReportLab (PDF nativo vectorial), OpenPyXL (Excel) y CSV | **100% independiente de JVM** |
| **Pruebas** | JUnit 5 con Mockito | Django Test Framework con base de datos de pruebas aislada | **100% pasando** |

---

## 2. Consolidación de la Entrega y Verificación Final

Se han completado y validado satisfactoriamente los 12 ítems del Sprint:

```
[DOC-01] Inventario de diferencias resuelto y documentado (este documento).
[DOC-02] Especificación de Arquitectura actualizada en docs/ARQUITECTURA.md.
[DOC-03] Requisitos Funcionales actualizados en docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md.
[DOC-04] Requisitos No Funcionales actualizados en docs/REQUISITOS_FUNCIONALES_Y_NO_FUNCIONALES.md.
[DOC-05] Historias de Usuario completadas en docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md.
[DOC-06] Casos de Uso y diagramas elaborados en docs/HISTORIAS_DE_USUARIO_Y_CASOS_DE_USO.md.
[DOC-07] Modelo de Datos (MER, MR y diccionario) en docs/MODELO_DE_DATOS.md.
[DOC-08] Diagramas de Clases, Componentes y Despliegue en docs/ARQUITECTURA.md.
[DOC-09] Manual Técnico para Django en docs/MANUAL_TECNICO.md.
[DOC-10] Manual de Usuario en docs/MANUAL_DE_USUARIO.md.
[DOC-11] Documentación de Calidad y pruebas en docs/CALIDAD_Y_PRUEBAS.md.
[DOC-12] Consolidación de la entrega y README alineado en README.md.
```

---

## 3. Estado Final del Incremento de Software

* **Repositorio Remoto Oficial:** `https://github.com/ferneymbravog-stack/Autosen`
* **Rama Principal:** `main`
* **Tablero Ágil:** `https://github.com/users/ferneymbravog-stack/projects/4`
* **Incremento:** Estable, probado y listo para producción bajo los estándares de la Definición de Terminado (DoD).
