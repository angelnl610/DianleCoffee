import hashlib

import pytest

from src.contracts import csv_text
from src.drive_loader import load_drive_csv, parse_csv
from src.etl import COLUMNS


class Response:
    def __init__(self, data=None, content=b""):
        self.data = data
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append((url, dict(params)))
        return next(self.responses)


def test_latest_csv_across_pages():
    content = csv_text([{"id_producto": "001"}], COLUMNS).encode()
    session = Session([
        Response({"nextPageToken": "next", "files": [
            {"id": "old", "name": "cafe_clean.csv", "modifiedTime": "2026-01-01T00:00:00Z"}]}),
        Response({"files": [
            {"id": "latest", "name": "batch_cafe_clean.csv", "modifiedTime": "2026-02-01T00:00:00Z"},
            {"id": "ignore", "name": "raw.csv", "modifiedTime": "2026-03-01T00:00:00Z"}]}),
        Response(content=content),
    ])
    data, metadata = load_drive_csv("folder", "test-key", session)
    assert data.iloc[0]["id_producto"] == "001"
    assert metadata["sha256"] == hashlib.sha256(content).hexdigest()
    assert session.calls[1][1]["pageToken"] == "next"
    assert session.calls[-1][0].endswith("/latest")


def test_empty_folder():
    with pytest.raises(ValueError, match="OUTPUT"):
        load_drive_csv("folder", "test-key", Session([Response({"files": []})]))


def test_invalid_columns():
    with pytest.raises(ValueError, match="Faltan columnas"):
        parse_csv(b"id_producto\n001\n")
