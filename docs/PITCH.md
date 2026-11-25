# Presentación ejecutiva — Dianle Coffee
Guion de 2 minutos, adaptable a indicación docente. Excel Cronograma fila 45 indica 6 minutos por grupo + 2 de preguntas; confirmar formato final. Propuesta de 6 diapositivas y demo breve.

| Diapositiva | Contenido visible |
|---|---|
| 1. Dianle Coffee | Inteligencia competitiva para café envasado · equipo Dianle |
| 2. Problema | 12 h/semana relevando precios; 10% errores según ficha; decisiones de catálogo y precio |
| 3. Analytics | 286 observaciones, 82 productos, 27 marcas, 9 comercios; comparador y oportunidades |
| 4. Inference | Ridge, MAE ARS 6.632 vs baseline 8.963; comparables, evidencia, simulador |
| 5. Flujo | SEPA → ETL/EDA → modelo → dashboard; Actor y Make/Drive según evidencia |
| 6. Propuesta | USD 2.223 iniciales; USD 50/mes escenario; 75% reducción objetivo; ROI 22,4% a 12 meses; payback 9,34 meses |

## Discurso
Somos Dianle y desarrollamos Dianle Coffee para ayudar a una comercializadora a evaluar su ingreso al mercado del café envasado. Según la ficha de Diana, su equipo dedica doce horas semanales a buscar precios manualmente. La información dispersa dificulta comparar alternativas de catálogo y posicionamiento.

Nuestro primer producto, Analytics, transforma datos reales en información comercial. En el lote del 15 de noviembre reunimos 286 observaciones de 82 productos, 27 marcas y nueve comercios de AMBA. Normalizamos precios por formato y mostramos comparaciones, oportunidades de investigación y advertencias sobre cobertura.

El segundo producto, Inference, estima un precio de referencia para una presentación. Evaluamos cinco modelos y una baseline, separando productos entre entrenamiento y prueba. Ridge redujo el error medio un 26% frente a la mediana en el test. El usuario puede comparar su precio con referencias y simular un margen a partir de sus propios costos.

Proponemos un piloto de USD 2.223, con operación mensual estimada de USD 50. Si reducimos el relevamiento de doce a tres horas semanales, el valor del tiempo liberado sería USD 288 al mes. El retorno proyectado a doce meses sería 22,4%, con recuperación cercana a nueve meses y medio. Es una hipótesis que debe medirse.

La muestra cubre un canal y una fecha: no predice demanda, ventas ni rentabilidad. Nuestro valor es ayudar a decidir con evidencia y reconocer cuándo falta información.

## Demo y ampliación
Mostrar filtros, comparador real, matriz, consulta Inference y simulador; usar datos existentes. Si hay corridas cloud comprobadas, mostrar Run ID y flujo Make/Drive. Si no, declarar pendiente. Cerrar con propuesta piloto, no contrato aceptado. Actualizar cifras al reproducir lote y medir costos.
