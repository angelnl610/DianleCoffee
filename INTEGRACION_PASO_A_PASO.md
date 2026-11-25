# Dianle Coffee · Integración paso a paso

El flujo local usa Python 3.13. El Actor utiliza el mismo ETL, EDA y predicción. La configuración de cuentas y las corridas externas siguen pendientes. Mantené el Actor, los archivos y las carpetas privados. Antes de enviarlos a cualquier servicio, comprobá el permiso de uso del lote y del artefacto derivado.

## 1. Prepará la computadora

Descargá el ZIP del repositorio de entrega y extraelo, o cloná el repositorio una vez publicado. Abrí PowerShell en su carpeta raíz:

```powershell
git clone https://github.com/angelnl610/DianleCoffee.git
cd DianleCoffee
```

No hace falta elegir una rama de desarrollo. El ZIP permite usar el proyecto sin Git. Si cambia la cuenta de publicación, copiá la URL del botón Code del repositorio.

En Windows, instalá Python 3.13 x64 con el lanzador `py` y ejecutá:

```powershell
.\preparar_entorno.ps1
.\preparar_datos.ps1
.\verificar_proyecto.ps1 -Sdk
.\ejecutar_demo.ps1
```

Si ya restauraste el lote procesado, los resultados de prueba y un modelo que coincide con ese lote, omití `preparar_datos.ps1` y empezá por verificar después de instalar las dependencias. `verificar_proyecto.ps1 -Sdk` también genera el contexto del Actor. Para regenerar únicamente ese contexto y sus salidas de control, usá `preparar_integracion.ps1`.

Si ya tenés el lote autorizado original, colocá antes de preparar datos `data/raw/cafe_raw.csv` y `data/raw/manifest.json`. Si faltan ambos, el script adquiere un lote público AMBA de hasta 2.000 observaciones con 32 fragmentos. La fuente puede actualizar la fecha y las observaciones. Un lote nuevo reproduce el procedimiento, y para reproducir los números históricos se requiere el CSV original junto con su manifiesto. Usá `-Descargar` solo cuando quieras reemplazar el crudo por uno nuevo. El hash y el conteo se validan al procesar. El entrenamiento reconstruye el modelo, las métricas y el conjunto de prueba. Si la fuente no está disponible, retomá con un CSV autorizado y su manifiesto compatible.

En Linux, creá el entorno con `python3.13 -m venv .venv`, instalá `.venv/bin/python -m pip install -r requirements.txt` y ejecutá, con ese intérprete, los módulos `scripts.acquire --limite 2000 --shards 32` si faltan ambos archivos, `scripts.run_analytics`, `scripts.train`, `scripts.verify_local --sdk`, `scripts.prepare_integration` y `streamlit run app.py`. Abrí `http://127.0.0.1:8501`. Con dependencias y datos en disco, la verificación sin `--sdk` y la demo funcionan sin Internet.

La copia de código prescinde de datos y modelos. La preparación genera `data/integracion/manifest_archivos.json` con las rutas, tamaños y SHA-256 del crudo, su manifiesto, el limpio, la calidad, los resultados, el modelo y los archivos de prueba. Copiá esos archivos solo cuando tengas permiso de transferencia.

`verify_local` genera y verifica:

| Archivo o carpeta | Contenido |
| --- | --- |
| `data/integracion/analytics.json` | Hasta 50 observaciones reales del crudo |
| `data/integracion/inference.json` | Hasta 5 consultas válidas tomadas de productos del conjunto de prueba |
| `data/integracion/esperado/analytics/` | OUTPUT, QUALITY, ANALYTICS, CAFE_CLEAN y DOCUMENTACION |
| `data/integracion/esperado/inference/` | OUTPUT, INFERENCE y DOCUMENTACION |
| `data/integracion/actor/` | Contexto de build con código, esquemas, Dockerfile y par modelo/metadatos verificado |

Para el lote conservado se esperan 50 de 50 filas válidas en Analytics y 5 de 5 en Inference. La región de Analytics debe ser AMBA. Las entradas de prueba fijan `fecha_referencia` para preservar la antigüedad al comparar. En corridas operativas omitila para usar la fecha UTC del run. Compará cada corrida con los archivos generados a partir de **esa misma entrada y ese mismo build**. El identificador y los conteos deben coincidir. Para números en punto flotante admití diferencias de redondeo entre plataformas. El hash documenta integridad local; usá exclusivamente un modelo generado por el equipo.

## 2. Construí y probá el Actor privado

1. Confirmá plan, saldo y autorización antes del primer build y de cada prueba. Instalá la [CLI oficial](https://docs.apify.com/cli/) con Node y `npm install -g apify-cli`. Autenticate con `apify login` en tu terminal privada.
2. Desde la raíz, ejecutá `apify validate-schema .actor/input_schema.json`. Cambiá a `data/integracion/actor` y corré `apify push` solo cuando corresponda. El contexto incluye `models/model.joblib` y `models/metadata.json`; el Dockerfile valida su consistencia durante el build. Conservá Actor ID, número de build y duración. Confirmá que el Actor tenga acceso privado.
3. En Apify Console, seleccioná ese build. Empezá con **512 MB** y **120 segundos**. En el modo de entrada JSON pegá `analytics.json`. Corré una vez. En el Run buscá estado `SUCCEEDED` y descargá `OUTPUT`, `CAFE_CLEAN`, `QUALITY` y `ANALYTICS` del Key-Value Store.
4. Repetí con `inference.json`. Compará `OUTPUT` e `INFERENCE` con la carpeta esperada. El resultado incluye referencia, versión, evidencia, recomendación y advertencias. Si una consulta aporta conjuntamente `precio_propuesto`, `costo_unitario_ars`, `unidades` y `costo_fijo_ars`, incluye el escenario comercial. `margen_objetivo_pct` acepta de 0 a menos de 100 y devuelve el precio mínimo del escenario si hay volumen positivo. Analytics entrega la matriz de oportunidades y los insights en `ANALYTICS`. Un estado `parcial` indica filas rechazadas, y `sin_resultados` indica que ninguna resultó válida, aunque el Run en sí haya finalizado.
5. Para demostrar la adquisición mediante Apify, corré aparte el JSON siguiente. Consume red hacia el endpoint público autorizado, con límite fijo de 50 observaciones y 12 fragmentos. Descargá también `CAFE_RAW` y `MANIFEST`. Comprobá fecha real, AMBA y SHA-256. El contenido puede variar por fecha de publicación; validalo contra su propio manifiesto.

```json
{"operation":"analytics","batch_id":"adquisicion-sepa-01","adquirir_sepa":true}
```

Si falla una corrida, conservá el `runId`, el estado de Apify, `OUTPUT` y el mensaje del log. Revisá el motivo antes de reintentar. Para un fallo de descarga, reutilizá el lote autorizado ya guardado para probar las otras operaciones.

## 3. Conectá Make y Drive

Creá las carpetas privadas `Dianle/entrada`, `Dianle/salida` y `Dianle/evidencias`. Subí los dos JSON de prueba a `entrada`. Conservá el CSV y manifiesto originales en la misma carpeta si su uso en Drive está permitido. Para la primera prueba creá un escenario Analytics y después duplicalo para Inference. Dejá desactivada la programación.

| Orden | Módulo o filtro | Valores y mapeo |
| --- | --- | --- |
| 1 | Google Drive → Download a File | Conexión OAuth privada. Elegí el ID de `analytics.json` o de `inference.json` en el duplicado. |
| 2 | Filtro de tamaño + JSON → Parse JSON | Rechazá archivos vacíos o de más de 1.000.000 bytes usando el tamaño del binario o el tamaño del archivo en Drive. Convertí el campo Data de descarga a texto UTF-8 y mapealo a JSON string. Creá la estructura de datos con el JSON real del escenario. |
| 3 | Filtro de entrada | Exigí `operation` correspondiente, `batch_id` alfanumérico con guion o guion bajo de 1–80 caracteres, `origen.fuente` y `origen.sha256_csv_origen` presentes, entre 1 y 50 elementos en `rows`, y adquisición desactivada en esta ruta. No uses Iterator. |
| 4 | Apify → Run an Actor | Conexión privada de Apify, Actor ID de la sección 2, mismo build, modo síncrono, 512 MB y 120 segundos. Input JSON recibe el texto UTF-8 completo del módulo 1. Guardá `id`, `status` y `defaultKeyValueStoreId`. |
| 5 | Filtro y HTTP → Make a request | Si el estado no es `SUCCEEDED`, detené la rama de publicación. Si quedó en ejecución, recuperá su estado por ID antes de considerar otro POST. Para éxito, GET autenticado de `OUTPUT`, usando la credencial en la conexión de HTTP. Compará `batch_id`, `operation` y `filas_entrada` con el JSON inicial. Para la prueba exigí `status=ok` y `filas_validas=filas_entrada`. |
| 6 | HTTP → Make a request | Un GET por clave esperada. Analytics: `CAFE_CLEAN`, `QUALITY`, `ANALYTICS`. Inference: `INFERENCE`. Usá respuesta sin parsear para conservar el contenido en Drive. |
| 7 | Google Drive → Upload a File | Un módulo por archivo, carpeta `salida`. Mapeá Data desde el cuerpo recuperado y nombre `<batch_id>-<runId>-<KEY>.<ext>` para los JSON, incluido `OUTPUT`. Para `CAFE_CLEAN`, usá `<batch_id>-<runId>_cafe_clean.csv`, compatible con el lector de Drive del dashboard. Desactivá conversión a documentos de Drive. |

Los GET de almacenamiento usan `https://api.apify.com/v2/key-value-stores/<storeId>/records/<KEY>` con Bearer configurado como credencial privada. El filtro de validación usa los campos JSON de OUTPUT y la subida usa su cuerpo original o el JSON serializado. Para consultar un Run iniciado usá `GET https://api.apify.com/v2/actor-runs/<runId>`. Conservá la ruta del error con el identificador de lote y Run; no agregues reintentos automáticos al POST. Ante 401/403 revisá las conexiones. Ante 429 guardá la evidencia y comprobá cuota antes de continuar. Si un GET o la subida falla, recuperá los archivos del mismo Run en vez de lanzar otro.

Corré **Run once** con Analytics y compará los archivos de Drive con el resultado local. Luego corré el escenario Inference y repetí la comparación. El presupuesto inicial es un lote por corrida, con una operación de descarga y una de subida por archivo, sin iterar por filas. Comprobá el consumo real en el historial antes de programar o ampliar el volumen. La guía usa configuración manual de conexiones, IDs de archivos y carpetas, mapeos, filtros y nombres de salida. Exportá el blueprint desde el escenario ya probado y revisá que no incluya datos o credenciales privadas. [Módulos Apify en Make](https://apps.make.com/apify) · [Módulos de Drive](https://apps.make.com/google-drive-modules)

## 4. Qué guardar como evidencia

Guardá build ID y número de build; Run ID, estado, fecha, duración, memoria y CU por operación; saldo antes/después; créditos Make en el historial; lista de archivos y acceso a Drive. Agregá la comparación local frente al Actor y la de los archivos de Drive. Medí manualmente el tiempo de intervención. El costo observado y el ROI final se completan después de esas pruebas. [Trazabilidad](docs/TRAZABILIDAD.md) · [Costos y ROI](docs/COSTOS_ROI.md)

## API del Actor

Consultá metadatos con `GET /v2/acts/<actorId>`. Ejecutá con `POST /v2/acts/<actorId>/runs?build=<numero>&memory=512&timeout=120`, cuerpo JSON y autenticación Bearer. Un POST aceptado entrega un identificador; consultá su estado y `defaultKeyValueStoreId` antes de recuperar los resultados. Los errores de contrato del Actor se registran en `OUTPUT` cuando el run llega a iniciarse. Los errores por fila de Inference quedan en `INFERENCE`, con numeración desde 1. Para el GET académico, tras la primera corrida autorizada abrí el enlace **Documentación de la API** del resultado o hacé `GET /v2/key-value-stores/<defaultKeyValueStoreId>/records/DOCUMENTACION` con Bearer. El JSON describe operaciones, parámetros, ejemplos, formatos, límites y estado del precio comercial. Comparalo con `DOCUMENTACION.json` en las salidas esperadas. El GET lee un registro del run existente. No inicia otro run y la automatización de Make puede seguir recuperando las mismas claves de negocio. [API de Apify](https://docs.apify.com/api/v2)

## Dashboard en el repositorio de entrega

Para desplegar la app en Streamlit Community Cloud, seleccioná `main` y `app.py` del repositorio nuevo. Configurá la carpeta de salida de Drive y los Secrets como indica [docs/DRIVE.md](docs/DRIVE.md). Verificá ambas vistas y que el hash del modelo coincida con el CSV. No se transfieren automáticamente Secrets ni despliegues de otro repositorio.
