"""Read processed CSVs from Google Drive."""
import io
import re
import hashlib

import pandas as pd
import requests

from google.auth.exceptions import GoogleAuthError

from src.etl import COLUMNS

API = "https://www.googleapis.com/drive/v3/files"
CSV_NAME = re.compile(r"(?:[A-Za-z0-9_-]+_)?cafe_clean(?:_[A-Za-z0-9_-]+)?\.csv$", re.I)


def _get(url, params, session):
    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response
    except (requests.RequestException, GoogleAuthError) as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        raise ValueError(f"Google Drive no disponible (HTTP {status or 'sin respuesta'}).") from None


def parse_csv(content):
    data = pd.read_csv(io.BytesIO(content), dtype={"id_producto": str})
    missing = set(COLUMNS) - set(data.columns)
    if missing:
        raise ValueError("Faltan columnas: " + ", ".join(sorted(missing)))
    if data.empty:
        raise ValueError("El lote no contiene observaciones válidas.")
    return data, hashlib.sha256(content).hexdigest()


def load_drive_csv(folder_id, api_key=None, session=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", folder_id or "") or (not api_key and session is None):
        raise ValueError("Configurá la carpeta y las credenciales de Google Drive.")
    session = requests if session is None else session
    auth_params = {"key": api_key} if api_key else {}
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "fields": "nextPageToken,files(id,name,modifiedTime)",
        "pageSize": 100,
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
        **auth_params,
    }
    files = []
    while True:
        page = _get(API, params, session).json()
        files.extend(f for f in page.get("files", []) if CSV_NAME.fullmatch(f["name"]))
        token = page.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token
    if not files:
        raise ValueError("OUTPUT no contiene archivos cafe_clean CSV publicados.")
    latest = max(files, key=lambda f: (f.get("modifiedTime", ""), f["name"], f["id"]))
    content = _get(f"{API}/{latest['id']}", {"alt": "media", "supportsAllDrives": "true", **auth_params}, session).content
    data, checksum = parse_csv(content)
    return data, {"name": latest["name"], "sha256": checksum,
                  "modifiedTime": latest.get("modifiedTime", ""), "source": "Google Drive"}
