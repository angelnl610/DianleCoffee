"""Ejecuta el SDK de Apify sobre almacenamiento temporal local."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from config import ROOT
from src.operations import execute


def main():
    workspace = ROOT / "data/integracion"
    for operation in ("analytics", "inference"):
        payload = json.loads((workspace / f"{operation}.json").read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "key_value_stores/default"
            store.mkdir(parents=True)
            if operation == "inference":
                # Supuestos aislados para probar que el SDK conserva el contrato del simulador.
                sample = {**payload["rows"][0], "precio_propuesto": 100, "costo_unitario_ars": 80,
                          "unidades": 10, "costo_fijo_ars": 250, "margen_objetivo_pct": 20}
                payload["rows"].append(sample)
            (store / "INPUT.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            environment = {key: value for key, value in os.environ.items()
                           if not key.startswith(("APIFY_", "ACTOR_", "CRAWLEE_"))}
            environment["APIFY_LOCAL_STORAGE_DIR"] = directory
            environment["APIFY_PURGE_ON_START"] = "false"
            environment["CRAWLEE_STORAGE_CLIENT_TYPE"] = "file_system"
            environment["OPENBLAS_NUM_THREADS"] = "1"
            environment["OMP_NUM_THREADS"] = "1"
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            subprocess.run([sys.executable, "-m", "src.main"], cwd=workspace / "actor", env=environment,
                           check=True, timeout=60)
            if operation == "inference":
                actual = json.loads((store / "INFERENCE").read_bytes())
                if (actual[-1]["escenario"]["precio_objetivo_ars"] != 131.25
                        or actual != execute(payload)["INFERENCE"]):
                    raise SystemExit("Distinto: simulador de Inference.")
                actual.pop()
                reference = workspace / "esperado/inference/INFERENCE.json"
                if actual != json.loads(reference.read_bytes()):
                    raise SystemExit("Distinto: inference/INFERENCE.json")
                actual_output = json.loads((store / "OUTPUT").read_bytes())
                if actual_output != execute(payload)["OUTPUT"]:
                    raise SystemExit("Distinto: inference/OUTPUT.json")
                expected_docs = workspace / "esperado/inference/DOCUMENTACION.json"
                if json.loads((store / "DOCUMENTACION").read_bytes()) != json.loads(expected_docs.read_bytes()):
                    raise SystemExit("Distinto: inference/DOCUMENTACION.json")
                print("inference: referencia y escenario coinciden con el SDK local.")
                continue
            for expected in (workspace / "esperado" / operation).iterdir():
                actual = store / expected.stem
                if expected.suffix == ".json":
                    if json.loads(actual.read_bytes()) != json.loads(expected.read_bytes()):
                        raise SystemExit(f"Distinto: {operation}/{expected.name}")
                elif actual.read_bytes() != expected.read_bytes():
                    raise SystemExit(f"Distinto: {operation}/{expected.name}")
        print(f"{operation}: salida del SDK local coincide.")


if __name__ == "__main__":
    main()
