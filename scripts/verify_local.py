"""Verifica la demo con sus archivos existentes y sin adquirir datos."""
import argparse
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys

import pandas as pd
from streamlit.testing.v1 import AppTest

from config import CLEAN, ROOT
from src.inference import load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", action="store_true", help="Incluye almacenamiento del SDK de Apify local.")
    options = parser.parse_args()
    commands = [("pytest", ["-q"]), ("scripts.check_demo", []), ("scripts.prepare_integration", [])]
    if options.sdk:
        commands.append(("scripts.verify_integration", []))
    for module, args in commands:
        subprocess.run([sys.executable, "-m", module, *args], cwd=ROOT, check=True)
    data = pd.read_csv(CLEAN)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    if app.exception or app.error or int(app.metric[0].value) != len(data):
        raise SystemExit("Falló la vista Analytics.")
    fmt = data["formato"].iloc[0]
    app.sidebar.multiselect(key="filter_formato").select(fmt).run()
    if app.exception or app.error or int(app.metric[0].value) != int(data["formato"].eq(fmt).sum()):
        raise SystemExit("Falló el filtro por formato.")
    app.sidebar.button[0].click().run()
    if app.exception or app.error or int(app.metric[0].value) != len(data):
        raise SystemExit("Falló el reinicio de filtros.")
    segments = data.groupby(["formato", "fuente", "canal", "region", "fecha_observacion"], dropna=False)
    if not any(group["grupo_producto"].nunique() >= 2 for _, group in segments):
        raise SystemExit("El lote no permite verificar la comparación de dos productos.")
    for key, group in segments:
        if group["grupo_producto"].nunique() >= 2:
            app.selectbox[0].set_value(key).run()
            break
    selector = app.multiselect(key="productos_comparados")
    selector.set_value(selector.options[:2]).run()
    if app.exception or app.error or not any(
            "brecha_unitaria_pct" in table.value.columns and len(table.value) == 2 for table in app.dataframe):
        raise SystemExit("Falló la comparación de productos.")
    if not any("condiciones_promocion" in df.value.columns and "comercio" in df.value.columns
               for df in app.dataframe):
        raise SystemExit("Falló el detalle de promociones por comercio.")
    app.sidebar.radio[0].set_value("Evaluar producto").run()
    fmt, support = next(iter(load_model()["metadata"]["soporte"].items()))
    app.selectbox[0].set_value(fmt).run()
    app.number_input[0].set_value(int(support["min"]))
    app.number_input[1].set_value(10000.0)
    app.number_input[2].set_value(7000.0)
    app.number_input[3].set_value(3)
    app.number_input[4].set_value(2000.0)
    app.number_input[5].set_value(40.0)
    app.button[0].click().run()
    if app.exception or app.error or not any("Referencia de lista" in metric.label for metric in app.metric):
        raise SystemExit("Falló el formulario de inferencia.")
    if not any(metric.label == "Resultado del escenario (ARS)" and metric.value == "7,000.00"
               for metric in app.metric) or not app.get("download_button"):
        raise SystemExit("Falló el simulador o la exportación.")
    if not any(metric.label == "Precio para el margen objetivo (ARS)" and metric.value == "12,777.78"
               for metric in app.metric):
        raise SystemExit("Falló el precio del margen objetivo.")
    with tempfile.TemporaryDirectory() as directory:
        with patch("config.CLEAN", Path(directory) / "sin-lote.csv"):
            empty = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        if empty.exception or not empty.info:
            raise SystemExit("Falló el estado sin lote.")
    print("Streamlit: Analytics, filtros, comparación, Inference, simulación, exportación y estado sin lote verificados.")


if __name__ == "__main__":
    main()
