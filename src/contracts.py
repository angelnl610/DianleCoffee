import csv
import io
import json
from hashlib import sha256


def csv_text(rows, fields):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="")


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()
