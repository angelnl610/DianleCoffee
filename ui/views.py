import json

import pandas as pd
import plotly.express as px
import streamlit as st

from config import CLEAN, MODEL, MIN_GROUP, RESULTS, POSITION_THRESHOLD
from src.commercial import evidence, recommendation, simulate
from src.eda import analyze
from src.inference import load_model, predict
from src.signals import feature_signals
from ui.charts import segment_charts, count_chart, price_comparison, scenario_chart, ars, FORMAT_LABELS, show
from ui.commercial import market_decisions


def explore(data):
    st.header("Explorá el mercado")
    st.write("Descubrí qué productos, marcas y comercios aparecen en la muestra y compará sus precios.")
    st.info("Empezá por conocer la oferta, después elegí un segmento para comparar precios y finalmente investigá productos específicos.")
    st.sidebar.subheader("Filtros del mercado")
    st.sidebar.caption("Dejá un filtro vacío para incluir todas sus opciones.")
    st.caption("Fuentes: " + ", ".join(data["fuente"].unique()) + " · Fechas: " +
               ", ".join(sorted(data["fecha_observacion"].unique())))
    filters = {"formato": "Formato", "marca": "Marca", "comercio": "Comercio", "canal": "Canal", "region": "Región",
               "fuente": "Fuente", "fecha_observacion": "Fecha"}
    if st.sidebar.button("Reiniciar filtros"):
        for field in filters:
            st.session_state.pop("filter_" + field, None)
    filtered = data
    for field, label in filters.items():
        selected = st.sidebar.multiselect(label, sorted(data[field].dropna().unique()),
                                          key="filter_" + field, format_func=(lambda value: FORMAT_LABELS.get(value, value)) if field == "formato" else str)
        if selected:
            filtered = filtered[filtered[field].isin(selected)]
    if filtered.empty:
        st.info("Los filtros no devuelven observaciones.")
        return
    st.caption(f"Mostrando {len(filtered)} de {len(data)} ofertas disponibles en el lote.")
    summary = analyze(filtered.to_dict("records"))
    for column, (key, label) in zip(st.columns(4), [
        ("ofertas", "Observaciones"), ("productos", "Productos"), ("marcas", "Marcas"), ("comercios", "Comercios")
    ]):
        definitions = {"ofertas": "Registros de precios observados; un producto puede aparecer varias veces.",
                       "productos": "Productos distintos según su identificador o agrupación.",
                       "marcas": "Marcas distintas con nombre informado.", "comercios": "Comercios distintos incluidos en la muestra."}
        column.metric(label, summary[key], border=True, help=definitions[key])
    st.caption("Producto distinto por ID de origen o agrupación heurística cuando falta. "
               "La frecuencia describe la muestra de precios.")
    st.subheader("1. ¿Qué productos y marcas aparecen en el mercado?")
    left, right = st.columns(2)
    with left:
        count_chart(filtered, "formato", "Formatos de café")
    with right:
        count_chart(filtered, "marca", "Marcas más observadas", limit=10)
    with st.expander("Ver presencia por comercio"):
        count_chart(filtered, "comercio", "Comercios observados")
    st.caption("La presencia en la muestra no equivale a ventas ni participación de mercado.")
    st.divider()
    st.subheader("2. ¿Cuánto cuesta un café comparable?")
    st.write("Elegí un conjunto de ofertas con formato, canal, región, fuente y fecha comparables. Así no mezclamos, por ejemplo, el precio por cápsula con el precio por kilo.")
    segments = filtered.groupby(["formato", "fuente", "canal", "region", "fecha_observacion"], dropna=False)
    groups = dict(tuple(segments))
    selection = st.selectbox("Segmento comparable", list(groups),
                             format_func=lambda key: " · ".join([FORMAT_LABELS.get(key[0], str(key[0])), *map(str, key[1:])]))
    group = groups[selection]
    segment_charts(group, " · ".join(map(str, selection)))
    market_decisions(group, summary)
    with st.expander("Ver tabla de todos los segmentos"):
        st.dataframe(pd.DataFrame(summary["segmentos"]), hide_index=True)
    valid = group.dropna(subset=["precio_unitario"]).copy()
    if len(valid) >= MIN_GROUP:
        median = valid["precio_unitario"].median()
        valid["indice_competitivo"] = valid["precio_unitario"] / median
        valid["brecha_pct"] = (valid["indice_competitivo"] - 1) * 100
        q1, q3 = valid["precio_unitario"].quantile([.25, .75])
        iqr = q3 - q1
        if iqr:
            valid["revisar_atipico"] = (valid["precio_unitario"] < q1 - 1.5 * iqr) | (
                valid["precio_unitario"] > q3 + 1.5 * iqr)
        st.subheader("Precios por debajo de la referencia")
        st.caption(f"Ofertas con precio unitario al menos {POSITION_THRESHOLD:.0%} inferior a la mediana de este segmento (n={len(valid)}). No necesariamente son buenas oportunidades de negocio: revisá sus características.")
        columns = ["nombre_original", "comercio", "precio_unitario", "unidad", "brecha_pct", "indice_competitivo"]
        if iqr:
            columns.append("revisar_atipico")
        cheaper = valid[valid["brecha_pct"] <= -100 * POSITION_THRESHOLD].sort_values("indice_competitivo")
        if cheaper.empty:
            st.info("No hay ofertas por debajo del umbral en este segmento.")
        else:
            st.dataframe(cheaper[columns], hide_index=True, column_config={
                "nombre_original": "Producto", "comercio": "Comercio", "precio_unitario": "Precio unitario",
                "unidad": "Unidad", "brecha_pct": st.column_config.NumberColumn("Diferencia (%)", format="%.1f"),
                "indice_competitivo": st.column_config.NumberColumn("Índice vs. mediana", format="%.2f"),
                "revisar_atipico": "Revisar precio atípico"})
    if summary['n_estado_promocion']:
        st.caption(f"Promociones observadas: {summary['proporcion_promociones']:.1%} entre "
                   f"{summary['n_estado_promocion']} observaciones con estado informado.")
    promotions = filtered[filtered["condiciones_promocion"].notna()]
    if not promotions.empty:
        st.subheader("Promociones observadas")
        st.dataframe(promotions[["nombre_original", "comercio", "condiciones_promocion"]], hide_index=True)
    with st.expander("Cobertura y correlaciones descriptivas"):
        st.dataframe((100 * filtered.notna().mean()).rename("Cobertura (%)"))
        dimension = "cantidad_capsulas" if selection[0] == "capsulas" else "peso_g"
        numeric = group[[dimension, "precio_lista_ars"]].dropna().astype(float)
        if len(numeric) >= MIN_GROUP and numeric.nunique().min() > 1:
            st.dataframe(numeric.corr())
            st.caption(f"Pearson para {len(numeric)} observaciones. Mide asociación lineal.")
        signals = feature_signals(group)
        if signals:
            st.caption("Señales descriptivas del filtro. Información mutua incluye dependencia no lineal.")
            st.json(signals)
    identical = group.dropna(subset=["id_producto", "precio_lista_ars"])
    spread = identical.groupby("id_producto").agg(
        producto=("nombre_original", "first"), comercios=("comercio", "nunique"),
        minimo_ars=("precio_lista_ars", "min"), maximo_ars=("precio_lista_ars", "max"),
    )
    spread = spread[spread["comercios"] >= 2].copy()
    if not spread.empty:
        spread["brecha_ars"] = spread["maximo_ars"] - spread["minimo_ars"]
        with st.expander("Mismo producto en distintos comercios"):
            st.caption("Compara el mismo identificador de origen en el segmento activo.")
            st.dataframe(spread.sort_values("brecha_ars", ascending=False))
    with st.expander("Consultar datos originales y exportar"):
        st.dataframe(filtered, hide_index=True)
        st.download_button("Descargar CSV", filtered.to_csv(index=False), "cafe_filtrado.csv", "text/csv", on_click="ignore")


def evaluate(data, dataset_sha256, model_loader=None):
    st.header("Evaluá tu producto")
    st.write("Compará el precio que pensás ofrecer con una referencia del mercado y, si conocés tus costos, probá un escenario comercial.")
    st.caption("La referencia describe precios de oferta: no pronostica ventas ni garantiza rentabilidad.")
    try:
        bundle = None
        if model_loader:
            bundle = model_loader()
        elif MODEL.is_file():
            bundle = load_model()
    except (OSError, ValueError) as error:
        st.warning(str(error))
        bundle = None
    if bundle and bundle["metadata"]["sha256"] != dataset_sha256:
        st.warning("El modelo corresponde a otro lote. Volvé a entrenarlo.")
        bundle = None
    if not bundle:
        st.info("Modelo pendiente. Ejecutá python -m scripts.train con el lote limpio.")
    formats = sorted(data["formato"].unique())
    st.subheader("1. Definí tu producto")
    fmt = st.selectbox("¿Qué tipo de café querés evaluar?", formats, format_func=lambda value: FORMAT_LABELS.get(value, value))
    if bundle and fmt not in bundle["metadata"]["soporte"]:
        st.info("El modelo no tiene soporte para este formato. Se mostrará la mediana si hay comparables.")
    group = data[data["formato"].eq(fmt)]
    brands = sorted(group["marca"].dropna().unique())
    channel = sorted(group["canal"].dropna().unique())
    dimension = "cantidad_capsulas" if fmt == "capsulas" else "peso_g"
    with st.form("evaluar"):
        left, right = st.columns(2)
        with left:
            brand = st.selectbox("Marca (opcional)", [None, *brands], format_func=lambda x: x or "Sin indicar")
        with right:
            observed_channel = st.selectbox("Canal de venta (opcional)", [None, *channel], format_func=lambda x: x or "Sin indicar")
        sizes = group[dimension].dropna()
        default_size = max(1, int(sizes.mode().iloc[0])) if not sizes.empty else (10 if fmt == "capsulas" else 250)
        left, right = st.columns(2)
        with left:
            size = st.number_input("Cantidad de cápsulas" if fmt == "capsulas" else "Peso del envase (g)", min_value=1,
                                   value=default_size, step=1, key=f"size_{fmt}")
        with right:
            proposal = st.number_input("¿A qué precio querés venderlo? (ARS)", min_value=0.0, value=None,
                                       help="Opcional. Si lo dejás vacío, solo se mostrará la referencia del mercado.")
        with st.expander("Opcional · Simulá tus costos y ganancias"):
            st.caption("Son tus propios supuestos, no estimaciones de demanda. Los costos fijos y unidades deben corresponder al mismo período.")
            left, right = st.columns(2)
            with left:
                cost = st.number_input("Costo variable por unidad (ARS)", min_value=0.0, value=None, help="Lo que cuesta producir o comprar, envasar y vender una unidad.")
                fixed = st.number_input("Costos fijos del período (ARS)", min_value=0.0, value=None, help="Alquiler, sueldos fijos y otros gastos que no cambian con el volumen.")
            with right:
                units = st.number_input("Unidades que estimás vender", min_value=0, value=None, step=1, help="Cantidad supuesta para el mismo período que los costos fijos; no es una predicción.")
                target = st.number_input("Margen objetivo (%)", min_value=0.0, max_value=99.99, value=None, help="Porcentaje de los ingresos que querés conservar después de los costos ingresados.")
        submitted = st.form_submit_button("Comparar con el mercado", type="primary", use_container_width=True)
    state_key = "last_product_evaluation"
    if submitted:
        st.session_state[state_key] = (dataset_sha256, fmt, brand, observed_channel, size, proposal, cost, units, fixed, target)
    previous = st.session_state.get(state_key)
    has_result = previous is not None and previous[:2] == (dataset_sha256, fmt)
    if has_result:
        _, _, brand, observed_channel, size, proposal, cost, units, fixed, target = previous
    if not has_result:
        st.info("Completá el producto y seleccioná Comparar con el mercado para ver el resultado.")
    if has_result:
        st.divider()
        st.caption(f"Última evaluación enviada · {FORMAT_LABELS.get(fmt, fmt)} · {size} {'cápsulas' if fmt == 'capsulas' else 'g'}. Volvé a comparar para aplicar cambios del formulario.")
        st.subheader("2. Tu precio frente al mercado")
        comparable = group[group[dimension].eq(size)]
        if observed_channel:
            comparable = comparable[comparable["canal"].eq(observed_channel)]
        query = {"formato": fmt, "marca": brand, "canal": observed_channel,
                 dimension: size, "precio_propuesto": proposal}
        result = None
        if bundle and fmt in bundle["metadata"]["soporte"]:
            try:
                result = predict(query, bundle)
                price_comparison(result["referencia_ars"], proposal, result["posicion"], result["brecha_pct"])
                with st.expander("Cómo se obtuvo la referencia"):
                    st.caption(f"Modelo {result['modelo']} · {result['version']} · Error absoluto medio en test: "
                               f"{ars(result['mae_test_ars'])} · {', '.join(result['fechas'])}")
                    st.caption("El error medio no es un intervalo de confianza ni una garantía de precisión.")
                for notice in result["advertencias"]:
                    st.warning(notice)
            except ValueError as error:
                st.warning(str(error))
        if result is None and not comparable.empty:
            price_comparison(float(comparable["precio_lista_ars"].median()), proposal, None, None,
                             label="Mediana de ofertas comparables")
            st.caption(f"Referencia de {len(comparable)} observaciones con el mismo tamaño y formato.")
        if result is None and comparable.empty:
            st.info("No podemos obtener una referencia para esta combinación. Probá otro tamaño o canal.")
        market_evidence = evidence(len(comparable), int(comparable["grupo_producto"].nunique()),
                                   int(comparable["comercio"].nunique()),
                                   observed_on=comparable["fecha_observacion"].dropna().min()
                                   if not comparable["fecha_observacion"].dropna().empty else None)
        st.subheader("3. ¿Qué tan respaldada está la comparación?")
        a, b, c = st.columns(3)
        a.metric("Ofertas comparables", len(comparable), border=True)
        b.metric("Comercios", comparable["comercio"].nunique(), border=True)
        c.metric("Evidencia", market_evidence["nivel"].capitalize(), border=True)
        st.caption("Se consideran ofertas con el mismo formato y tamaño; el canal se filtra si lo indicás.")
        explanations = {"suficiente": "La muestra alcanza los mínimos definidos de cobertura y actualidad; no garantiza precisión.",
                        "limitada": "Hay algunos comparables, pero conviene reunir más información antes de decidir.",
                        "insuficiente": "No hay respaldo reciente suficiente para una decisión comercial."}
        st.markdown("**Qué significa la evidencia:** " + explanations.get(market_evidence["nivel"], ""))
        if market_evidence["antiguedad_dias"] is not None:
            st.caption(f"Antigüedad de la observación más antigua: {market_evidence['antiguedad_dias']} días.")
        for reason in market_evidence["motivos"]:
            st.caption(reason)
        scenario = None
        if any(value is not None for value in (cost, units, fixed, target)):
            try:
                scenario = simulate(proposal, cost, units, fixed, target)
                st.subheader("4. Resultado de tu escenario comercial")
                scenario_chart(scenario)
                st.caption("El resultado depende de que se cumplan los costos, precios y unidades ingresados.")
                if scenario["margen_pct"] is not None:
                    st.metric("Margen del escenario", f"{scenario['margen_pct']:.2f}%", border=True)
                if scenario["precio_objetivo_ars"] is not None:
                    st.metric("Precio para alcanzar tu margen objetivo", ars(scenario["precio_objetivo_ars"]), border=True)
            except ValueError as error:
                st.warning(str(error))
        median = float(comparable["precio_lista_ars"].median()) if not comparable.empty else None
        gap = result["brecha_pct"] if result else None
        support = result["evidencia"] if result and market_evidence["nivel"] == "suficiente" else market_evidence
        advice = recommendation(support, gap / 100 if gap is not None else None, scenario, median,
                                proposal if proposal and proposal > 0 else None)
        st.subheader("¿Qué conviene revisar antes de decidir?")
        st.info(advice)
        export = {"consulta": query, "evaluacion": result, "evidencia_comparables": market_evidence,
                  "mediana_comparables_ars": median,
                  "recomendacion": advice, "escenario": scenario}
        st.download_button("Descargar evaluación JSON", json.dumps(export, ensure_ascii=False, indent=2),
                           "evaluacion_dianle.json", "application/json", on_click="ignore")
        st.subheader("Presentaciones de igual formato y tamaño")
        if comparable.empty:
            st.info("No hay presentaciones observadas con esa combinación.")
        else:
            prices = comparable["precio_lista_ars"].dropna()
            if not prices.empty:
                a, b, c = st.columns(3)
                a.metric("Menor precio observado", ars(prices.min()), border=True)
                b.metric("Mediana observada", ars(prices.median()), border=True)
                c.metric("Mayor precio observado", ars(prices.max()), border=True)
                fig = px.strip(comparable, x="precio_lista_ars", y="comercio", hover_name="nombre_original",
                               labels={"precio_lista_ars": "Precio por envase (ARS)", "comercio": "Comercio"},
                               title="¿A qué precios se ofrecen productos similares?")
                fig.update_traces(marker_color="#895B3C", marker_size=8)
                if proposal is not None and proposal > 0:
                    fig.add_vline(x=proposal, line_dash="dash", line_color="#42765C", annotation_text="Tu precio")
                show(fig, max(280, 34 * comparable["comercio"].nunique() + 120))
                st.caption("Cada punto representa una oferta del mismo formato y tamaño. La línea marca tu precio si lo ingresaste.")
            st.dataframe(comparable[["nombre_original", "comercio", "fuente",
                                     "fecha_observacion", "precio_lista_ars"]].head(25), hide_index=True,
                         column_config={"nombre_original": "Producto", "comercio": "Comercio", "fuente": "Fuente",
                                        "fecha_observacion": "Fecha", "precio_lista_ars": "Precio de lista (ARS)"})
    if bundle:
        with st.expander("Información técnica · rendimiento del modelo"):
            if not bundle["metadata"].get("supera_mediana_test"):
                st.caption("La referencia seleccionada no mejoró la mediana de entrenamiento en test.")
            scores = bundle["metadata"]["metricas"]
            st.dataframe(pd.DataFrame({name: value["test"] for name, value in scores.items()}).T)
            st.caption("El MAE mide errores observados. No indica un intervalo ni garantiza un precio rentable. "
                       "La evaluación separa productos, pero cubre un solo día y canal en este lote.")
            st.dataframe(pd.DataFrame(bundle["metadata"].get("test_por_formato", {})).T)
            st.write("Selección exploratoria de características en entrenamiento")
            st.json(bundle["metadata"]["senales_train"])
            path = RESULTS / "inference.csv"
            if path.is_file():
                results = pd.read_csv(path)
                st.plotly_chart(px.scatter(results, x="precio_lista_ars", y="predicho_ars",
                                           title="Precios reales y predichos en test (ARS)"))
                st.plotly_chart(px.histogram(results, x="residuo_ars", title="Residuos en test (ARS)"))
            st.json(bundle["metadata"]["permutacion_mae"])

