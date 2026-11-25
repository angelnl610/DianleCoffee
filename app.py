import base64
import json
import os

import streamlit as st
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

from config import CLEAN, NAME
from src.drive_loader import load_drive_csv, parse_csv
from src.inference import load_model_bytes
from ui.views import explore, evaluate

st.set_page_config(page_title=NAME, page_icon="☕", layout="wide")
st.markdown("""
<style>
[data-testid="stMetric"] {padding: 0.8rem; border: 1px solid rgba(137,91,60,.22); border-radius: 12px;}
[data-testid="stMetricValue"] {font-size: clamp(1.25rem, 2.5vw, 2rem);}
[data-testid="stSidebar"] {border-right: 1px solid rgba(137,91,60,.18);}
.block-container {padding-top: 2.5rem; max-width: 1440px;}
</style>
""", unsafe_allow_html=True)
st.sidebar.title("☕ Dianle Coffee")
st.sidebar.caption("Inteligencia competitiva")
view = st.sidebar.radio("¿Qué querés hacer?", ["Explorar mercado", "Evaluar producto"])
st.title("☕ Dianle Coffee")
st.caption("Conocé la oferta de café envasado y evaluá tu posicionamiento comercial.")


def setting(name):
    value = os.environ.get(name.upper()) if name != "gdrive_service_account" else None
    if value:
        return value
    try:
        return st.secrets.get(name)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return None


@st.cache_data(ttl=300, show_spinner=False)
def remote_data(folder_id, api_key, service_account):
    if service_account:
        try:
            credentials = Credentials.from_service_account_info(
                service_account, scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
        except (ValueError, GoogleAuthError):
            raise ValueError("Credenciales de Google Drive inválidas.") from None
        with AuthorizedSession(credentials) as session:
            return load_drive_csv(folder_id, session=session)
    return load_drive_csv(folder_id, api_key)


@st.cache_resource(show_spinner=False)
def remote_model(encoded_model, metadata_json):
    return load_model_bytes(base64.b64decode(encoded_model, validate=True), json.loads(metadata_json))


def configured_model():
    encoded_model = setting("model_joblib_b64")
    metadata_json = setting("model_metadata_json")
    if not (encoded_model and metadata_json):
        raise ValueError("Configuración incompleta del modelo entrenado.")
    return remote_model(encoded_model, metadata_json)


folder_id = setting("gdrive_folder_id")
api_key = setting("gdrive_api_key")
service_account = setting("gdrive_service_account")
try:
    if folder_id or api_key or service_account:
        if not (folder_id and (api_key or service_account)):
            raise ValueError("Configuración incompleta de Google Drive.")
        if st.sidebar.button("Actualizar datos de Drive"):
            remote_data.clear()
        data, metadata = remote_data(folder_id, api_key, dict(service_account) if service_account else None)
        with st.expander("Fuente y actualización de datos"):
            st.caption(f"Google Drive · {metadata['name']} · {metadata['modifiedTime']}")
        checksum = metadata["sha256"]
    else:
        data, checksum = parse_csv(CLEAN.read_bytes())
        with st.expander("Fuente y actualización de datos"):
            st.caption("Archivo local de desarrollo.")
    if view == "Explorar mercado":
        explore(data)
    else:
        use_secrets = setting("model_joblib_b64") or setting("model_metadata_json")
        evaluate(data, checksum, configured_model if use_secrets else None)
except FileNotFoundError:
    st.info("Todavía no hay un lote procesado. Configurá Drive o generá un lote local.")
except (ValueError, KeyError, OSError) as error:
    st.error(f"No se pudo abrir el lote: {error}")
