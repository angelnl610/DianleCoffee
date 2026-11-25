from collections import defaultdict
from math import floor, ceil, isnan
from statistics import median

from config import MIN_GROUP, POSITION_THRESHOLD
from src.commercial import insights, opportunity
from src.etl import transform


def present(value):
    return value is not None and not (isinstance(value, float) and isnan(value))


def quantile(ordered, percentile):
    index = (len(ordered) - 1) * percentile
    lower = floor(index)
    return ordered[lower] + (ordered[ceil(index)] - ordered[lower]) * (index - lower)


def analyze(rows, as_of=None):
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(row[field] if present(row[field]) else None for field in
                    ("formato", "fuente", "canal", "region", "fecha_observacion"))
        grouped[key].append(row)
    segments = []
    for (fmt, source, channel, region, day), group in grouped.items():
        comparable = [row for row in group if present(row["precio_unitario"])]
        values = sorted(row["precio_unitario"] for row in comparable)
        q1, q3 = (quantile(values, q) for q in (.25, .75)) if values else (None, None)
        iqr = q3 - q1 if values else None
        reference = median(values) if values else None
        known_promo = sum(r["estado_promocion"] in ("observada", "sin_promocion_reportada") for r in group)
        promo = sum(r["estado_promocion"] == "observada" for r in group)
        below = sum(v <= reference * (1 - POSITION_THRESHOLD) for v in values)
        above = sum(v >= reference * (1 + POSITION_THRESHOLD) for v in values)
        segments.append({"formato": fmt, "fuente": source, "canal": channel, "region": region, "fecha": day,
                         "unidad": group[0]["unidad"], "ofertas": len(group),
                         "productos": len({row["grupo_producto"] for row in group}),
                         "n_unitario": len(values), "mediana": reference, "iqr": iqr,
                         "minimo_unitario": values[0] if values else None,
                         "maximo_unitario": values[-1] if values else None,
                         "promociones_observadas": promo, "estado_promo_conocido": known_promo,
                         "promociones_pct": round(100 * promo / known_promo, 2) if known_promo else None,
                         "productos_unitarios": len({r["grupo_producto"] for r in comparable}),
                         "comercios_unitarios": len({r["comercio"] for r in comparable if present(r["comercio"])}),
                         "debajo_referencia": below, "sobre_referencia": above,
                         "debajo_referencia_pct": round(100 * below / len(values), 2) if values else None,
                         "sobre_referencia_pct": round(100 * above / len(values), 2) if values else None,
                         "atipicos": sum(value < q1 - 1.5 * iqr or value > q3 + 1.5 * iqr for value in values)
                         if len(values) >= MIN_GROUP and iqr else None})
    known = sum(row["estado_promocion"] in ("observada", "sin_promocion_reportada") for row in rows)
    promotions = sum(row["estado_promocion"] == "observada" for row in rows)
    summary = {"promociones_observadas": promotions, "n_estado_promocion": known,
               "proporcion_promociones": promotions / known if known else None,
               "ofertas": len(rows), "segmentos": segments}
    for key, field in (("productos", "grupo_producto"), ("marcas", "marca"), ("comercios", "comercio")):
        summary[key] = len({row[field] for row in rows if present(row[field])})
    summary["oportunidades"] = [opportunity(segment, as_of) for segment in segments]
    summary["insights"] = insights(summary["oportunidades"])
    return summary


def analytics(rows, as_of=None):
    clean, quality = transform(rows)
    return clean, quality, analyze(clean, as_of)
