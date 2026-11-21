---
name: "Historia de Usuario (User Story / PBI)"
about: "Propone una necesidad de usuario o valor para el Product Backlog de AutoSen"
title: "US: [Título breve de la necesidad]"
labels: ["user-story", "pbi"]
assignees: ""
---

### Contexto de la Historia de Usuario
**COMO** [rol del usuario: conductor, técnico de soporte, superadmin, administrador de taller]  
**QUIERO** [acción o capacidad técnica que desea realizar en la aplicación]  
**PARA** [beneficio o valor que aporta al usuario o al negocio]  

---

### Criterios de Aceptación (Acceptance Criteria)
Condiciones comprobables que deben cumplirse para dar por aceptado este elemento:
- [ ] **Escenario 1:** Dado que [contexto inicial], cuando [evento/acción], entonces [resultado esperado].
- [ ] **Escenario 2:** Si los datos ingresados son incompletos o inválidos, se informa claramente en pantalla sin romper la interfaz.
- [ ] **Escenario 3:** La funcionalidad se integra correctamente con los módulos existentes de telemetría y auditoría.

---

### Prioridad y Estimación
* **Prioridad:** [Alta / Media / Baja]
* **Módulo Afectado:** [Web Cliente / Telemetría OBD2 / Alertas Multicanal / Panel Admin / Auditoría / Reportes]
* **Sprint Sugerido:** [Sprint 1 / Sprint 2]

---

### Tareas Técnicas Asociadas (Plan de los Developers)
- [ ] Diseñar / actualizar modelo de datos o migración
- [ ] Implementar vista / controlador y rutas URL
- [ ] Crear / adaptar plantilla HTML con soporte de tema claro/oscuro
- [ ] Escribir pruebas unitarias e integración en `tests/`
