# Trazabilidad

| Requisito | Material | Evidencia y alcance |
| --- | --- | --- |
| Adquisición y procedencia | Guía estudiantes pp. 2–4, clases 42–47 pp. 10–11 | 286 observaciones reales, CSV y manifiesto con fecha y hash; rama de adquisición del Actor probada localmente con 50 observaciones. |
| ETL, EDA y decisiones | Primera entrega y clase 42–47 p. 10 | Calidad, distribución, IQR, precio por unidad, comparables, cobertura, señales y dos vistas verificadas localmente. |
| Modelo y selección | Entregas posteriores y clase 42–47 pp. 10–11 | Cinco candidatos y mediana evaluados por grupos de producto. Ridge seleccionado por validación. Resultados y límites en INSIGHTS. |
| Un Actor y dos operaciones | Clases 42–47 pp. 10–12 | SDK local, esquema, Dockerfile, contrato y archivos reales de control. Build y prueba en Apify pendientes. |
| GET / POST | Clases 42–47 p. 12 | POST de ejecución y registro JSON DOCUMENTACION publicado por el SDK. GET nativo autenticado del Key-Value Store tras la primera corrida autorizada. Pendiente verificar el GET externo. |
| Apify, Make y Drive | Guía estudiantes pp. 2–4 | Guía de integración preparada. Requiere cuentas, saldo, permisos de transferencia y pruebas externas. |
| Dashboard, reporte, pitch y video | Guía estudiantes p. 8 | Dashboard, informe, guion y defensa preparados. Grabación y enlace de portafolio pendientes. |
| Costo y propuesta comercial | Clases 42–47 pp. 11–12 | Plantilla de medición y escenarios en COSTOS_ROI. Faltan CU, tiempo de intervención y costo reales. |
| Store y portafolio | Clases 42–47 / guía | Dependen de evidencia y autorización de publicación. |

La ausencia de Mercado Libre impide contrastar canales. El lote SEPA derivado tiene granularidad de cadena/región y se reporta como AMBA. Los materiales originales siguen en el checkout privado.

## Cierre de producto

| Requisito | Implementación y evidencia |
| --- | --- |
| Comparador 2–4 productos | Selector del segmento filtrado, brecha frente al primer producto, detalle por comercio y promociones. AppTest compara productos reales. |
| Oportunidades e insights | Matriz por segmento con cobertura, precios, brechas, promociones, antigüedad y evidencia. El resultado se comparte con Analytics del Actor. |
| Suficiencia y recomendaciones | Suficiente, limitada o insuficiente según cobertura, antigüedad y, para el modelo, error y soporte. Se conserva el carácter descriptivo. |
| Simulación y exportación | Precios, costos y unidades aportados por quien consulta, sin estimar demanda. Margen porcentual, objetivo y precio mínimo. Resultado y evaluación exportables en JSON. El Actor comparte la función de simulación. |
| Windows y distribución | Cinco scripts PowerShell y ZIP de código. Ejecución local verificada en Linux; reproducibilidad en Windows pendiente de ensayo en Windows. |
| Datos y modelo | Originales conservados en el entorno privado. Regeneración y manifiesto con rutas, tamaños y hashes. Redistribución pendiente de comprobar. |
