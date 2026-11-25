from config import RAW, CLEAN, RESULTS, LIMIT
from src.contracts import csv_text, digest, read_csv, write_json, write_text
from src.etl import COLUMNS


def main():
    if not RAW.is_file() or not RAW.with_name("manifest.json").is_file():
        raise SystemExit("Falta el CSV crudo o su manifest. Ver README.md.")
    import json
    manifest = json.loads(RAW.with_name("manifest.json").read_text(encoding="utf-8-sig"))
    if manifest.get("sha256") != digest(RAW):
        raise SystemExit("El SHA-256 del CSV no coincide con el manifest.")
    rows = read_csv(RAW)
    if not 0 < len(rows) <= LIMIT or manifest.get("filas") != len(rows):
        raise SystemExit("Cantidad de filas inválida o distinta del manifest.")
    from src.eda import analytics
    clean, quality, summary = analytics(rows)
    write_text(CLEAN, csv_text(clean, COLUMNS))
    write_json(CLEAN.with_name("quality.json"), {**quality, "sha256_crudo": digest(RAW)})
    write_json(RESULTS / "analytics.json", summary)
    print(quality)


if __name__ == "__main__":
    main()
