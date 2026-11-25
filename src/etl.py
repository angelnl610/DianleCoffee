import re
import unicodedata
from datetime import date
from math import isfinite

FORMATS = {"molido": (1000, "ARS/kg"), "grano": (1000, "ARS/kg"),
           "instantaneo": (100, "ARS/100 g"), "capsulas": (1, "ARS/cápsula")}
FIELDS = ("id_oferta id_producto nombre_original marca comercio fuente canal region "
          "granularidad fecha_observacion fecha_extraccion url precio_lista_ars "
          "precio_promo_ars condiciones_promocion estado_promocion").split()
COLUMNS = FIELDS + ("nombre_normalizado formato peso_g cantidad_capsulas cantidad_pack tostado_torrado descafeinado "
                    "precio_efectivo_ars descuento_pct unidad precio_unitario grupo_producto").split()


def normalize(value):
    return "".join(c for c in unicodedata.normalize("NFKD", str(value or "").lower())
                   if not unicodedata.combining(c)).strip()


def positive(value):
    try:
        number = float(value)
        return number if number > 0 and isfinite(number) else None
    except (ValueError, TypeError, OverflowError):
        return None


def classify(name):
    name = normalize(name)
    if not re.search(r"\bcafe\b", name) or re.search(
        r"\b(cafetera\w*|filtro\w*|reutilizable\w*|combo\w*|sucedaneo\w*|bebida\w*|instantanea)\b", name
    ):
        return None
    for pattern, label in [(r"\bcapsulas?\b", "capsulas"),
                           (r"\b(soluble|instantaneo|liofilizado)\b", "instantaneo"),
                           (r"\bgranos?\b", "grano"), (r"\bmolido\b", "molido")]:
        if re.search(pattern, name):
            return label
    return None


def dimensions(name, fmt):
    name = normalize(name)
    weight_unit = r"kgm?|grm|gr?s?"
    pack = re.search(rf"\b(\d+)\s*[x×]\s*\d+(?:[.,]\d+)?\s*(?:{weight_unit})\b", name)
    pack_count = int(pack[1]) if pack else None
    if fmt == "capsulas":
        match = re.search(r"\b(\d+)\s*(?:capsulas?|unidades?|uni|un|u)\b", name)
        if not match:
            match = re.search(r"\bcapsulas?\s*x\s*(\d+)\b", name)
        return None, int(match[1]) if match else None, None
    match = re.search(rf"\b(\d+(?:[.,]\d+)?)\s*({weight_unit})\b", name)
    if not match:
        return None, None, pack_count
    weight = float(match[1].replace(",", ".")) * (1000 if match[2] in ("kg", "kgm") else 1)
    return weight * (pack_count or 1), None, pack_count


def transform(rows):
    clean, excluded, seen = [], {}, set()
    for raw in rows:
        row = {field: raw.get(field) or None for field in FIELDS}
        if row["fuente"] == "SEPA derivado" and row["region"] == "CABA" and (
            str(row["url"]).startswith("https://hysmarcos.github.io/superprecios-claros/v1/sku/")
            and str(row["url"]).endswith("/AMBA.json")
        ):
            row["region"] = "AMBA"
        name = normalize(row["nombre_original"])
        fmt = classify(name)
        price = positive(row["precio_lista_ars"])
        key = (row["fuente"], row["id_oferta"], row["fecha_observacion"])
        reason = None
        try:
            date.fromisoformat(str(row["fecha_observacion"]))
        except ValueError:
            reason = "fecha_invalida"
        if not all(key) or not row["comercio"]:
            reason = "identidad_incompleta"
        elif not price:
            reason = "precio_invalido"
        elif not fmt:
            reason = "formato_no_verificado"
        elif key in seen:
            reason = "duplicado"
        if reason:
            excluded[reason] = excluded.get(reason, 0) + 1
            continue
        seen.add(key)
        weight, capsules, pack = dimensions(name, fmt)
        denominator = capsules if fmt == "capsulas" else weight
        factor, unit = FORMATS[fmt]
        promo = positive(row["precio_promo_ars"])
        general = normalize(row["condiciones_promocion"]) == "general"
        effective = min(price, promo) if general and promo else price
        tostado = re.search(r"\b(torrado|tostado)\b", name)
        product = ("ean:" + str(row["id_producto"]) if row["id_producto"] and str(row["id_producto"]).isdigit() else
                   "heuristica:" + "|".join(map(str, (normalize(row["marca"]), name, fmt, weight, capsules))))
        row.update(nombre_normalizado=name, formato=fmt, peso_g=weight,
                   cantidad_capsulas=capsules, cantidad_pack=pack, grupo_producto=product,
                   tostado_torrado=tostado[1] if tostado else None,
                   descafeinado=True if re.search(r"\bdescafeinado\b", name) else None,
                   precio_lista_ars=price, precio_promo_ars=promo, precio_efectivo_ars=effective,
                   descuento_pct=100 * (1 - promo / price) if promo and promo < price else None,
                   unidad=unit, precio_unitario=price * factor / denominator if denominator else None)
        clean.append(row)
    return clean, {"entrada": len(clean) + sum(excluded.values()), "salida": len(clean),
                   "exclusiones": excluded,
                   "faltantes": {field: sum(row[field] is None for row in clean) for field in COLUMNS}}
