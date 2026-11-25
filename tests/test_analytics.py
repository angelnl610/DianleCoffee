import unittest

from src.eda import analytics


class TestAnalytics(unittest.TestCase):
    def test_groups_and_promotions(self):
        base = dict(fuente="fixture", fecha_observacion="2026-01-01", comercio="A",
                    nombre_original="Café molido 500 g", precio_lista_ars=100)
        rows = [{**base, "id_oferta": "a", "estado_promocion": "observada"},
                {**base, "id_oferta": "b", "precio_lista_ars": 200,
                 "estado_promocion": "sin_promocion_reportada"},
                {**base, "id_oferta": "c", "nombre_original": "Café instantáneo 50 g"}]
        clean, quality, summary = analytics(rows)
        self.assertEqual(len(clean), quality["salida"])
        self.assertEqual(summary["n_estado_promocion"], 2)
        self.assertEqual(summary["proporcion_promociones"], .5)
        self.assertEqual([s["unidad"] for s in summary["segmentos"]], ["ARS/kg", "ARS/100 g"])
        self.assertEqual(summary["segmentos"][0]["mediana"], 300)
        self.assertEqual(summary["segmentos"][0]["iqr"], 100)

    def test_empty(self):
        self.assertEqual(analytics([])[2]["segmentos"], [])
