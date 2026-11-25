"""Indicadores descriptivos y escenarios con supuestos explícitos."""
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_CEILING, localcontext
from math import isfinite

from config import MIN_GROUP, POSITION_THRESHOLD


def evidence(offers, products, merchants=None, *, observed_on=None, as_of=None):
    gaps = []
    today = as_of or datetime.now(timezone.utc).date()
    try:
        age = (today - date.fromisoformat(str(observed_on))).days
    except ValueError:
        age = None
    if offers < MIN_GROUP:
        gaps.append(f"Menos de {MIN_GROUP} observaciones comparables.")
    if products < 5:
        gaps.append("Menos de cinco productos distintos.")
    if merchants is not None and merchants < 2:
        gaps.append("Menos de dos comercios observados.")
    if age is None or age < 0:
        gaps.append("La fecha de observación falta o es inválida.")
    elif age > 30:
        gaps.append(f"Los datos tienen {age} días; el umbral de frescura es de 30 días.")
    insufficient = not offers or not products or age is None or age < 0 or age > 90
    return {"nivel": "insuficiente" if insufficient else "limitada" if gaps else "suficiente",
            "motivos": gaps, "antiguedad_dias": age, "fecha_referencia": today.isoformat(),
            "observaciones": offers, "productos": products, "comercios": merchants}


def recommendation(support, gap=None, scenario=None, comparable_price=None, proposed=None):
    messages = []
    if support["nivel"] != "suficiente":
        messages.append("Reuní comparables recientes antes de fijar el precio.")
    if comparable_price is not None:
        messages.append(f"La mediana comparable es ARS {comparable_price:,.2f}.")
        if proposed is not None:
            messages.append(f"Tu precio queda {100 * (proposed / comparable_price - 1):+.1f}% respecto de esa mediana.")
    if gap is not None:
        messages.append(f"Brecha frente a la referencia del modelo: {gap:+.1%}; tratala como una señal orientativa.")
    if scenario:
        margin = scenario["margen_pct"]
        required = scenario["precio_objetivo_ars"]
        if margin is None:
            messages.append("Ingresá un volumen positivo para evaluar el margen y el precio objetivo.")
        else:
            messages.append(f"Con los costos ingresados, el margen del escenario es {margin:.2f}%.")
            if required is not None and scenario["precio_ars"] < required:
                messages.append(f"Para alcanzar el objetivo, necesitás cobrar al menos ARS {required:,.2f} "
                                "o reducir los costos.")
            elif required is not None:
                messages.append("El escenario alcanza el margen objetivo con los costos ingresados.")
            if required is not None and comparable_price is not None and required > comparable_price:
                messages.append("El precio objetivo supera la mediana comparable; revisá costos y posicionamiento.")
    return " ".join(messages) or "Contrastá la referencia con ofertas equivalentes y verificá tus costos."


def opportunity(segment, as_of=None):
    support = evidence(segment["n_unitario"], segment["productos_unitarios"], segment["comercios_unitarios"],
                       observed_on=segment.get("fecha"), as_of=as_of)
    if support["motivos"]:
        action = "Ampliar evidencia de precios comparables."
    elif segment["debajo_referencia"] and segment["sobre_referencia"]:
        action = "Revisar alternativas económicas y qué atributos explican los precios altos."
    elif segment["debajo_referencia"]:
        action = "Revisar alternativas de catálogo por debajo de la mediana."
    elif segment["sobre_referencia"]:
        action = "Revisar las presentaciones con precio superior a la mediana."
    else:
        action = "Monitorear el segmento y contrastar con nuevas fechas."
    return {**segment, "evidencia": support["nivel"], "motivos": support["motivos"],
            "antiguedad_dias": support["antiguedad_dias"], "fecha_referencia": support["fecha_referencia"],
            "cobertura_unitaria_pct": 100 * segment["n_unitario"] / segment["ofertas"] if segment.get("ofertas") else None,
            "accion": action}


def insights(matrix):
    if not matrix:
        return ["No hay observaciones en el filtro activo."]
    qualified = sum(row["evidencia"] == "suficiente" for row in matrix)
    coverage = sum(row["n_unitario"] for row in matrix)
    total = sum(row["ofertas"] for row in matrix)
    messages = [
        f"{coverage} de {total} observaciones tienen un precio unitario comparable.",
        f"{qualified} de {len(matrix)} segmentos alcanzan el umbral de suficiencia.",
    ]
    below = sum(row["debajo_referencia"] for row in matrix if row["evidencia"] == "suficiente")
    if below:
        messages.append(f"{below} observaciones quedan al menos {POSITION_THRESHOLD:.0%} por debajo "
                        "de su mediana de segmento con evidencia suficiente.")
    else:
        messages.append("El filtro no muestra oportunidades por debajo del umbral con evidencia suficiente.")
    return messages


def simulate(price, cost, units, fixed, target=None):
    try:
        price, cost, units, fixed = map(float, (price, cost, units, fixed))
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("Completá los supuestos del escenario con números válidos.") from error
    if not all(map(isfinite, (price, cost, units, fixed))) or price <= 0 or min(cost, units, fixed) < 0 or not units.is_integer():
        raise ValueError("Ingresá precio positivo, costos no negativos y unidades enteras no negativas.")
    if target not in (None, ""):
        try:
            target = float(target)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("El margen objetivo debe estar entre 0% y menos de 100%.") from error
        if not 0 <= target < 100:
            raise ValueError("El margen objetivo debe estar entre 0% y menos de 100%.")
    else:
        target = None
    income = price * units
    contribution = (price - cost) * units
    result = contribution - fixed
    if not all(map(isfinite, (income, contribution, result))):
        raise ValueError("Los supuestos superan el rango numérico admitido.")
    required = None
    if units and target is not None:
        with localcontext() as context:
            context.prec = 330
            effective_cost = Decimal(str(cost)) + Decimal(str(fixed)) / Decimal(str(units))
            rounded = (effective_cost / (1 - Decimal(str(target)) / 100)).quantize(
                Decimal("0.01"), rounding=ROUND_CEILING)
            required = float(max(Decimal("0.01"), rounded))
            if not isfinite(required):
                raise ValueError("Los supuestos superan el rango numérico admitido.")
    margin = (result / income) * 100 if income else None
    if margin is not None and not isfinite(margin):
        raise ValueError("Los supuestos superan el rango numérico admitido.")
    return {"margen_pct": round(margin, 2) if margin is not None else None,
            "margen_objetivo_pct": target, "precio_objetivo_ars": required,
            "precio_ars": price, "costo_unitario_ars": cost, "unidades": int(units),
            "costo_fijo_ars": fixed, "ingreso_ars": round(income, 2),
            "contribucion_ars": round(contribution, 2), "resultado_ars": round(result, 2)}


def inference_advice(segment, gap, difference, baseline, brand_known, *, observed_on=None, as_of=None,
                     scenario=None):
    support = evidence(segment["filas"] if segment else 0, segment["productos"] if segment else 0,
                       observed_on=observed_on, as_of=as_of)
    if not baseline:
        support["motivos"].append("El modelo no mejoró la mediana base en prueba.")
    if not brand_known:
        support["motivos"].append("Falta soporte de la marca en entrenamiento.")
    if difference is not None and segment and difference <= segment["mae"]:
        support["motivos"].append("La brecha cabe dentro del error medio del formato.")
    if support["motivos"] and support["nivel"] == "suficiente":
        support["nivel"] = "limitada"
    return support, recommendation(support, gap, scenario)
