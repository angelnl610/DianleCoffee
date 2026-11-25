from datetime import date

import pytest

from src.commercial import evidence, inference_advice, insights, opportunity, simulate
from src.eda import analytics


def test_scenario_and_losses():
    result = simulate(100, 80, 10, 250)
    assert result["ingreso_ars"] == 1000
    assert result["contribucion_ars"] == 200
    assert result["resultado_ars"] == -50
    assert simulate(100, 80, 0, 250)["resultado_ars"] == -250


@pytest.mark.parametrize("args", [(0, 1, 2, 0), (1, 1, 1.5, 0), (1, None, 2, 0), (1, 1, 0, float("inf"))])
def test_invalid_scenario(args):
    with pytest.raises(ValueError):
        simulate(*args)


def test_matrix_counts_only_comparable_observations():
    base = dict(fuente="fixture", fecha_observacion="2026-01-01", comercio="A",
                nombre_original="Café molido 500 g", precio_lista_ars=100)
    rows = [{**base, "id_oferta": "a"}, {**base, "id_oferta": "b", "precio_lista_ars": 200},
            {**base, "id_oferta": "c", "nombre_original": "Café molido"}]
    _, _, summary = analytics(rows, date(2026, 1, 5))
    row, = summary["oportunidades"]
    assert row["n_unitario"] == 2
    assert row["debajo_referencia"] == row["sobre_referencia"] == 1
    assert row["evidencia"] == "limitada"
    assert "2 de 3" in summary["insights"][0]
    assert insights([])


def test_margin_and_target_price():
    result = simulate(100, 80, 10, 250, 20)
    assert result["margen_pct"] == -5
    assert result["precio_objetivo_ars"] == 131.25
    assert simulate(100, 80, 3, 200, 30)["precio_objetivo_ars"] == 209.53
    assert simulate(100, 80, 0, 250, 20)["precio_objetivo_ars"] is None
    with pytest.raises(ValueError, match="margen objetivo"):
        simulate(100, 80, 10, 250, 100)


def test_market_and_model_evidence():
    dates = {"observed_on": "2026-01-01", "as_of": date(2026, 1, 5)}
    assert evidence(8, 5, 2, **dates)["nivel"] == "suficiente"
    assert evidence(8, 5, 1, **dates)["nivel"] == "limitada"
    assert evidence(0, 0, 0, **dates)["nivel"] == "insuficiente"
    assert evidence(8, 5, 2, observed_on="2026-01-01", as_of=date(2026, 2, 2))["nivel"] == "limitada"
    assert evidence(8, 5, 2, observed_on="2026-01-01", as_of=date(2026, 4, 2))["nivel"] == "insuficiente"
    assert evidence(8, 5, 2, observed_on="2026-01-06", as_of=date(2026, 1, 5))["nivel"] == "insuficiente"
    segment = {"filas": 10, "productos": 5, "mae": 100}
    support, _ = inference_advice(segment, .20, 90, True, True, **dates)
    assert support["nivel"] == "limitada"
    support, _ = inference_advice(segment, .20, 110, True, True, **dates)
    assert support["nivel"] == "suficiente"
    assert opportunity({"fecha": dates["observed_on"], "n_unitario": 8, "productos_unitarios": 5,
                        "comercios_unitarios": 2, "debajo_referencia": 1, "sobre_referencia": 1},
                       dates["as_of"])["accion"].startswith("Revisar")


def test_recommendation_integrates_market_costs_and_margin():
    from src.commercial import recommendation

    advice = recommendation({"nivel": "limitada"}, .10, simulate(100, 80, 10, 250, 20), 90, 100)
    assert "mediana comparable" in advice
    assert "+10.0%" in advice and "-5.00%" in advice
    assert "131.25" in advice and "revisá costos" in advice
