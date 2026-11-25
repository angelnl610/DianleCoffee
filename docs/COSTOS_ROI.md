# Propuesta comercial y retorno de inversión
Dianle · 24/11/2026 · Propuesta piloto no aceptada ni facturada.

## 1. Presupuesto por producto (USD)
La ficha del curso fija USD 2.500 iniciales y USD 150 mensuales máximos. El ejemplo de la hoja Presupuesto (100 horas a sus tarifas de ejemplo) suma USD 2.375 de costo y USD 3.087,50 con recargo del 30%, por encima del límite. Proponemos 62 horas presupuestadas para un MVP acotado. No son horas registradas ni pagos efectivos.

| Etapa | Perfil | Horas | USD/h | Subtotal USD |
|---|---|---:|---:|---:|
| Analytics | DS | 12 | 35 | 420 |
| Analytics | SE | 10 | 20 | 200 |
| Analytics | BA | 8 | 25 | 200 |
| Inference | DS | 14 | 35 | 490 |
| Inference | SE | 10 | 20 | 200 |
| Inference | BA | 8 | 25 | 200 |
| Total | | 62 | | 1.710 |

Tarifas de referencia consultadas el 24/11/2026: [Upwork](https://www.upwork.com/resources/upwork-hourly-rates/), Data Scientist USD 35–250/h, Software Developer USD 10–100/h (aproximación al rol SE), Business Analyst USD 25–60/h. Elegimos tarifas del extremo bajo por alcance de piloto. Son referencias internacionales, no cotizaciones vinculantes.

| Etapa | Costo | Recargo 30% | Precio propuesto |
|---|---:|---:|---:|
| Analytics | 820 | 246 | 1.066 |
| Inference | 890 | 267 | 1.157 |
| Total | 1.710 | 513 | 2.223 |

Margen comercial bruto presupuestado = 513/2223 = 23,08%. El 30% del Excel es recargo sobre costo, no margen sobre venta. Restan USD 277 del presupuesto de Diana. El costo laboral es una estimación; no incluye impuestos ni costos de herramientas iniciales no medidos. Si surgen, deben absorberse dentro del saldo o renegociarse. Pago por etapa sujeto a aceptación; no afirmar que el 12/11 hubo pago o que se acordó un adelanto. La oferta comprende alcance de NEGOCIO.md, entrega y guía de uso; costos operativos se consideran por separado.

## 2. Operación mensual
Escenario objetivo, NO cotización de planes ni consumo observado: USD 15 Apify, USD 10 Make, USD 5 alojamiento/almacenamiento, USD 20 mantenimiento (1 h a USD 20). Total USD 50/mes. El uso de cuotas gratuitas puede reducirlo; si no alcanzan, revisar plan y frecuencia sin contratar automáticamente. Ejemplo de frecuencia de evaluación: 4 lotes Analytics y 20 lotes Inference al mes, sujeto al cliente. La frecuencia efectiva y el tamaño se validan. No duplicar cargos si un plan ya incluye créditos. El máximo de ficha es USD 150/mes.

## 3. ROI para Diana
Base académica: 12 h semanales × USD 8/h. Meta piloto: 3 h semanales. Ahorro bruto de tiempo valorizado = (12−3)×8×4 = USD 288/mes. No equivale necesariamente a ahorro salarial efectivo. Horizonte 12 meses, cuatro semanas por mes, sin descontar flujos. No sumar la meta de ventas de USD 15.000/mes ni NPS al beneficio.

| Escenario | Horas restantes/sem | Operación USD/mes | Beneficio bruto/mes | Neto/mes | Payback meses | ROI 12 meses |
|---|---:|---:|---:|---:|---:|---:|
| Objetivo | 3 | 50 | 288 | 238 | 9,34 | 22,4% |
| Prudente | 6 | 50 | 192 | 142 | 15,65 | −18,4% |
| Operación máxima | 3 | 150 | 288 | 138 | 16,11 | −14,1% |

Inversión inicial común: USD 2.223. ROI = (beneficio bruto acumulado − inversión − operación acumulada)/(inversión + operación acumulada). Escenario objetivo: (3456−2823)/2823 = 22,4%. Recupero = inversión / beneficio neto mensual si es positivo. Para ROI no negativo a 12 meses en escenario objetivo, la operación mensual debe ser como máximo USD 102,75. Medir trabajo humano en tareas equivalentes antes/después, incluidos revisión y carga, y no confundirlo con duración del Actor. KPI meta: reducción del 75% del tiempo; no lograda todavía.

## 4. Comercialización del Actor
Un servicio con dos operaciones; costo y precio por corrida se calculan por separado. No fijar precio definitivo sin medición. CU aproximadas = memoria asignada GB × duración en horas; usar CU facturadas en consola y tarifa efectiva del plan, más almacenamiento, transferencia, builds prorrateados y otros cargos aplicables. Make: créditos consumidos × costo efectivo, considerando cuota y plan. Costo por 1.000 registros = costo de corrida / filas válidas × 1000, solo como normalización, no garantía de escalabilidad. Precio objetivo con margen bruto 30% = costo total por operación / 0,70, redondeado hacia arriba conforme al modelo de monetización de Store y comisiones aplicables. El precio de Store no se suma al presupuesto de Diana si ya está incluido en su operación mensual.

| Operación | Run ID | Filas válidas | Segundos | Memoria MB | CU | Costo USD | Créditos Make | Minutos humanos | Precio propuesto |
|---|---|---|---|---|---|---|---|---|---|
| Analytics | Pendiente | | | | | | | | |
| Inference | Pendiente | | | | | | | | |
| Adquisición | Pendiente | | | | | | | | |

Hasta el último estado de desarrollo: cero builds y corridas cloud. Guardar evidencias de saldo, plan, IDs, versión, resultados y cargos; no confundir uso local con facturación. Revisar términos y permisos antes de publicar.

Fuentes: cronograma alumnos, hojas Resumen y Presupuesto; clases 42–47, lámina 12; [Upwork](https://www.upwork.com/resources/upwork-hourly-rates/).