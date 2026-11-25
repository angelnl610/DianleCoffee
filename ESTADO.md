# Estado de Dianle Coffee · 24/11/2026

Objetivo: evaluar catálogo y posicionamiento con datos reales de café envasado. Los archivos se crearon en el repositorio local existente.

| Etapa | Archivos y resultado |
| --- | --- |
| 1 · Entorno y fuentes | Se creó .venv con Python 3.13, disponible junto con 3.14. pip falló con getaddrinfo al resolver PyPI. Sin wheels relevantes en la caché. curl tampoco resolvió api.mercadolibre.com, datos.gob.ar, datos.produccion.gob.ar ni hysmarcos.github.io. La documentación web oficial de SEPA confirma que existe un catálogo de descargas; la consulta directa a sus páginas produjo timeout/403. La documentación indexada de Mercado Libre describe llamadas autenticadas; no se comprobó acceso autorizado ni un dataset de café. |
| 2 · Adquisición y análisis | scripts/acquire.py implementa el contrato documentado del derivado de SEPA, CABA con la etiqueta AMBA de origen, mediana por producto/cadena/región y un día. No se pudo verificar el manifest remoto ni bajar un lote. src/etl.py, src/eda.py y scripts/run_analytics.py producen salidas a partir de un CSV real validado por hash. Cuatro pruebas unitarias aisladas pasaron. |
| 3 · Modelo | scripts/train.py prepara cinco candidatos y mediana, split agrupado, selección por MAE de validación, test y permutación. No se entrenó ni se produjeron predicciones reales. El umbral de 20 productos es una decisión de protocolo, debe revisarse junto a la diversidad de la muestra. |
| 4 · Interfaz | app.py, config.py y ui/ contienen las dos vistas, tema, filtros, EDA, formulario y referencia de mediana si hay comparables. Streamlit no está instalado, la interfaz todavía requiere una prueba de ejecución. |
| 5 · Verificación | Pasaron .venv\Scripts\python.exe -m unittest discover -s tests -v y compileall. scripts.run_analytics y scripts.check_demo reportan la falta de archivos reales. Pendiente el ensayo en modo avión con instalación y datos completos. |
| 6 · Integración | Se preparó el Actor y la entrada JSON con hasta 50 filas en la prueba inicial. Schema, build, Make, Drive y extracción en Apify pendientes de prueba. Se optó por preparar CSV→JSON en Python y validar JSON en Make. Consumo: 0 builds, 0 corridas, 0 créditos usados en esta sesión. |
| 7 · Entregables | README y docs incluyen negocio, guías, costo/ROI, métricas, diccionario, demo, defensa y trazabilidad. Insights con cifras y pitch pendientes del lote real. Video, Store y portafolio público pendientes. |
| 8 · Git | Sin commit ni push. Existe material académico previamente versionado, revisar historial y licencias antes de publicar. Configuración, código y documentación nuevos listos para revisión. |

## Fuentes y evidencia académica

- [SEPA oficial](https://datos.gob.ar/sl/dataset/produccion-precios-claros---base-sepa) registra archivos diarios. No se asumió que la última fecha del portal refleje precios actuales.
- [Ítems y búsquedas de Mercado Libre](https://developers.mercadolibre.com.ar/es_ar/administra-areas-de-cobertura/items-y-busquedas) muestra ejemplos con Bearer. La adquisición multicanal queda pendiente.
- [superprecios-claros](https://github.com/hysmarcos/superprecios-claros) documenta los endpoints y la granularidad. MIT corresponde al código del proyecto. Revisar términos de los datos antes de redistribuir.
- Se inspeccionaron inventario académico y PDF Clases 42–47, de 25 páginas. Se renderizaron y leyeron visualmente las páginas 10–12. Confirman las dos operaciones en un Actor, Analytics seguido de Inference, documentación GET y ejecución POST, medición de costos y publicación Store.
- Registro real de la reunión y pedidos de Diana pendiente de aporte del equipo.

## Retomar

Con DNS disponible, instalar requisitos y correr adquisición inicial. Si las fuentes siguieran inaccesibles, usar un CSV de observaciones reales autorizado y su manifest. Revisar diversidad, fecha, marcas, comercios, inclusiones y exclusiones antes de entrenar. Luego verificar Streamlit, pruebas con resultados reales y demo sin red. Para probar nube, confirmar autorización explícita y saldo antes del primer build/run.

## Verificación del flujo local en Codex · 24/11/2026

- Se cargó el commit `5529ce0` y se instalaron las dependencias fijadas con Python 3.13.5 en Linux.
- `scripts/acquire.py` usa `fecha_datos` del manifiesto verificado. `src/etl.py` reconoce GRM, KGM y UNI en descripciones de la fuente. `tests/test_etl.py` cubre estas unidades.
- `python -m scripts.acquire --limite 2000 --shards 32` descargó 5.873.516 bytes y guardó 286 observaciones del 15/11/2026. `python -m scripts.run_analytics` conservó las 286; 250 admiten precio unitario.
- `python -m scripts.train` seleccionó Ridge. El MAE en test fue de ARS 6.632,27 frente a ARS 8.963,36 de la mediana base. `python -m scripts.check_demo` verificó la inferencia desde los archivos locales.
- `python -m pytest` pasó 5 pruebas. Streamlit AppTest verificó ambas vistas, el filtro de cápsulas y el envío del formulario con una presentación dentro del rango entrenado. Se documentaron hallazgos en `docs/INSIGHTS.md`.
- Consumo de Apify y Make en esta etapa: 0 builds y 0 corridas. Quedan pendientes la verificación de Apify, Make y Drive, y el ensayo en Windows.

## Cierre previo a integración externa · 24/11/2026

- Se preservó el estado anterior en `1fe5f9a` y se subió la rama privada `desarrollo/preintegracion`. La copia original del lote, salidas y modelo quedó en `data/archive/preintegracion`. El crudo activo conserva las mismas 286 observaciones con región AMBA; el manifiesto documenta el hash anterior. Analytics corrige también lotes previos con URL verificable de AMBA.
- Se revisaron AGENTS, notas de entrega y las láminas 10–12 del Capstone. Se actualizaron la trazabilidad, los hallazgos, el pitch, la ficha del Actor y la planilla de medición de costos. Los indicadores y comparables usan formato, fuente, canal, región y fecha. Se incorporaron comparaciones por identificador y una referencia descriptiva cuando la consulta no tiene soporte de modelo.
- `scripts.run_analytics` conservó 286 de 286 filas y calculó precio unitario para 250. `scripts.train` evaluó los cinco candidatos y la mediana. Ridge fue elegido por validación y obtuvo MAE de ARS 6.632,27 en test, frente a ARS 8.963,36 de la mediana. El error de grano proviene de un solo producto de prueba. El posicionamiento mostrado es orientativo; el modelo aporta una referencia inicial de este lote.
- `scripts.verify_local` pasó en Linux con Python 3.13.5, bloqueado el acceso externo durante esa prueba. Verificó nueve pruebas, modelo y demo, filtros, reinicio, formulario y ausencia de lote. `scripts.verify_local --sdk` pasó con Apify SDK 3.1.0 en almacenamiento temporal local; las salidas coincidieron con los archivos de referencia para Analytics (50/50) e Inference (5/5). La ruta local de adquisición del Actor descargó 50 observaciones de AMBA, 2.638.641 bytes, en 3,45 segundos. Se confirmó el hash del crudo devuelto.
- Se cambió a Apify SDK 3.1.0 porque la versión 2.7.2 dependía de un paquete sin wheel compatible con Windows/Python 3.13. Se resolvieron wheels para Windows x64 con Python 3.13 en una prueba de dependencias; falta ejecutar en Windows. La CLI de Apify validó el esquema de entrada, con un error posterior al intentar escribir su configuración de usuario en este entorno. El socket de Docker local no estuvo accesible, así que el Dockerfile y los límites de memoria quedan pendientes de build y corrida real.
- Los comandos, JSON reales, salidas de comparación y contexto privado de build quedaron listos según `INTEGRACION_PASO_A_PASO.md`. El contexto incluye exclusivamente el modelo generado localmente y su metadata verificada, además del código y los esquemas. Datos y modelos están ignorados por Git.
- Consumo externo de Apify y Make: cero builds y cero corridas. Quedan pendientes el build y las corridas privadas, las conexiones de cuenta a Make y Drive, la medición real de costos y la publicación autorizada. Mercado Libre requiere acceso autorizado o un lote con permiso y procedencia verificable. Confirmar con el docente si el GET de metadatos y README satisface el requisito de documentación.

## Auditoría de GitHub y cierre comercial · 24/11/2026

- Se partió de `1459ea0` con la rama `desarrollo/preintegracion` limpia. Se completaron el comparador de 2 a 4 productos, matriz de oportunidades, insights dinámicos, suficiencia descriptiva, recomendaciones, simulador por supuestos y exportación JSON. Analytics e Inference amplían sus salidas conservando el contrato de lotes y las claves de almacenamiento. El cálculo compartido vive en `src/commercial.py`.
- Se agregaron los cinco scripts PowerShell con un intérprete común y se actualizaron la guía de integración, las instrucciones de clonación superficial y dispersa, la documentación del Actor y la trazabilidad. Se preparó un ZIP de código sin historial, material académico, cachés, entornos, datos o modelos.
- Desde una extracción limpia del ZIP en Linux, `scripts.acquire` volvió a descargar 286 observaciones y `scripts.run_analytics`, `scripts.train` y `scripts.verify_local --sdk` completaron el flujo. Ridge obtuvo el mismo MAE de ARS 6.632,27. Pasaron 16 pruebas, AppTest y el SDK 3.1.0 usando el contexto preparado, con Analytics, Inference y un caso aislado de simulación. También pasó `scripts.verify_local` sin acceso externo con el lote conservado. El paquete oficial `@apify/input_schema` validó el esquema.
- Se preservaron el lote anterior y el modelo. No se generó una nueva distribución de datos ni modelo porque sus permisos de redistribución no están confirmados. La preparación genera `data/integracion/manifest_archivos.json` con rutas, tamaños y hashes, y la guía permite regenerar los archivos desde la fuente disponible o desde un CSV original autorizado.
- Quedan pendientes PowerShell en Windows, build Docker, corridas privadas en Apify, configuración efectiva de Make y Drive y medición de consumo. El escenario se documenta módulo por módulo. La compatibilidad de un blueprint y su exportación se comprueban después de armarlo en la cuenta. GitHub Actions queda pendiente de confirmar permisos y cuota. No se modificó `main` ni se reescribió historial. Consumo externo en Apify y Make: cero builds y cero corridas.

## Ajustes de la auditoría 442bbda · 24/11/2026

- Se completaron el margen del escenario, el objetivo y el precio mínimo; el comparador con brechas frente al primer producto y promociones por comercio; la clasificación de evidencia en tres niveles con antigüedad; las recomendaciones de mercado y costos; y los indicadores de cobertura, dispersión, brechas y promociones en la matriz.
- Se agregó el documento JSON `DOCUMENTACION` al almacenamiento del Actor y se enlazó desde su esquema de salida. Apify ofrece un GET autenticado al registro de una corrida existente. El documento contiene propósito, operaciones, parámetros, ejemplos, formatos, límites y estado del precio comercial. La URL externa se comprobará en la primera corrida privada autorizada.
- La preparación genera los documentos esperados para ambas operaciones y fija `fecha_referencia` en las entradas de prueba. Se reutilizaron el lote de 286 observaciones y el modelo Ridge existente. No se reentrenó.
- Pasaron 20 pruebas, AppTest, validación del esquema oficial de entrada y pruebas de ambas operaciones con el SDK local. En Analytics se regeneraron los indicadores con el mismo lote. No se hicieron builds ni corridas externas. Quedan pendientes Windows, integración externa, revisión de resultados, correcciones de integración y entregables académicos.

## Rama de entrega · 24/11/2026

- `entrega/final` parte de `bb22834` y conserva la documentación académica y comercial, los ocho puntos del README, el código, los contratos, las pruebas y los scripts. El árbol de entrega excluye `materiales/`, `AGENTS.md` y `docs/AUDITORIA_CIERRE.md`. El historial anterior sigue en Git y la descarga ligera usa un clon superficial o el ZIP.
- Verificación en Linux con el lote y modelo existentes: 20 pruebas, demo de ambas vistas con AppTest y paridad del SDK local de Analytics e Inference, incluidos sus registros de documentación. Se generó el contexto de build del Actor; el build Docker y las corridas externas quedan pendientes. Se revisaron los enlaces y las rutas y módulos invocados por los cinco scripts PowerShell; su ejecución en Windows queda pendiente.
- El ZIP de entrega incluye solo archivos versionados del árbol limpio. El lote y modelo se recuperan de una copia autorizada o se regeneran como indica la guía. En esta preparación no se repitieron la descarga de datos ni el entrenamiento. No se iniciaron builds, corridas externas ni publicaciones. El proyecto y la documentación se prepararon con asistencia de IA y requieren revisión y defensa por el equipo.

## Preparación de copia independiente · 25/11/2026

- Este registro conserva las etapas históricas (incluidas las referencias a ramas y ZIP anteriores). Para instalar la entrega vigente, seguir el README y la guía actualizados; ya no se requiere clonar una rama de desarrollo.
- Base funcional: `9a45cc508842fed57c479d937980bbeb36b7a629` de `integration/drive-dashboard`, con las mejoras visuales y de Drive. El [workflow de dashboard](https://github.com/angelnl610/DianleCoffe/actions/runs/45508391260) finalizó correctamente en esa revisión.
- Se actualizan documentación, nombres de CSV en la guía de integración, reglas de exclusión de credenciales y disparadores del workflow para `main`. No se alteran el código de aplicación, el modelo ni las pruebas. Verificar la copia y el despliegue nuevo antes de entregar; conservar la evidencia histórica y el reconocimiento de asistencia con IA.
