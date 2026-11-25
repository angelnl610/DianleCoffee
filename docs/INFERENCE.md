# Producto 2 — Inference
## Problema y contrato
Regresión supervisada para estimar el precio de lista por presentación (ARS), no precio futuro, demanda ni precio óptimo. Features: formato, marca, canal, peso_g y cantidad_capsulas; target: precio_lista_ars. Precio propuesto y costos son parámetros de evaluación, no predictores.

## Preprocesamiento y entrenamiento
Categorías: OneHotEncoder con categorías desconocidas admitidas; numéricas: imputación mediana y StandardScaler. Cero estructural solo para dimensión no aplicable. Los transformadores se ajustan con train dentro del pipeline. GroupShuffleSplit por grupo_producto separa test (25% de grupos) y luego validación (25% del resto), semillas 42 y 43. No se comparte el mismo producto entre particiones. Se elige el menor MAE de validación, nunca por test. El modelo seleccionado queda entrenado en train; el Actor no vuelve a entrenar.

| Candidato | Enfoque |
|---|---|
| Mediana | Baseline: valor constante de train |
| Linear Regression | Relación lineal |
| Ridge | Regresión lineal regularizada L2, reduce sensibilidad a coeficientes grandes |
| Random Forest | Promedio de árboles |
| Gradient Boosting | Árboles secuenciales que corrigen errores |
| MLP | Red neuronal; target escalado |

El script guarda MAE, RMSE y R² por validación/test para todos los candidatos, aviso de convergencia, importancia por permutación, señales train, grupos y residuos. Los artefactos están fuera de Git; no inventamos métricas no disponibles. Recuperar models/metadata.json y data/results/inference.csv para la tabla completa.

## Resultados del lote reportado
Ridge ganó por MAE de validación. Test: 70 observaciones, 21 productos. MAE ARS 6.632,27 frente a mediana ARS 8.963,36, mejora relativa 26,0%. MAE es promedio del error absoluto en pesos, RMSE penaliza más errores grandes, R² mide ajuste relativo a la media del test y puede ser negativo. No decir que 26% es precisión.

| Formato | Grupos test | MAE ARS |
|---|---:|---:|
| Grano | 1 | 13.334,74 |
| Cápsulas | 5 | 4.586,35 |
| Instantáneo | 7 | 5.482,35 |
| Molido | 8 | 6.963,76 |

El error de grano no puede generalizarse. Una brecha de precio dentro del MAE del formato es señal débil. Tamaños fuera del rango y formatos sin soporte se rechazan; marca desconocida genera advertencia. El resultado se contrasta con comparables en la interfaz; si no hay soporte, se puede mostrar una referencia descriptiva identificada. La clasificación de evidencia no es probabilidad de acierto.

## Simulador comercial
El usuario aporta precio P, costo variable C, unidades U, costo fijo F y margen objetivo m (fracción). Ingreso P×U; contribución (P−C)×U; resultado = contribución−F. Margen del escenario = resultado/ingreso; precio mínimo = (C+F/U)/(1−m), redondeado hacia arriba a centavos. Con U=0 no se calcula margen ni precio mínimo. No equivale al margen bruto unitario si incluye costos fijos y no predice ventas.

## Persistencia y prueba
models/model.joblib y metadata.json guardan pipeline, versión scikit-learn y hashes; cargar solo artefactos confiables. scripts.train entrena fuera de Apify. src/inference.py carga y predice; src/operations.py valida lote y devuelve INFERENCE con errores por fila. Probar con consultas nuevas válidas sin reentrenar; conservar OUTPUT, DOCUMENTACION y métricas. Resultado histórico reportado, no reejecutado en esta auditoría. Nube y Windows pendientes.
