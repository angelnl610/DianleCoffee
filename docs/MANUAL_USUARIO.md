# Manual breve
## Inicio
Abrí el dashboard autorizado de Streamlit o prepará entorno y datos con las instrucciones del README y entrá a http://127.0.0.1:8501. Comprobá fecha, región, fuente y disponibilidad de modelo. Si está configurado Drive, usá «Actualizar datos de Drive» para volver a consultar la carpeta.

## Explorar mercado
1. Elegir formato, marca y comercio según los filtros disponibles.
2. Leer cantidades de observaciones, productos, comercios y marcas; no confundir ofertas con ventas.
3. Revisar precio unitario y distribución solo dentro de unidades compatibles.
4. Seleccionar de 2 a 4 productos del mismo segmento y contrastar brechas frente al primero y detalle por comercio. Promoción desconocida no implica ausencia.
5. Consultar matriz de oportunidades, evidencia y recomendaciones. Priorizar investigación, no declarar demanda insatisfecha.
6. Descargar CSV del filtro y conservar fecha de consulta.

## Evaluar producto
1. Elegir formato, marca, canal y tamaño compatible con entrenamiento.
2. Introducir opcionalmente precio de venta para comparar.
3. Interpretar referencia, brecha, MAE, comparables y advertencias. La referencia es precio de lista estimado, no precio óptimo.
4. Si desea simular, ingresar costo variable unitario, unidades previstas, costo fijo y margen objetivo. Son supuestos propios; no predicciones.
5. Revisar resultado del escenario y precio mínimo, contrastar con mercado y exportar evaluación JSON.
6. Si no existe soporte suficiente, ampliar relevamiento o usar referencia descriptiva explícita. No forzar una recomendación.

## Problemas frecuentes
- Sin datos: recuperar lote autorizado y manifest o ejecutar preparación.
- Sin modelo o con hash incompatible: entrenar sobre el lote limpio vigente y actualizar el modelo y sus metadatos juntos.
- Presentación fuera de rango: seleccionar una compatible; no extrapolar sin validación.
- Nube no disponible: usar modo local con archivos previos.
- Fecha distinta: actualizar informes y resultados; no mezclar lotes.
