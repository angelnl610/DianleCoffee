from config import CLEAN, MODEL, RAW
from src.contracts import digest, read_csv
from src.etl import COLUMNS


def main():
    for item in (RAW, CLEAN, MODEL):
        if not item.is_file():
            raise SystemExit(f"Falta {item.name}. Consultá README.md.")
    import plotly
    import streamlit
    import sklearn
    from src.inference import load_model, predict
    rows = read_csv(CLEAN)
    if not rows or set(COLUMNS) - rows[0].keys():
        raise SystemExit("El lote limpio está vacío o tiene columnas faltantes.")
    bundle = load_model()
    meta = bundle["metadata"]
    if meta["sha256"] != digest(CLEAN) or meta["sklearn"] != sklearn.__version__:
        raise SystemExit("El modelo no coincide con el lote o la versión de sklearn.")
    for row in rows:
        try:
            result = predict(row, bundle)
        except ValueError:
            continue
        print(f"Demo verificada con referencia de {result['referencia_ars']:,.2f} ARS. "
              f"Streamlit {streamlit.__version__}; Plotly {plotly.__version__}.")
        return
    raise SystemExit("Ninguna observación del lote admite inferencia con el modelo actual.")


if __name__ == "__main__":
    main()
