# Cierre de entrega · 24/11/2026
Checklist operativo, no acta de conformidad.

| Entregable | Evidencia | Estado |
|---|---|---|
| Negocio y requerimientos | NEGOCIO.md | Redactado; validar cliente y mapa nominal |
| Analytics | ANALYTICS.md, INSIGHTS.md, dashboard | Reportado local; verificar lote |
| Modelo de decisión | INFERENCE.md, METRICAS.md, scripts/train.py | Reportado local; recuperar métricas completas |
| Propuesta económica | COSTOS_ROI.md | Proyección; medir costos y validar horas |
| API y flujo | ARQUITECTURA.md, guías | Implementación; probar nube |
| Manual | MANUAL_USUARIO.md | Redactado; revisar interfaz |
| Pitch y defensa | PITCH.md, DEFENSA.md, DEMO.md | Guiones; presentación y video reales pendientes |
| Colab | scripts Python reproducibles | Omitido por decisión del equipo; cronograma fila 46 lo menciona, confirmar aceptación equivalente |
| Portafolio | README y repositorio de entrega | Pendiente de autorización y publicación |
| Store | ficha APIFY.md | Pendiente de ejecución, pricing y autorización |

## Verificación final
1. Clonar el repositorio de entrega desde su rama principal (sin parámetros de rama) o extraer el ZIP, recuperar/generar datos y modelo, ejecutar PowerShell y pruebas. Guardar versión, hash, resultados, métricas, capturas.
2. Autorizar build y corrida privada de Analytics, Inference y adquisición. Comparar resultados con misma entrada/build. Registrar GET/POST, CU, duración y costos.
3. Ejecutar Make y Drive, guardar IDs, archivos, créditos, diagrama/capturas sin secretos.
4. Actualizar ROI, precio Store y reporte de insights. Completar nombres, pedidos, feedback y veredicto reales. Revisar presentación y grabar demo.
5. La copia independiente de entrega conserva las rutas del proyecto y se publica en `main`. Revisar que no incluya secretos, datos no autorizados, cachés, entornos virtuales ni materiales de desarrollo. El ZIP descargado desde GitHub incluye los archivos versionados. El lote y el modelo se regeneran o recuperan de una copia autorizada. La documentación registra pruebas, limitaciones y uso de asistencia con IA.
6. Revisar instalación desde copia limpia y enlaces; autorizar publicación y acceso a dashboard/Actor; recoger feedback real.

Referencias: guía estudiantes p.8, clases 42–47 pp.10–15, cronograma alumnos filas 45–53, imagen docente Pipeline de libros de terror (ocho puntos del README).

## Verificación del dashboard integrado

La versión `9a45cc5` superó el workflow Dashboard smoke tests en el repositorio de desarrollo. Al publicar la copia, verificar la nueva ejecución de GitHub Actions, el acceso a Drive, el modelo compatible y las dos vistas en Streamlit. Las pruebas previas no reemplazan esta comprobación.
