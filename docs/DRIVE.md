# Google Drive

1. En [Google Drive](https://drive.google.com/), seleccioná **Nuevo > Nueva carpeta** y creá Dianle. Adentro creá entrada, salida y evidencias.
2. En entrada usá **Nuevo > Subir archivo** para subir `cafe_raw.csv`, `manifest.json` y los JSON de entrada generados (`analytics.json` e `inference.json`). Make descarga el JSON correspondiente para invocar el Actor.
3. Conservá acceso restringido. La cuenta conectada a Make necesita leer entrada y escribir salida. Podés copiar el ID desde el enlace del archivo o elegirlo en el selector.
4. En salida buscá los archivos asociados al batch_id verificado. Descargá CAFE_CLEAN a `data/processed/cafe_clean.csv`, QUALITY a `data/processed/quality.json` y ANALYTICS a `data/results/analytics.json`. Descargá INFERENCE como JSON de evidencia en data/results. El CSV de evaluación se genera en entrenamiento local.
5. Guardá evidencias de ejecución sin credenciales. Mantené un respaldo local de raw, manifest, limpio y modelo para la demo.

## Dashboard en Streamlit Community Cloud

Seleccioná el repositorio de entrega, rama `main`, archivo `app.py` y Python 3.13. Usá como OUTPUT la carpeta de salida del flujo y subí `cafe_clean.csv` o `<batch_id>-<runId>_cafe_clean.csv` como CSV (sin convertirlo a Google Sheets). Compartí OUTPUT como lector con la cuenta de servicio para mantener el acceso restringido. El dashboard también admite una API key restringida a Drive API para carpetas de lectura pública.

Configurá estos valores en Secrets de Streamlit, o en el archivo local ignorado `.streamlit/secrets.toml`:

```toml
gdrive_folder_id = "ID_DE_OUTPUT"
model_joblib_b64 = "MODELO_ENTRENADO_CODIFICADO_EN_BASE64"
model_metadata_json = 'CONTENIDO_JSON_DE_MODELS_METADATA'

[gdrive_service_account]
type = "service_account"
client_email = "CORREO_DE_LA_CUENTA"
private_key = "CLAVE_PRIVADA_CON_SALTOS_DE_LINEA_ESCAPADOS"
token_uri = "https://oauth2.googleapis.com/token"
```

Para el modo de lectura pública, reemplazá la tabla de cuenta de servicio por `gdrive_api_key` en el nivel superior. Los Secrets del modelo se construyen con los bytes de `models/model.joblib` codificados en base64 y el texto JSON de `models/metadata.json`. Cargá únicamente un modelo entrenado de confianza.

El dashboard conserva el modo local si no se configuró Drive. Si Drive se configura, los errores se informan en pantalla. La app selecciona el CSV compatible por fecha de modificación, valida sus columnas y conserva una caché de cinco minutos. Inference utiliza el modelo cuando el SHA-256 del CSV coincide con sus metadatos.

Al migrar a otro repositorio, configurá los Secrets directamente en el nuevo despliegue, sin incluirlos en Git. Comprobá ambas vistas y actualizá los datos desde el botón de la barra lateral. No publiques credenciales ni modelos de procedencia no verificada.
