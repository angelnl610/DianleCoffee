import pytest

from src.operations import execute, validate


def test_actor_analytics_returns_quality_for_empty_result():
    payload = {"operation": "analytics", "batch_id": "prueba", "origen": {"fuente": "fixture"}, "rows": [{}]}
    result = execute(payload)
    assert result["OUTPUT"]["status"] == "sin_resultados"
    assert result["QUALITY"]["entrada"] == 1
    assert result["ANALYTICS"]["ofertas"] == 0


def test_actor_rejects_nested_row_value():
    with pytest.raises(ValueError, match="escalares"):
        validate({"operation": "analytics", "batch_id": "prueba", "rows": [{"fuente": {}}]})


def test_inference_cannot_acquire():
    with pytest.raises(ValueError, match="exclusiva de Analytics"):
        validate({"operation": "inference", "batch_id": "prueba", "adquirir_sepa": True})


def test_documentation_record_and_frozen_date():
    from src.actor_docs import DOCUMENTATION
    payload = {"operation": "analytics", "batch_id": "docs", "origen": {"fuente": "fixture"},
               "fecha_referencia": "2026-02-02", "rows": [
                   {"fuente": "fixture", "id_oferta": "1", "fecha_observacion": "2026-01-01",
                    "comercio": "A", "nombre_original": "Café molido 250 g", "precio_lista_ars": 100},
               ]}
    records = execute(payload)
    assert records["DOCUMENTACION"] == DOCUMENTATION
    assert records["DOCUMENTACION"]["documentacion"]["metodo"] == "GET"
    assert "DOCUMENTACION" in records["OUTPUT"]["archivos"]
    opportunity, = records["ANALYTICS"]["oportunidades"]
    assert opportunity["antiguedad_dias"] == 32 and opportunity["evidencia"] == "limitada"
    assert opportunity["cobertura_unitaria_pct"] == 100


def test_invalid_reference_date_fails_before_processing():
    with pytest.raises(ValueError, match="fecha_referencia"):
        execute({"operation": "analytics", "batch_id": "docs", "origen": {"fuente": "fixture"},
                 "fecha_referencia": "20260202", "rows": [{}]})
