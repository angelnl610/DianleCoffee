import math
import warnings
from datetime import datetime, timezone

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import CLEAN, MODEL, RESULTS
from src.contracts import digest, write_json
from src.inference import CATEGORICAL, NUMERIC, FEATURES, TARGET, preprocess


from src.signals import feature_signals


def split(frame, seed):
    splitter = GroupShuffleSplit(n_splits=1, test_size=.25, random_state=seed)
    a, b = next(splitter.split(frame, groups=frame["grupo_producto"]))
    return frame.iloc[a], frame.iloc[b]


def metrics(model, frame):
    prediction = model.predict(preprocess(frame))
    y = frame[TARGET]
    r2 = float(r2_score(y, prediction, force_finite=False)) if y.nunique() > 1 else None
    return dict(mae=float(mean_absolute_error(y, prediction)),
                rmse=float(root_mean_squared_error(y, prediction)),
                r2=r2 if r2 is not None and math.isfinite(r2) else None)


def main():
    if not CLEAN.is_file():
        raise SystemExit("Falta el lote limpio. Ejecutá Analytics primero.")
    data = pd.read_csv(CLEAN, dtype={"id_producto": str})
    if data["grupo_producto"].nunique() < 20:
        raise SystemExit("Se necesitan al menos 20 grupos de producto para este protocolo.")
    development, test = split(data, 42)
    train, validation = split(development, 43)
    candidates = {
        "Mediana": DummyRegressor(strategy="median"),
        "Lineal": LinearRegression(), "Ridge": Ridge(),
        "Random Forest": RandomForestRegressor(n_estimators=80, min_samples_leaf=2, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
        "MLP": TransformedTargetRegressor(
            regressor=MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42),
            transformer=StandardScaler()),
    }
    fitted, scores = {}, {}
    for name, model in candidates.items():
        transform = ColumnTransformer([
            ("cantidad", make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True),
                                       StandardScaler()), NUMERIC),
            ("categoria", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)])
        pipe = make_pipeline(transform, model)
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always", ConvergenceWarning)
            pipe.fit(preprocess(train), train[TARGET])
        fitted[name] = pipe
        scores[name] = {"validacion": metrics(pipe, validation),
                        "aviso_convergencia": any(issubclass(w.category, ConvergenceWarning) for w in captured)}
    best = min(scores, key=lambda name: scores[name]["validacion"]["mae"])
    for name, pipe in fitted.items():
        scores[name]["test"] = metrics(pipe, test)
    winner = fitted[best]
    support = {}
    for fmt, group in train.groupby("formato"):
        dimension = "cantidad_capsulas" if fmt == "capsulas" else "peso_g"
        valid = group.dropna(subset=[dimension])
        if valid["grupo_producto"].nunique() >= 4:
            support[fmt] = {"min": float(valid[dimension].min()), "max": float(valid[dimension].max()),
                            "marcas": sorted(valid["marca"].dropna().unique().tolist())}
    metadata = dict(version=digest(CLEAN)[:12], fecha=datetime.now(timezone.utc).isoformat(),
                    sha256=digest(CLEAN), sklearn=sklearn.__version__, modelo=best, features=FEATURES,
                    schema_version=1, target=TARGET, soporte=support, mae_test=scores[best]["test"]["mae"],
                    fuentes=sorted(data["fuente"].unique()), fechas=sorted(data["fecha_observacion"].unique()),
                    particiones={name: {"filas": len(part), "grupos": int(part["grupo_producto"].nunique())}
                                 for name, part in [("train", train), ("validacion", validation), ("test", test)]},
                    metricas=scores)
    importance = permutation_importance(winner, preprocess(test), test[TARGET],
                                        scoring="neg_mean_absolute_error", n_repeats=8, random_state=42)
    metadata["supera_mediana_test"] = scores[best]["test"]["mae"] < scores["Mediana"]["test"]["mae"]
    metadata["senales_train"] = feature_signals(train)
    metadata["permutacion_mae"] = dict(zip(FEATURES, importance.importances_mean.tolist()))
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    predictions = test[["id_oferta", "formato", "grupo_producto", TARGET]].copy()
    predictions["predicho_ars"] = winner.predict(preprocess(test))
    predictions["residuo_ars"] = predictions[TARGET] - predictions["predicho_ars"]
    predictions.to_csv(RESULTS / "inference.csv", index=False)
    metadata["test_por_formato"] = {
        fmt: {"filas": len(group), "productos": int(group["grupo_producto"].nunique()),
              "mae": float(group["residuo_ars"].abs().mean())}
        for fmt, group in predictions.groupby("formato")
    }
    joblib.dump({"pipeline": winner, "metadata": metadata}, MODEL)
    write_json(MODEL.with_name("metadata.json"), {**metadata, "sha256_modelo": digest(MODEL)})
    print(f"Seleccionado por MAE de validación: {best}. MAE test: {metadata['mae_test']:.2f} ARS.")


if __name__ == "__main__":
    main()
