# Dianle Coffee — Caso de negocio y requerimientos

**Equipo:** Dianle · Samsung Innovation Campus · Capstone Project  
**Fecha de revisión:** 24/11/2026  
**Alcance:** MVP de inteligencia competitiva para café envasado.

## 1. Contexto y necesidad

Diana dirige una comercializadora multicanal que evalúa incorporar café a su catálogo. La ficha simulada del curso (cronograma de alumnos, hoja Resumen) plantea que su equipo comercial dedica tiempo a relevar precios manualmente, incurre en errores y conoce tarde cambios de la competencia. Necesita decidir qué productos investigar e incorporar, a qué precio posicionarlos y qué estrategias promocionales considerar.

| Indicador de la ficha | Valor de referencia |
|---|---:|
| Integrantes del equipo comercial | 3 |
| Relevamiento manual semanal | 12 horas |
| Costo de trabajo | USD 8/h |
| Errores de carga | 10% |
| NPS inicial | 22 |
| Meta de ventas del nuevo rubro | USD 15.000/mes |
| Presupuesto máximo inicial | USD 2.500 |
| Presupuesto operativo máximo | USD 150/mes |

Estos valores pertenecen al escenario académico y requieren validación. No son resultados medidos por Dianle Coffee. El proyecto no atribuye la meta de ventas a la herramienta ni promete una mejora de NPS.

## 2. Mercado y propuesta de valor

- Rubro: comercialización de café envasado.
- Temática: inteligencia competitiva.
- Cliente: comercializadora multicanal; usuarios: responsables comerciales y analistas.
- Mercado de interés: Argentina, con foco inicial en Buenos Aires. Cobertura demostrada: supermercados de AMBA, sin posibilidad de aislar CABA en la fuente agregada.
- Problema: convertir información comercial dispersa en referencias comparables y acciones de investigación.
- Solución: sistema de soporte a decisiones que reúne datos, facilita comparaciones y proporciona estimaciones de precio de referencia y simulaciones de escenarios.

**Objetivo general:** reducir la incertidumbre y el trabajo manual al evaluar alternativas de catálogo y posicionamiento de precios.

**Objetivos específicos:** normalizar observaciones; describir oferta, marcas, comercios y promociones disponibles; detectar diferencias de precio; evaluar presentaciones con comparables y regresión; calcular escenarios a partir de costos aportados por el usuario; automatizar el intercambio de datos y conservar trazabilidad.

La herramienta complementa el criterio del responsable comercial. No sustituye la investigación de demanda, costos, logística ni la validación de una decisión de inversión.

## 3. Alcance del servicio

| Producto | Funcionalidades |
|---|---|
| Analytics — Explorar mercado | Adquisición, ETL, EDA, filtros, indicadores, análisis de precios y promociones, comparador, matriz de oportunidades, insights y descarga CSV. |
| Inference — Evaluar producto | Estimación de precio de lista, comparables, brecha de posicionamiento, suficiencia de evidencia, recomendaciones, simulación comercial con supuestos explícitos y exportación JSON. |
| Entrega técnica | Aplicación Streamlit, un Actor con operaciones analytics/inference, API documentada y flujo batch mediante Make y Drive. |

Incluye café molido, en grano, instantáneo y cápsulas. Se excluyen accesorios, cafeteras, bebidas listas y productos que no puedan clasificarse dentro del alcance. Las unidades de comparación son ARS/kg para molido y grano, ARS/100 g para instantáneo y ARS/cápsula para cápsulas.

No incluye predicción de ventas, pronóstico temporal sin histórico, rentabilidad garantizada, ejecución de compras, alertas en tiempo real, ni análisis de opiniones ausentes del dataset. La comparación multicanal queda como ampliación condicionada a fuentes autorizadas. El simulador sí calcula margen y resultados bajo supuestos del usuario, sin predecir demanda ni beneficio real futuro.

La actualización es por lotes. Debe validarse con el docente su equivalencia respecto del objetivo de monitoreo automatizado/en tiempo real de la guía inicial.

## 4. Procesos y actores

**AS-IS (reconstrucción propuesta a partir de la ficha):** definir productos a relevar → consultar fuentes → registrar precios → ajustar unidades → comparar → analizar → decidir. Riesgos: duplicación de trabajo, errores manuales, referencias de fechas distintas y falta de cobertura.

**TO-BE (flujo previsto):** obtener lote autorizado → registrar procedencia → validar y normalizar → generar Analytics → entrenar/evaluar modelo fuera del Actor → utilizar Inference con nuevas consultas → comparar y simular → revisar evidencia → decisión humana. Make orquesta el intercambio de entradas y resultados con Drive y Apify. La integración externa aún debe probarse.

| Actor | Responsabilidad |
|---|---|
| Diana / equipo comercial | Validar necesidades, costos aportados y decisiones comerciales. |
| Business Analyst | Definir alcance, requerimientos, criterios de éxito, presupuesto, ROI y comunicación. |
| Data Science Analyst | Calidad de datos, EDA, evaluación del modelo y hallazgos. |
| Solution Engineer | Implementación, automatización, pruebas y demo. |
| Docente | Supervisión académica, validación de criterios y enlace con cliente. |

Los nombres de integrantes, actas, acuerdos y pedidos adicionales se incorporarán a partir de registros reales.

## 5. Benchmark y mapa de competencia

Se distinguen dos niveles: vendedores y marcas de café que Diana necesita analizar, y herramientas que podrían sustituir parte del trabajo de Dianle.

| Alternativa de relevamiento | Función | Diferencia de la propuesta |
|---|---|---|
| [SEPA / Precios Claros](https://www.argentina.gob.ar/economia/industria-y-comercio/defensadelconsumidor/precios-sepa) | Consulta y fuente de precios minoristas. | Dianle delimita el rubro y organiza comparaciones por formato y unidad. |
| [superprecios-claros](https://github.com/hysmarcos/superprecios-claros) | Fuente derivada de precios agregados por cadena y región. | Dianle añade ETL, indicadores, estimación y evaluación de escenarios. |
| [Mercado Libre Argentina](https://www.mercadolibre.com.ar/) | Exploración de oferta del marketplace. | Canal potencial complementario, no integrado ni incluido en los resultados actuales. |
| Relevamiento manual | Consultas y análisis realizados por el equipo comercial. | Dianle busca reducir tareas repetitivas, conservando control humano. |

El lote documentado contiene 82 productos, 27 marcas y 9 comercios. La identificación y clasificación nominal de los principales competidores deberá extraerse del dashboard con el lote real, indicando el criterio de ranking. No se infiere participación de mercado a partir de frecuencia de observaciones. El benchmark compara enfoques, no certifica una auditoría exhaustiva de las funcionalidades de cada proveedor.

## 6. Requerimientos funcionales y criterios de aceptación

| ID | Requerimiento funcional | Criterio de aceptación propuesto |
|---|---|---|
| RF01 | Adquirir y registrar datos reales. | El lote conserva fuente, fecha, región, identificadores y manifiesto verificable. |
| RF02 | Validar, limpiar y normalizar. | Entradas = salidas + exclusiones; faltantes y unidades incompatibles se tratan explícitamente. |
| RF03 | Explorar indicadores y filtrar. | Los conteos, gráficos y tablas responden al filtro y muestran unidades y contexto. |
| RF04 | Comparar 2–4 productos compatibles. | Se muestran referencias unitarias, diferencias porcentuales y detalle disponible por comercio/promoción. |
| RF05 | Detectar señales comerciales. | La matriz y los insights se calculan con datos observados y distinguen limitaciones. |
| RF06 | Estimar un precio de referencia. | Una consulta válida devuelve estimación, modelo y advertencias sin volver a entrenar. |
| RF07 | Evaluar posicionamiento y evidencia. | La respuesta muestra brecha, comparables disponibles y advertencias de soporte, fecha y error. |
| RF08 | Simular escenarios. | Con precio positivo, costo válido y margen objetivo válido se calculan resultados y precio necesario; valores inválidos se rechazan. |
| RF09 | Exportar resultados. | Analytics permite descargar el filtro en CSV; Inference exporta evaluación JSON. |
| RF10 | Ejecutar ambas operaciones por API. | Un Actor acepta la operación solicitada y devuelve registros y documentación recuperable. |
| RF11 | Automatizar el intercambio. | Make recibe entradas, invoca el Actor y guarda las salidas verificadas en Drive. |

RF10 y RF11 requieren pruebas externas. Los criterios son verificaciones propuestas, no constancias de aceptación del cliente.

## 7. Requerimientos no funcionales

| ID | Requerimiento | Verificación |
|---|---|---|
| RNF01 | Reproducibilidad con Python 3.13 y dependencias fijadas. | Preparación y pruebas desde una copia limpia; Windows pendiente. |
| RNF02 | Demo local independiente de red con artefactos previos. | Abrir ambas vistas con lote y modelo persistidos y sin acceso externo. |
| RNF03 | Trazabilidad e integridad. | Verificar SHA-256, procedencia, fecha y asociación modelo/dataset. |
| RNF04 | Lotes acotados. | Contrato de hasta 2.500 filas y 1 MB; verificar límites efectivos de nube. |
| RNF05 | Seguridad y privacidad. | No versionar credenciales, datos restringidos ni modelos no autorizados; accesos privados durante pruebas. |
| RNF06 | Usabilidad y claridad. | Interfaz en español, unidades visibles, errores comprensibles y advertencias. |
| RNF07 | Consistencia. | Comparar resultados locales y remotos para las mismas entradas y versión. |

## 8. Hipótesis y métricas de éxito

| Hipótesis / KPI | Línea base | Meta propuesta / método |
|---|---|---|
| Tiempo manual semanal | 12 h, ficha | 3 h o menos; medir tareas equivalentes con y sin solución. |
| Errores manuales | 10%, ficha | Reducirlos; acordar umbral y auditar una muestra comparable. |
| Calidad del lote | No medida por cliente | Conciliación de conteos y reporte de faltantes. |
| Utilidad de estimación | Mediana como baseline | Mejorar MAE en test separado por grupo de producto; revisar error por formato. |
| Costos mensuales | Límite USD 150 | Medir Apify/Make, alojamiento y mantenimiento para una frecuencia declarada. |
| Valor comercial | Sin medición | Diana debe poder justificar alternativas de catálogo y precio con evidencia. |

La hipótesis de reducción de 12 a 3 horas equivale a 75% de reducción y USD 288/mes de valor bruto del tiempo liberado, usando cuatro semanas y USD 8/h. No constituye ahorro observado ni necesariamente reducción de gasto salarial. Presupuesto y ROI se desarrollan en COSTOS_ROI.md.

## 9. Evidencia disponible y limitaciones

El lote reportado del 15/11/2026 contiene 286 observaciones, de las cuales 250 tienen unidad comparable. Representa precios agregados por producto y cadena/región, de un solo día y canal. El modelo Ridge fue seleccionado por validación y reporta MAE de ARS 6.632,27 frente a ARS 8.963,36 de la mediana en test separado por producto. No equivale a una precisión porcentual ni demuestra rentabilidad. Consultar INSIGHTS.md y METRICAS.md.

La versión dc1e363 documenta 20 pruebas aprobadas y verificación local en Linux. La comprobación independiente en Windows, build y corridas privadas de Apify y ejecución Make/Drive siguen pendientes. El GET de documentación se realiza mediante un registro de almacenamiento del Actor y debe verificarse externamente.

## 10. Riesgos, backlog y cierre

| Prioridad | Riesgo / tarea de cierre | Mitigación |
|---|---|---|
| P0 | Datos y modelo no versionados | Recuperar lote autorizado o regenerarlo, validar manifiesto y modelo. |
| P0 | Integración externa no demostrada | Probar Windows, Apify y Make/Drive con autorización; guardar resultados y costos. |
| P0 | Cobertura temporal y geográfica limitada | Explicitar límites, confirmar alcance batch con docente. |
| P0 | Publicación y permisos | Revisar licencias, datos, materiales, credenciales y preparar distribución limpia. |
| P0 | Entrega comercial | Completar costo por corrida, precio, margen, ROI, pitch y video. |
| P1 | Error de regresión y poca cobertura en grano | Mostrar comparables, advertencias y evitar recomendaciones concluyentes. |
| P1 | Cambios en la fuente | Validar esquema, fecha y región; conservar lote previo autorizado. |
| P1 | Gestión del cliente | Recuperar reunión del 05/11, pedidos del 12/11 y feedback real; no retrofechar registros. |
| P2 | Histórico, opiniones y nuevos canales | Ampliación futura, fuera del cierre inmediato. |

## 11. Fuentes y documentos relacionados

- Guía para Estudiantes del Capstone, pp. 1–8: objetivo, roles, gestión y entregables.
- Capstone Project — Clases 42 a 47, láminas 10–15: arquitectura, Analytics, Inference, comercialización, benchmark e impacto.
- Cronograma de alumnos, hoja Resumen: ficha simulada del cliente (valores reproducidos en la especificación interna, sujetos a validación).
- [Reporte de insights](INSIGHTS.md) · [Costos y ROI](COSTOS_ROI.md) · [Diccionario de datos](DICCIONARIO_DATOS.md) · [Trazabilidad](TRAZABILIDAD.md) · [Guía de integración](../INTEGRACION_PASO_A_PASO.md).

Este documento distingue diseño, resultados reportados y verificaciones pendientes. La entrega debe actualizar las evidencias y decisiones con información efectivamente comprobada.
