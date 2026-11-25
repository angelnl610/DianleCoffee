from sklearn.feature_selection import mutual_info_regression

from src.inference import FEATURES, NUMERIC, TARGET, preprocess


def feature_signals(frame):
    """Ordena señales del conjunto entregado, sin modificar el modelo."""
    data = preprocess(frame)
    target = frame[TARGET]
    if len(frame) < 10 or target.nunique() < 2:
        return {}
    linear, nonlinear = {}, {}
    for field in FEATURES:
        pair = data[[field]].join(target)
        if field == "peso_g":
            pair = pair.loc[frame["formato"].ne("capsulas")]
        elif field == "cantidad_capsulas":
            pair = pair.loc[frame["formato"].eq("capsulas")]
        pair = pair.dropna()
        if len(pair) < 10 or pair[field].nunique() < 2 or pair[TARGET].nunique() < 2:
            continue
        discrete = field not in NUMERIC
        if discrete and not pair[field].duplicated().any():
            continue
        values = pair[field].factorize()[0] if discrete else pair[field].to_numpy()
        nonlinear[field] = float(mutual_info_regression(
            values.reshape(-1, 1), pair[TARGET], discrete_features=discrete, random_state=42)[0])
        if not discrete:
            linear[field] = float(pair[field].corr(pair[TARGET]))
    top = dict(sorted(linear.items(), key=lambda item: abs(item[1]), reverse=True)[:5])
    other = dict(sorted(((key, value) for key, value in nonlinear.items() if key not in top and value > 0),
                        key=lambda item: item[1], reverse=True)[:5])
    return {"pearson": top, "informacion_mutua": other}
