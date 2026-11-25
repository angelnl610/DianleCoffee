"""Genera entradas reales, resultados de referencia y contexto privado del Actor."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config import CLEAN, MODEL, RAW, RESULTS, ROOT
from src.contracts import digest, read_csv, write_json, write_text
from src.inference import load_model, predict
from src.operations import execute


def main():
    output = ROOT / "data/integracion"
    manifest = json.loads(RAW.with_name("manifest.json").read_text(encoding="utf-8-sig"))
    if manifest["sha256"] != digest(RAW) or manifest["filas"] != len(raw_rows := read_csv(RAW)):
        raise SystemExit("El lote crudo no coincide con el manifiesto.")
    bundle = load_model()
    if bundle["metadata"]["sha256"] != digest(CLEAN):
        raise SystemExit("Entrená el modelo con el lote limpio actual.")
    raw_subset = raw_rows[:50]
    test_ids = set(pd.read_csv(RESULTS / "inference.csv", dtype=str)["id_oferta"])
    queries = []
    for row in read_csv(CLEAN):
        if row["id_oferta"] not in test_ids:
            continue
        query = {key: row[key] for key in ("formato", "marca", "canal", "peso_g", "cantidad_capsulas")}
        try:
            predict(query, bundle)
        except ValueError:
            continue
        if query not in queries:
            queries.append(query)
        if len(queries) == 5:
            break
    if not queries:
        raise SystemExit("El conjunto de prueba carece de consultas admitidas.")
    for operation, rows in (("analytics", raw_subset), ("inference", queries)):
        origin = {"fuente": manifest["fuente"], "fecha_observacion": manifest["fecha_observacion"],
                  "sha256_csv_origen": digest(RAW if operation == "analytics" else CLEAN)}
        rows_hash = hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        payload = dict(operation=operation, batch_id=f"{operation}-{rows_hash[:12]}", origen=origin, rows=rows,
                       fecha_referencia=datetime.now(timezone.utc).date().isoformat())
        write_json(output / f"{operation}.json", payload)
        for key, value in execute(payload).items():
            directory = output / "esperado" / operation
            if isinstance(value, str):
                write_text(directory / f"{key}.csv", value)
            else:
                write_json(directory / f"{key}.json", value)

    context = output / "actor"
    sources = [Path(name) for name in ("Dockerfile", ".dockerignore", "requirements.txt", "config.py", "README.md")]
    sources += [path.relative_to(ROOT) for path in sorted((ROOT / "src").glob("*.py"))]
    sources += [path.relative_to(ROOT) for path in sorted((ROOT / ".actor").glob("*.json"))]
    sources += [Path("models/model.joblib"), Path("models/metadata.json")]
    for path in sources:
        destination = context / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
        if digest(destination) != digest(ROOT / path):
            raise SystemExit(f"Copia inválida: {path}")
    deliverables = [RAW, RAW.with_name("manifest.json"), CLEAN, CLEAN.with_name("quality.json"),
                    RESULTS / "analytics.json", RESULTS / "inference.csv", MODEL, MODEL.with_name("metadata.json"),
                    output / "analytics.json", output / "inference.json"]
    deliverables.extend(sorted((output / "esperado").glob("*/*")))
    write_json(output / "manifest_archivos.json", {
        "fecha_observacion": manifest["fecha_observacion"],
        "archivos": [{"ruta": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size}
                     for path in deliverables],
    })
    print(output)


if __name__ == "__main__":
    main()
