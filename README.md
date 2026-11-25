# Dianle Coffee
**Inteligencia competitiva para café envasado** · Equipo Dianle · Samsung Innovation Campus.

Dianle Coffee es un MVP académico de inteligencia competitiva para evaluar alternativas de catálogo y posicionamiento de precios. No predice demanda, ventas ni rentabilidad futura.

- **Analytics — Explorar mercado:** filtros, gráficos de precios, comparación de productos, matriz de oportunidades e insights basados en la oferta observada.
- **Inference — Evaluar producto:** referencia estimada de precio de lista, comparables, advertencias y simulación comercial con supuestos de costos, volumen y margen.

**Tecnologías:** Python, pandas, NumPy, scikit-learn, Streamlit, Plotly, Apify SDK, Docker, Make y Google Drive API.

## 1. Arquitectura y flujo
Fuente derivada de SEPA → adquisición → CSV/manifiesto → ETL y EDA → Analytics; datos limpios → entrenamiento fuera del Actor → modelo persistido → Inference. Make orquesta lotes de Drive hacia un Actor de Apify y recupera sus salidas. Streamlit consume datos locales o un CSV de Google Drive; Inference requiere un modelo compatible con el lote. [Arquitectura y contratos](docs/ARQUITECTURA.md).

## 2. Estructura del repositorio
```text
.actor/       esquemas y configuración del Actor
.github/      pruebas automáticas de GitHub Actions
.streamlit/   tema del dashboard
src/          lógica de datos, modelo y operaciones
ui/           vistas y gráficos
scripts/      adquisición, entrenamiento y verificación
tests/        pruebas automatizadas
data/         lotes y resultados locales (no versionados)
models/       artefacto y metadatos locales (no versionados)
docs/         documentación
app.py        entrada Streamlit
config.py     rutas y límites
Dockerfile    contexto de build del Actor
requirements.txt
```
El repositorio de entrega está preparado para funcionar desde su rama principal, sin depender de ramas de desarrollo. Los datos, modelos generados y credenciales no se versionan; se regeneran o recuperan desde un respaldo autorizado.

## 3. Actor de Apify
Una instancia con operation analytics o inference. SDK de Apify, Dockerfile y esquemas. El modelo se entrena previamente y se empaqueta con su metadata. [Guía Apify](docs/APIFY.md) · [Integración paso a paso](INTEGRACION_PASO_A_PASO.md).

## 4. Funciones y modelo
| Función | Entrada | Salida |
|---|---|---|
| acquire | fuente y límites | CSV + manifest |
| transform | observaciones crudas | filas limpias + calidad |
| analytics | filas crudas | indicadores + limpio + calidad |
| preprocess | características | columnas preparadas |
| train | dataset limpio | modelo + métricas |
| predict | consulta y modelo | referencia y advertencias |
| execute | JSON | registros de salida |

Ridge seleccionado por MAE de validación entre cinco candidatos y mediana base. [Analytics](docs/ANALYTICS.md) · [Inference](docs/INFERENCE.md).

## 5. Contrato del Actor
POST /v2/acts/{actorId}/runs con operation, batch_id, origen, rows; adquisición opcional solo Analytics. GET /v2/key-value-stores/{defaultKeyValueStoreId}/records/DOCUMENTACION tras corrida. Analytics devuelve CAFE_CLEAN, QUALITY, ANALYTICS; Inference devuelve INFERENCE; ambas OUTPUT y DOCUMENTACION. Máximo 2.500 filas y 1 MB por entrada. Ver [contrato](docs/ARQUITECTURA.md). No incluye credenciales.

## 6. Métricas
Lote reportado 15/11/2026: 286 observaciones, 82 productos, 27 marcas, 9 comercios, 250 precios unitarios. Cobertura: supermercados AMBA, una fecha. Test Ridge MAE ARS 6.632,27 vs baseline ARS 8.963,36. KPI de negocio propuesto: reducir 12 a 3 horas semanales (75%, no medido). [Insights](docs/INSIGHTS.md) · [Métricas](docs/METRICAS.md) · [Negocio](docs/NEGOCIO.md).

## 7. Costo computacional y propuesta
Medición cloud pendiente: duración, memoria, CU, créditos y costo por operación. Recursos iniciales 512 MB y 120 s, no rendimiento demostrado. Propuesta piloto USD 2.223, operación objetivo USD 50/mes, ROI proyectado 22,4% anual a 12 meses, sujeto a medición. [Presupuesto y ROI](docs/COSTOS_ROI.md).

## 8. Instalación y ejecución
Requisitos: Python 3.13 y Git (opcional si se descarga el ZIP). Cloná el repositorio de entrega una vez publicado:

```powershell
git clone https://github.com/angelnl610/DianleCoffee.git
cd DianleCoffee
```

También podés descargar el ZIP y abrir su carpeta raíz. Si cambia la cuenta de publicación, usá la URL del botón Code de GitHub.

### Windows (PowerShell)
Python 3.13 x64 con el lanzador `py`:
```powershell
.\preparar_entorno.ps1
.\preparar_datos.ps1
.\verificar_proyecto.ps1 -Sdk
.\ejecutar_demo.ps1
```
### Linux

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# Adquirir solo si no existen el lote crudo y su manifiesto.
python -m scripts.acquire --limite 2000 --shards 32
python -m scripts.run_analytics
python -m scripts.train
python -m scripts.verify_local --sdk
python -m scripts.prepare_integration
streamlit run app.py
```

Abrí http://127.0.0.1:8501. Si restauraste el lote procesado, los resultados y el modelo compatibles, omití `preparar_datos.ps1` en Windows o la adquisición, ETL y entrenamiento en Linux. El script de verificación genera también los archivos para integrar Apify. `preparar_datos.ps1` entrena; una descarga nueva puede cambiar las cifras. Para Linux y detalles: [guía](INTEGRACION_PASO_A_PASO.md). Datos y modelos se regeneran o recuperan de copia autorizada. No cargar archivos joblib no confiables.

### Streamlit Community Cloud
Seleccioná el repositorio de entrega, rama `main`, archivo `app.py` y Python 3.13. Configurá Drive y, para Inference, un modelo entrenado compatible mediante Secrets. No copies credenciales al repositorio. El dashboard anterior no se migra automáticamente al cambiar de repositorio. [Configuración de Drive y Streamlit](docs/DRIVE.md).

### Pruebas
Con el entorno activo, ejecutá `python -m pytest -q`. GitHub Actions ejecuta compilación y pruebas en `main` y las ramas de integración previstas. Para la demo completa, prepará datos y modelo primero.

## Documentación de entrega
[Manual](docs/MANUAL_USUARIO.md) · [Presentación](docs/PITCH.md) · [Trazabilidad](docs/TRAZABILIDAD.md) · [Demo](docs/DEMO.md) · [Checklist](docs/ENTREGA.md) · [Instalación](docs/INSTALACION.md).
Estado: se reportaron 20 pruebas y SDK local en Linux en una versión anterior. El código integrado en `9a45cc5` superó las [pruebas de GitHub Actions](https://github.com/angelnl610/DianleCoffe/actions/runs/45508391260). Esto no certifica Windows, el nuevo despliegue, las corridas externas ni el ROI. Consultá [ESTADO.md](ESTADO.md) y el checklist para evidencia histórica y pendientes de verificación. Desarrollo y documentación asistidos con herramientas de IA; el equipo debe revisar, probar y defender los resultados según las normas del curso.
