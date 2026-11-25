"""Contrato de operaciones compartido por el Actor y las pruebas locales."""
import csv
import io
import json
import re
from datetime import date
from src.actor_docs import DOCUMENTATION

from config import LIMIT, MAX_BYTES
from src.acquisition import acquire
from src.contracts import csv_text
from src.eda import analytics
from src.etl import COLUMNS
from src.inference import load_model, predict


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError("El INPUT debe ser un objeto JSON.")
    if len(json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")) > MAX_BYTES:
        raise ValueError("El lote supera 1 MB.")
    operation = payload.get("operation")
    batch_id = payload.get("batch_id")
    rows = payload.get("rows")
    origin = payload.get("origen")
    if operation not in ("analytics", "inference"):
        raise ValueError("Operación inválida.")
    if not isinstance(batch_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", batch_id):
        raise ValueError("batch_id inválido.")
    if payload.get("adquirir_sepa") is True:
        if operation != "analytics" or rows is not None:
            raise ValueError("La adquisición SEPA es exclusiva de Analytics y no admite rows.")
        return operation, batch_id, None
    if not isinstance(rows, list) or not 0 < len(rows) <= LIMIT or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"rows debe contener entre 1 y {LIMIT} objetos.")
    if any(isinstance(value, (list, dict)) for row in rows for value in row.values()):
        raise ValueError("Los campos de cada fila deben ser escalares.")
    if not isinstance(origin, dict) or not origin.get("fuente"):
        raise ValueError("Incluí la fuente en origen.")
    return operation, batch_id, rows


def infer_batch(rows, bundle, as_of=None):
    results = []
    for index, row in enumerate(rows, start=1):
        try:
            results.append({"fila": index, **predict(row, bundle, as_of)})
        except ValueError as error:
            results.append({"fila": index, "error": str(error)})
    return results


def execute(payload):
    operation, batch_id, rows = validate(payload)
    as_of = None
    if "fecha_referencia" in payload:
        try:
            value = payload["fecha_referencia"]
            as_of = date.fromisoformat(value)
            if as_of.isoformat() != value:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("fecha_referencia debe tener formato AAAA-MM-DD.") from None
    acquisition = {}
    if rows is None:
        raw, manifest = acquire(50, 12)
        rows = list(csv.DictReader(io.StringIO(raw)))
        acquisition = {"CAFE_RAW": raw, "MANIFEST": manifest}
    output = dict(operation=operation, batch_id=batch_id, filas_entrada=len(rows))
    if operation == "analytics":
        clean, quality, summary = analytics(rows, as_of)
        records = {**acquisition, "CAFE_CLEAN": csv_text(clean, COLUMNS), "QUALITY": quality, "ANALYTICS": summary}
        valid = len(clean)
    else:
        bundle = load_model()
        results = infer_batch(rows, bundle, as_of)
        records = {"INFERENCE": results}
        valid = sum("error" not in item for item in results)
        output["version"] = bundle["metadata"]["version"]
    records["DOCUMENTACION"] = DOCUMENTATION
    output.update(status="ok" if valid == len(rows) else "parcial" if valid else "sin_resultados",
                  filas_validas=valid, archivos=list(records))
    return {**records, "OUTPUT": output}
