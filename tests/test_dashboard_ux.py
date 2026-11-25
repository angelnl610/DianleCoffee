"""Smoke-test both dashboard views using synthetic data, without Drive secrets."""
from streamlit.testing.v1 import AppTest

FIXTURE = """
import pandas as pd
from datetime import date
from src.etl import transform
from ui.views import explore, evaluate

rows = [
    dict(id_oferta=str(i), id_producto=str(1000 + i // 2),
         nombre_original=f"Café molido Marca {i // 2} 250 g",
         marca=f"Marca {i // 2}", comercio=f"Comercio {i % 2}",
         fuente="Prueba", canal="Supermercado", region="AMBA",
         fecha_observacion=date.today().isoformat(),
         precio_lista_ars=10000 + i * 250,
         estado_promocion="sin_promocion_reportada")
    for i in range(12)
]
data = pd.DataFrame(transform(rows)[0])

def unavailable():
    raise ValueError("Modelo no configurado para la prueba")
"""

def test_market_view_renders():
    app = AppTest.from_string(FIXTURE + "\nexplore(data)\n", default_timeout=60).run()
    assert not app.exception
    assert any(metric.label == "Observaciones" and metric.value == "12" for metric in app.metric)

def test_evaluation_and_scenario_render():
    app = AppTest.from_string(
        FIXTURE + '\\nevaluate(data, "test", unavailable)\\n'.replace("\\n", "\n"),
        default_timeout=60,
    ).run()
    assert not app.exception
    values = {
        "¿A qué precio querés venderlo? (ARS)": 12000.0,
        "Costo variable por unidad (ARS)": 8000.0,
        "Costos fijos del período (ARS)": 1000000.0,
        "Unidades que estimás vender": 1000,
        "Margen objetivo (%)": 25.0,
    }
    for field in app.number_input:
        if field.label in values:
            field.set_value(values[field.label])
    next(button for button in app.button if button.label == "Comparar con el mercado").click().run()
    assert not app.exception
    assert any(metric.label == "Resultado del período" and "3.000.000" in metric.value for metric in app.metric)
