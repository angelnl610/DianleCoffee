# Oferta observada de café envasado

El lote del 15 de noviembre de 2026 reúne 286 observaciones de 82 productos, 27 marcas y 9 comercios. Cada observación corresponde a un precio por producto y cadena en la región AMBA de la fuente. La agregación regional impide identificar precios específicos de CABA. [Fuente derivada de SEPA](https://hysmarcos.github.io/superprecios-claros/v1/manifest.json)

| Formato | Observaciones | Productos | Observaciones con precio unitario | Mediana de precio unitario |
| --- | ---: | ---: | ---: | ---: |
| Cápsulas | 68 | 22 | 32 | ARS 1.061,31 por cápsula |
| Grano | 15 | 5 | 15 | ARS 54.130,00 por kg |
| Instantáneo | 115 | 28 | 115 | ARS 8.550,00 por 100 g |
| Molido | 88 | 27 | 88 | ARS 60.942,21 por kg |

Para evaluar una presentación de cápsulas, conviene contrastar el precio por cápsula con referencias compatibles y del mismo tamaño. En 36 de las 68 observaciones de cápsulas faltó un conteo explícito y quedaron fuera del cálculo unitario. La muestra de grano cubrió cinco productos, por lo que ampliar su cobertura ayudaría a fijar una referencia de catálogo.

Ridge fue elegido por MAE de validación. En la partición de prueba, con 70 observaciones de 21 grupos de producto, su MAE fue de ARS 6.632,27 frente a ARS 8.963,36 de la mediana base. La referencia sirve para orientar una revisión de precio. Los resultados corresponden a un solo día y canal, sin evidencia temporal ni de demanda.

## Utilidad y límites de la referencia

El MAE de Ridge bajó un 26,0% frente a la mediana base en esta partición. En grano, el test tuvo un solo producto y un error medio de ARS 13.334,74. En cápsulas fueron 5 productos y ARS 4.586,35; en instantáneo 7 productos y ARS 5.482,35; en molido 8 productos y ARS 6.963,76. Con estas muestras, una diferencia pequeña entre el precio propuesto y la referencia es una señal débil. Conviene revisar ofertas con el mismo identificador o tamaño, y ampliar fechas, canales y marcas antes de usar las estimaciones para fijar precios.

## Lectura de las herramientas comerciales

La matriz marca brechas de al menos 10% respecto de la mediana de precio unitario en cada combinación de formato, fuente, canal, región y fecha. La evidencia suficiente requiere ocho observaciones con unidad comparable, cinco productos distintos y dos comercios, con datos de hasta 30 días. Con menos cobertura o entre 31 y 90 días es limitada. Sin comparables, con fecha inválida o con más de 90 días es insuficiente. Los umbrales son reglas operativas del proyecto. El comparador muestra de dos a cuatro productos de un segmento, con sus medianas por envase y unidad, brechas frente al primero seleccionado y detalle de precios y promociones por comercio.

En Inference, la evaluación usa tamaño y formato, cobertura del test y soporte de marca. Una brecha menor o igual al MAE del formato debilita la señal. El simulador aplica los supuestos introducidos por el usuario: ingreso = precio × unidades; contribución = (precio − costo variable por unidad) × unidades; resultado = contribución − costo fijo. El resultado corresponde al escenario y no estima el volumen de venta.

El margen es resultado dividido por ingreso. Para un margen objetivo, el precio mínimo es (costo variable unitario + costo fijo por unidad del escenario) dividido por (1 − margen objetivo expresado como fracción), redondeado hacia arriba a centavos. Con volumen cero no se informa margen ni precio objetivo. La recomendación compara el precio objetivo con la mediana de ofertas comparables cuando existe.
