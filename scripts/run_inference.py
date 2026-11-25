import argparse
from pathlib import Path

from config import CLEAN, MODEL, RESULTS
from src.contracts import csv_text, digest, read_csv, write_json, write_text


def main():
    parser = argparse.ArgumentParser(description="Evalúa por lote consultas reales en CSV.")
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    if not MODEL.is_file() or not CLEAN.is_file():
        raise SystemExit("Falta el modelo entrenado o el lote limpio.")
    from src.inference import load_model
    from src.operations import infer_batch
    bundle = load_model()
    if bundle["metadata"]["sha256"] != digest(CLEAN):
        raise SystemExit("Modelo de otro lote. Entrená de nuevo.")
    rows = infer_batch(read_csv(args.csv), bundle)
    output = RESULTS / "consultas.csv"
    fields = list(dict.fromkeys(key for row in rows for key in row)) or ["fila"]
    write_text(output, csv_text(rows, fields))
    write_json(output.with_suffix(".json"), {
        "version": bundle["metadata"]["version"], "filas": len(rows),
        "errores": sum("error" in row for row in rows), "sha256_consultas": digest(args.csv)})
    print(output)


if __name__ == "__main__":
    main()
