# Producto 1 — Analytics
## Propósito
Describir oferta de café envasado para elegir qué presentaciones comparar e investigar, sin atribuir ventas a la oferta observada.

## Origen y ETL
Fuente derivada de SEPA: https://hysmarcos.github.io/superprecios-claros/v1/manifest.json. Cada fila corresponde a un agregado de precio por producto/cadena/región; no sucursal individual. El lote reportado del 15/11/2026 contiene 286 filas, 82 productos, 27 marcas y 9 comercios en AMBA. Fecha de extracción y observación se distinguen en el manifiesto. Mercado Libre no integra el lote.

| Paso | Entrada | Salida |
|---|---|---|
| Adquisición | Manifest y fragmentos de la fuente | CSV crudo y manifiesto con SHA-256 |
| Validación | Filas crudas | Identidad, fecha, comercio, formato y precio válidos |
| Transformación | Registros válidos | Nombre normalizado, tipo, peso o cápsulas, precio unitario y grupo de producto |
| Calidad | Entrada y salida | Conteos, exclusiones, faltantes |
| EDA | Registros limpios | Indicadores por formato/fuente/canal/región/fecha, mediana, IQR, promociones conocidas, atípicos |
| Visualización | Indicadores y registros | Filtros, comparador 2–4 productos, matriz, insights y CSV |

Reglas: precio de lista positivo; duplicados por fuente/id_oferta/fecha; EAN o grupo heurístico declarado; excluir categorías ajenas; conservar registros válidos sin tamaño pero sin precio unitario. Lista normalizada a ARS/kg en molido/grano, ARS/100 g en instantáneo y ARS/cápsula. Precio promocional separado; solo promoción general comprobada modifica precio efectivo. Desconocido no es cero.

## Resultados reportados
286 de 286 filas conservadas; 250 con precio unitario (87,4%). Cápsulas: 32/68 con cantidad verificable; las 36 restantes no sirven para comparación unitaria. Consultar [Insights](INSIGHTS.md) para medianas y decisiones. No hay evidencia temporal ni datos de ventas o reviews.
 
## EDA, señales y oportunidades
Mediana: centro robusto ante valores extremos; IQR = Q3−Q1, dispersión central; atípicos: fuera de Q1−1,5 IQR y Q3+1,5 IQR (cuando hay soporte y dispersión). Un atípico es señal de revisión, no error automático. Las promociones se dividen por observaciones de estado conocido. La matriz usa ±10% de mediana de segmentos compatibles y umbrales de cobertura/fecha. La evidencia suficiente requiere 8 observaciones unitarias, 5 productos y 2 comercios, hasta 30 días; limitada o insuficiente si no se cumplen criterios. No es un score de rentabilidad.

Pearson mide asociación lineal entre variables numéricas aplicables y precio; información mutua detecta dependencia que puede ser no lineal, no demuestra causalidad. Se muestran hasta 5 de cada grupo según disponibilidad; con solo dos variables numéricas y cinco features totales no se fuerza una lista de diez. Valores efectivos se generan al ejecutar el lote, no están versionados. El modelo usa señales de train como diagnóstico y no descarta automáticamente features por un ranking.

## Evidencia y reproducción
Ejecutar scripts.acquire, scripts.run_analytics y verificar_proyecto según README. Salidas: data/raw/cafe_raw.csv, manifest.json, data/processed/cafe_clean.csv, quality.json y resultados analíticos. Guardar capturas del dashboard, conteos y hash. Las pruebas en Linux/SDK fueron reportadas por el equipo de desarrollo; nube y Windows pendientes. Si cambia la fecha de fuente, actualizar resultados y no atribuir cifras antiguas al lote nuevo.
