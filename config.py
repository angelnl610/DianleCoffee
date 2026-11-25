from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/cafe_raw.csv"
CLEAN = ROOT / "data/processed/cafe_clean.csv"
RESULTS = ROOT / "data/results"
MODEL = ROOT / "models/model.joblib"
NAME = "Dianle Coffee"
MIN_GROUP = 8
POSITION_THRESHOLD = 0.10
LIMIT = 2500
MAX_BYTES = 1_000_000
