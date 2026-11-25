import hashlib
import io
import json
import math

import joblib
import pandas as pd
import sklearn

from config import MODEL, POSITION_THRESHOLD
from src.commercial import inference_advice, simulate
from src.etl import FORMATS, positive

NUMERIC = ["peso_g", "cantidad_capsulas"]
CATEGORICAL = ["formato", "marca", "canal"]
FEATURES = CATEGORICAL + NUMERIC
TARGET = "precio_lista_ars"


def preprocess(frame):
    result = frame[FEATURES].copy()
    for name in NUMERIC:
        result[name] = pd.to_numeric(result[name], errors="coerce")
        applies = result["formato"].eq("capsulas") if name == "cantidad_capsulas" else result["formato"].ne("capsulas")
        result.loc[~applies, name] = 0
    for name in CATEGORICAL:
        result[name] = result[name].fillna("sin dato").astype(str)
    return result


def predict(row, bundle, as_of=None):
    fmt = row.get("formato")
    if fmt not in FORMATS:
        raise ValueError("Formato inválido.")
    dimension = "cantidad_capsulas" if fmt == "capsulas" else "peso_g"
    size = positive(row.get(dimension))
    if not size or (fmt == "capsulas" and not size.is_integer()):
        raise ValueError("Ingresá una cantidad positiva y, para cápsulas, entera.")
    support = bundle["metadata"]["soporte"].get(fmt)
    if support is None:
        raise ValueError("El formato no tiene soporte suficiente en entrenamiento.")
    warnings = []
    if row.get("marca") not in support["marcas"]:
        warnings.append("Marca sin ejemplos de entrenamiento en este formato.")
    if not support["min"] <= size <= support["max"]:
        raise ValueError("La presentación queda fuera del rango observado para este formato.")
    estimate = float(bundle["pipeline"].predict(preprocess(pd.DataFrame(
        [{key: row.get(key) for key in FEATURES}]
    )))[0])
    if estimate <= 0 or not math.isfinite(estimate):
        raise ValueError("El modelo no devolvió una referencia válida.")
    proposal = positive(row.get("precio_propuesto"))
    if row.get("precio_propuesto") not in (None, "") and proposal is None:
        raise ValueError("El precio propuesto debe ser positivo.")
    gap = proposal / estimate - 1 if proposal else None
    position = None
    meta = bundle["metadata"]
    if gap is not None:
        position = ("económico" if gap < -POSITION_THRESHOLD else
                    "elevado" if gap > POSITION_THRESHOLD else "en rango")
    segment = meta.get("test_por_formato", {}).get(fmt)
    error = segment["mae"] if segment else meta["mae_test"]
    if gap is not None and abs(proposal - estimate) <= error:
        warnings.append("La diferencia cabe dentro del error medio observado. Posicionamiento no concluyente.")
    if segment is None or segment["productos"] < 5:
        warnings.append("Hay pocos productos de este formato en evaluación.")
    if not meta.get("supera_mediana_test"):
        warnings.append("En prueba el modelo no mejoró la mediana base.")
    scenario = None
    if any(row.get(field) not in (None, "") for field in
           ("costo_unitario_ars", "unidades", "costo_fijo_ars", "margen_objetivo_pct")):
        scenario = simulate(proposal, row.get("costo_unitario_ars"), row.get("unidades"),
                            row.get("costo_fijo_ars"), row.get("margen_objetivo_pct"))
    evidence, recommendation = inference_advice(
        segment, gap, abs(proposal - estimate) if proposal else None,
        meta.get("supera_mediana_test"), row.get("marca") in support["marcas"],
        observed_on=min(meta["fechas"], default=None), as_of=as_of, scenario=scenario)
    return dict(evidencia=evidence, recomendacion=recommendation, escenario=scenario, referencia_ars=round(estimate, 2), brecha_pct=round(100 * gap, 2) if gap is not None else None,
                posicion=position, posicion_concluyente=False, advertencias=warnings, version=meta["version"],
                modelo=meta["modelo"], mae_test_ars=meta["mae_test"],
                fuentes=meta["fuentes"], fechas=meta["fechas"])


def load_model():
    if not MODEL.is_file() or not MODEL.with_name("metadata.json").is_file():
        raise ValueError("Faltan el modelo entrenado y sus metadatos.")
    metadata = json.loads(MODEL.with_name("metadata.json").read_text(encoding="utf-8"))
    return load_model_bytes(MODEL.read_bytes(), metadata)


def load_model_bytes(content, metadata):
    if metadata.get("schema_version") != 1 or metadata.get("sklearn") != sklearn.__version__:
        raise ValueError("El esquema o la versión de sklearn del modelo no coincide.")
    if metadata.get("sha256_modelo") != hashlib.sha256(content).hexdigest():
        raise ValueError("El SHA-256 del modelo no coincide con los metadatos.")
    bundle = joblib.load(io.BytesIO(content))
    expected = {key: value for key, value in metadata.items() if key != "sha256_modelo"}
    if bundle["metadata"] != expected:
        raise ValueError("Los metadatos del artefacto y del archivo JSON difieren.")
    return bundle
