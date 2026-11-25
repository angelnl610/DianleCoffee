"""Descarga acotada de datos públicos derivados de SEPA."""
import json
import random
from datetime import date
from datetime import datetime, timezone
from collections import defaultdict
from urllib.request import urlopen

from hashlib import sha256

from src.contracts import csv_text
from src.etl import FIELDS, classify

BASE = "https://hysmarcos.github.io/superprecios-claros/v1"
REGION = "AMBA"


def download(url):
    with urlopen(url, timeout=8) as response:
        data = response.read(4_000_001)
    if len(data) > 4_000_000:
        raise ValueError("Recurso mayor al límite local.")
    return json.loads(data), len(data)


def acquire(limit, shards):
    if not 1 <= limit <= 2000 or not 1 <= shards <= 32:
        raise ValueError("Límites: 1 a 2000 observaciones y 1 a 32 shards.")
    manifest, downloaded = download(BASE + "/manifest.json")
    try:
        observation_day = manifest["fecha_datos"]
        date.fromisoformat(observation_day)
    except (KeyError, TypeError, ValueError):
        raise ValueError("El manifest no informa una fecha ISO bajo el esquema esperado.") from None
    picked = defaultdict(list)
    extraction_day = datetime.now(timezone.utc).date().isoformat()
    for shard in range(shards):
        url = f"{BASE}/skus/{REGION}/{shard:02}.json"
        payload, size = download(url)
        downloaded += size
        if payload.get("fecha") != observation_day or payload.get("region") != REGION:
            raise ValueError("Fecha o región del listado distinta del manifest.")
        entries = payload["items"].items()
        for ean, item in entries:
            if not isinstance(item, dict) or not str(ean).isdigit():
                continue
            product = item.get("producto", item)
            fmt = classify(product.get("nombre"))
            if fmt:
                picked[fmt].append(str(ean))
    rows, urls = [], []
    for index in range(max(map(len, picked.values()), default=0)):
        for fmt in sorted(picked):
            if index >= len(picked[fmt]) or len(rows) >= limit:
                continue
            ean = picked[fmt][index]
            url = f"{BASE}/sku/{ean}/{REGION}.json"
            detail, size = download(url)
            downloaded += size
            if detail.get("fecha") != observation_day or detail.get("region") != REGION:
                raise ValueError("Fecha o región del SKU distinta del lote esperado.")
            urls.append(url)
            product = detail["producto"]
            offers = sorted(detail["precios"], key=lambda offer: offer["cadena"]["id"])
            random.Random(ean).shuffle(offers)
            for offer in offers:
                if len(rows) >= limit:
                    break
                chain = offer["cadena"]
                rows.append(dict(id_oferta=f"{ean}:{chain['id']}:{REGION}", id_producto=ean,
                                 nombre_original=product["nombre"], marca=product.get("marca"),
                                 comercio=chain["nombre"], fuente="SEPA derivado",
                                 canal="supermercado", region=REGION,
                                 granularidad="agregado por cadena y región",
                                 fecha_observacion=detail["fecha"], fecha_extraccion=extraction_day,
                                 url=url, precio_lista_ars=offer.get("precio_lista"),
                                 condiciones_promocion=json.dumps(offer["promo"], ensure_ascii=False)
                                 if offer.get("promo") is not None else None,
                                 estado_promocion=("observada" if offer["promo"] is not None else
                                                    "sin_promocion_reportada") if "promo" in offer else None))
        if len(rows) >= limit:
            break
    if not rows:
        raise ValueError("Sin observaciones verificables. Se conserva cualquier lote anterior.")
    csv = csv_text(rows, FIELDS)
    raw = csv.encode("utf-8")
    return csv, {
        "fuente": "superprecios-claros, derivado de SEPA", "urls": urls,
        "manifest_url": BASE + "/manifest.json", "manifest_original": manifest,
        "fecha_observacion": observation_day, "fecha_extraccion": extraction_day,
        "region": REGION, "granularidad": "agregado por cadena y región",
        "filas": len(rows), "filtro": f"AMBA según fuente, {shards} shards iniciales",
        "reutilizacion": "Código del derivador MIT. Datos sujetos a términos de Precios Claros.",
        "terminos": "https://www.preciosclaros.gob.ar/terminos_y_condiciones.html",
        "sha256": sha256(raw).hexdigest(), "bytes": len(raw), "bytes_descargados": downloaded}
