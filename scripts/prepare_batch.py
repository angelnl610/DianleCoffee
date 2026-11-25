import argparse
import json
from pathlib import Path

from config import RAW, LIMIT, MAX_BYTES
from src.contracts import digest, read_csv, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["analytics", "inference"])
    parser.add_argument("--csv", type=Path, default=RAW)
    parser.add_argument("--manifest", type=Path, default=RAW.with_name("manifest.json"))
    parser.add_argument("--out", type=Path, default=Path("data/entrada_actor.json"))
    parser.add_argument("--limite", type=int, default=50)
    args = parser.parse_args()
    if not 0 < args.limite <= LIMIT:
        parser.error("Límite inválido.")
    source = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    if source.get("sha256") != digest(args.csv):
        raise SystemExit("El manifest no coincide con el CSV.")
    rows = read_csv(args.csv)[:args.limite]
    batch = dict(operation=args.operation, batch_id=digest(args.csv)[:12], rows=rows,
                 origen={key: source.get(key) for key in (
                     "fuente", "fecha_observacion", "fecha_extraccion", "manifest_url", "sha256")})
    if not rows or len(json.dumps(batch, ensure_ascii=False, indent=2).encode()) > MAX_BYTES:
        raise SystemExit("Lote vacío o mayor de 1 MB. Revisá el límite.")
    write_json(args.out, batch)
    print(args.out)


if __name__ == "__main__":
    main()
