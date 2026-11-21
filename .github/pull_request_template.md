## Resumen del Cambio
Descripción clara del cambio introducido, funcionalidad agregada o problema resuelto.

## Tipo de Cambio
- [ ] Nueva funcionalidad (`feat`)
- [ ] Corrección de error (`fix`)
- [ ] Pruebas unitarias o de integración (`test`)
- [ ] Documentación técnica (`docs`)
- [ ] Refactorización sin cambio funcional (`refactor`)

## Referencia a Issues del Product Backlog
- Referencia de seguimiento: `Refs #` [Número del Issue]
- Cierre automático al fusionar: `Closes #` [Número del Issue]

---

## Comprobaciones Realizadas (Evidencia)
- [ ] Pruebas unitarias ejecutadas localmente con resultado exitoso: `python manage.py test`
- [ ] Verificación en navegador en modo claro y oscuro
- [ ] Verificación de consultas e inserciones en base de datos PostgreSQL

---

## Lista de Verificación de la Definición de Terminado (DoD)
Antes de solicitar la aprobación de este PR, confirma el cumplimiento de la DoD:
- [ ] La aplicación inicia limpiamente (`python manage.py runserver`)
- [ ] Las migraciones se aplican sin errores (`python manage.py migrate`)
- [ ] La funcionalidad cumple todos sus Criterios de Aceptación
- [ ] No se suben archivos sensibles (`.env`, contraseñas, tokens de API)
- [ ] El código sigue las convenciones del proyecto y la arquitectura GoF
- [ ] La documentación del repositorio está actualizada
