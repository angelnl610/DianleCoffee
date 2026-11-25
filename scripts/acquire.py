"""Descarga acotada de datos públicos derivados de SEPA."""
import argparse

from config import RAW
from src.acquisition import acquire
from src.contracts import write_json, write_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int, default=50)
    parser.add_argument("--shards", type=int, default=12)
    args = parser.parse_args()
    try:
        csv, manifest = acquire(args.limite, args.shards)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Adquisición interrumpida: {error}\n")
    write_text(RAW, csv)
    write_json(RAW.with_name("manifest.json"), manifest)
    print(f"Guardadas {manifest['filas']} observaciones; {manifest['bytes_descargados']} bytes descargados.")


if __name__ == "__main__":
    main()
