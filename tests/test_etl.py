import unittest

from src.etl import classify, dimensions, transform


class TestETL(unittest.TestCase):
    def test_formats_and_units(self):
        self.assertEqual(classify("CAFÉ TOSTADO MOLIDO"), "molido")
        self.assertEqual(classify("Cápsulas reutilizables de café"), None)
        self.assertEqual(dimensions("Café molido 2 x 250 g", "molido"), (500, None, 2))
        self.assertEqual(dimensions("Café cápsulas 52 g", "capsulas"), (None, None, None))
        self.assertEqual(dimensions("Café instantáneo 0,2 kg", "instantaneo"), (200, None, None))

    def test_sepa_units(self):
        self.assertEqual(dimensions("Café molido 2 x 250 GRM", "molido"), (500, None, 2))
        self.assertEqual(dimensions("Café en grano 1 KGM", "grano"), (1000, None, None))
        self.assertEqual(dimensions("Cápsulas de café X 10 UNI", "capsulas"), (None, 10, None))

    def test_original_amba_region_is_recovered(self):
        row = dict(fuente="SEPA derivado", id_oferta="1", fecha_observacion="2026-11-15",
                   comercio="A", nombre_original="Café molido 250 GRM", precio_lista_ars=100,
                   region="CABA", url="https://hysmarcos.github.io/superprecios-claros/v1/sku/1/AMBA.json")
        clean, _ = transform([row])
        self.assertEqual(clean[0]["region"], "AMBA")
        self.assertEqual(row["region"], "CABA")

    def test_counts_and_commerce(self):
        row = dict(fuente="fixture", id_oferta="a", fecha_observacion="2026-01-01",
                   id_producto="001", comercio="A", nombre_original="Café molido 500 g",
                   precio_lista_ars=100, precio_promo_ars=80, condiciones_promocion="tarjeta")
        clean, quality = transform([row, row, {**row, "id_oferta": "b", "comercio": "B"},
                                    {**row, "id_oferta": "c", "precio_lista_ars": 0}])
        self.assertEqual(quality["entrada"], 4)
        self.assertEqual(quality["exclusiones"], {"duplicado": 1, "precio_invalido": 1})
        self.assertEqual(len(clean), 2)
        self.assertEqual(clean[0]["precio_unitario"], 200)
        self.assertEqual(clean[0]["precio_efectivo_ars"], 100)
        self.assertEqual(clean[0]["grupo_producto"], "ean:001")


if __name__ == "__main__":
    unittest.main()
