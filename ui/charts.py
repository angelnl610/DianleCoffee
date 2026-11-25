import plotly.express as px
import plotly.graph_objects as go
from config import POSITION_THRESHOLD, MIN_GROUP
import streamlit as st

COFFEE = "#895B3C"
GREEN = "#42765C"
SAND = "#D3AC7D"
RED = "#A04A42"
FORMAT_LABELS = {"molido": "Molido", "grano": "En grano", "instantaneo": "Instantáneo", "capsulas": "Cápsulas"}

def ars(value):
    return "ARS $" + f"{value:,.2f}".translate(str.maketrans(",.", ".,"))

def show(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=24, t=48, b=fig.layout.margin.b or 16),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#302119"), title_font_size=17)
    fig.update_layout(separators=",.")
    fig.update_xaxes(gridcolor="#E5DBCD", zerolinecolor="#B8A99B")
    fig.update_yaxes(gridcolor="#E5DBCD")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def count_chart(data, field, title, limit=None):
    counts = data[field].value_counts().rename_axis(field).reset_index(name="observaciones")
    if counts.empty:
        return
    counts["porcentaje"] = 100 * counts["observaciones"] / len(data)
    counts["etiqueta"] = counts.apply(lambda row: f"{row['observaciones']} ({row['porcentaje']:.1f}%)", axis=1)
    if field == "formato":
        counts[field] = counts[field].map(lambda value: FORMAT_LABELS.get(value, value))
    visible = counts.head(limit) if limit else counts
    fig = px.bar(visible.sort_values("observaciones"), x="observaciones", y=field,
                 orientation="h", text="etiqueta", title=title,
                 hover_data={"porcentaje": ":.1f", "etiqueta": False},
                 labels={"observaciones": "Ofertas observadas", field: ""},
                 color_discrete_sequence=[COFFEE])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(range=[0, max(visible["observaciones"]) * 1.4])
    show(fig, max(280, 34 * len(visible) + 100))
    top = counts.iloc[0]
    st.markdown(f"**Cómo leerlo:** {top[field]} aparece en {top['observaciones']} de {len(data)} ofertas ({top['porcentaje']:.1f}%).")
    st.caption("Sirve para identificar dónde hay más ofertas para investigar; no indica qué se vende más."
               + (f" Se muestran {len(visible)} de {len(counts)} categorías." if len(visible) < len(counts) else ""))

def price_comparison(reference, proposal, position, gap, label="Referencia estimada por el modelo"):
    a, b, c = st.columns(3)
    a.metric(label, ars(reference), border=True)
    b.metric("Tu precio", ars(proposal) if proposal is not None and proposal > 0 else "Sin indicar", border=True)
    c.metric("Posición orientativa", str(position).capitalize() if position else "Sin clasificar", border=True,
             help="Clasificación respecto de la referencia del modelo, no de la calidad ni de la rentabilidad.")
    if proposal is not None and proposal > 0:
        fig = px.bar(x=[reference, proposal], y=[label, "Tu precio"], orientation="h",
                     color=[label, "Tu precio"], color_discrete_sequence=[SAND, COFFEE],
                     labels={"x": "Precio por envase (ARS)", "y": ""})
        fig.update_layout(showlegend=False)
        fig.update_traces(hovertemplate="ARS %{x:,.2f}<extra></extra>", texttemplate="%{x:,.0f}", textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, max(reference, proposal) * 1.3])
        show(fig, 230)
        difference = gap if gap is not None else ((proposal / reference - 1) * 100 if reference > 0 else None)
        if difference is not None:
            if abs(difference) < 0.005:
                st.caption("Tu precio coincide con la referencia al redondear a dos decimales.")
            else:
                direction = "por debajo" if difference < 0 else "por encima"
                st.markdown(f"**Qué significa:** tu precio está {abs(difference):.2f}% {direction} de la referencia ({ars(abs(proposal - reference))} de diferencia por envase).")
                st.caption("Un precio menor puede ayudar a competir, pero no demuestra que venderás más ni que tendrás ganancias.")
    else:
        st.caption("Ingresá un precio propio para visualizar la comparación.")

def scenario_chart(scenario):
    a, b, c = st.columns(3)
    a.metric("Ingresos", ars(scenario["ingreso_ars"]), border=True)
    b.metric("Contribución", ars(scenario["contribucion_ars"]), border=True)
    c.metric("Resultado del período", ars(scenario["resultado_ars"]), border=True)
    variable = scenario["costo_unitario_ars"] * scenario["unidades"]
    fixed = scenario["costo_fijo_ars"]
    fig = go.Figure(go.Waterfall(
        x=["Ingresos", "Costos variables", "Contribución", "Costos fijos", "Resultado"],
        measure=["absolute", "relative", "total", "relative", "total"],
        y=[scenario["ingreso_ars"], -variable, 0, -fixed, 0],
        text=[ars(scenario["ingreso_ars"]), ars(variable), ars(scenario["contribucion_ars"]),
              ars(fixed), ars(scenario["resultado_ars"])],
        textposition="outside", increasing={"marker": {"color": GREEN}},
        decreasing={"marker": {"color": RED}}, totals={"marker": {"color": COFFEE}},
        connector={"line": {"color": "#B8A99B"}}, hoverinfo="x+text"))
    fig.update_layout(title="¿Cómo se llega al resultado?", showlegend=False, yaxis_title="ARS")
    show(fig, 380)
    result = scenario["resultado_ars"]
    st.markdown(f"**Cómo leerlo:** a los ingresos se les restan {ars(variable)} de costos variables y {ars(fixed)} de costos fijos.")
    if result > 0:
        st.success(f"Con tus supuestos, quedarían {ars(result)} en el período.")
    elif result < 0:
        st.warning(f"Con tus supuestos, habría una pérdida de {ars(abs(result))} en el período.")
    else:
        st.info("Con tus supuestos, los ingresos cubren exactamente los costos ingresados.")
    contribution_per_unit = scenario["precio_ars"] - scenario["costo_unitario_ars"]
    if contribution_per_unit > 0:
        import math
        ratio = fixed / contribution_per_unit
        if math.isfinite(ratio):
            break_even = math.ceil(ratio)
            st.metric("Unidades para cubrir los costos", f"{break_even:,}".replace(",", "."), border=True,
                      help="Punto de equilibrio: costos fijos divididos por el aporte de cada unidad, redondeado hacia arriba.")
            st.caption("El punto de equilibrio supone precio y costo por unidad constantes.")
        else:
            st.warning("El punto de equilibrio supera el rango numérico disponible.")
    else:
        st.warning("Cada unidad aporta cero o menos a los costos fijos; vender más no soluciona ese escenario.")


def segment_charts(group, label):
    series = group.dropna(subset=["precio_unitario"])
    if series.empty:
        st.info("Sin presentaciones con unidad verificable para comparar.")
        return
    unit = series["unidad"].iloc[0]
    axis = {"precio_unitario": f"Precio de lista ({unit})"}
    median = series["precio_unitario"].median()
    a, b, c = st.columns(3)
    a.metric("Precio unitario de referencia", ars(median), border=True)
    b.metric("Unidad de comparación", str(unit), border=True)
    c.metric("Ofertas con precio unitario", len(series), border=True)
    fig = px.histogram(series, x="precio_unitario", labels=axis, title="¿En qué precios se concentra la oferta?",
                       color_discrete_sequence=[COFFEE])
    fig.add_vline(x=median, line_dash="dash", line_color=GREEN, annotation_text="Mediana")
    show(fig)
    q1, q3 = series["precio_unitario"].quantile([.25, .75])
    st.markdown(f"**Cómo leerlo:** el 50% central de las ofertas se sitúa aproximadamente entre {ars(q1)} y {ars(q3)} ({unit}). La línea indica la mediana, no el promedio.")
    if len(series) >= MIN_GROUP:
        low = median * (1 - POSITION_THRESHOLD)
        high = median * (1 + POSITION_THRESHOLD)
        values = series["precio_unitario"]
        below = int((values <= low).sum())
        above = int((values >= high).sum())
        middle = len(values) - below - above
        st.markdown("**¿Cuántas ofertas son más económicas o más caras?**")
        fig = go.Figure()
        for name, n, color in [("Más económicas", below, "#AE835C"), ("Cercanas a la mediana", middle, "#D3AC7D"), ("Más caras", above, "#6E5140")]:
            fig.add_trace(go.Bar(name=name, x=[n], y=["Ofertas"], orientation="h", marker_color=color,
                                 text=[f"{n} ({n / len(values):.0%})" if n else ""], textposition="inside"))
        fig.update_layout(barmode="stack", legend=dict(orientation="h", y=-.35), margin=dict(b=55))
        show(fig, 210)
        st.caption(f"Más económicas: hasta {ars(low)}; más caras: desde {ars(high)}. Umbral de {POSITION_THRESHOLD:.0%} respecto de la mediana; no es una clasificación de calidad.")
    else:
        st.info(f"Hay menos de {MIN_GROUP} ofertas con unidad comparable. Tomá la distribución solo como referencia descriptiva.")
    left, right = st.columns(2)
    for field, column in (("marca", left), ("comercio", right)):
        with column:
            valid = series.dropna(subset=[field])
            counts = valid.groupby(field)["precio_unitario"].agg(["median", "size"])
            counts = counts[counts["size"] >= 3].sort_values("median").head(10).reset_index()
            if counts.empty:
                st.info(f"No hay grupos por {field} con al menos tres observaciones.")
                continue
            fig = px.bar(counts.sort_values("median", ascending=False), x="median", y=field,
                         orientation="h", title=f"Menores medianas por {field}",
                         hover_data=["size"], labels={"median": f"Mediana ({unit})", field: "", "size": "Observaciones"},
                         color_discrete_sequence=[COFFEE])
            show(fig, max(280, 35 * len(counts) + 100))
            st.markdown(f"**Qué observar:** {counts.iloc[0][field]} tiene la menor mediana ({ars(counts.iloc[0]['median'])} · {unit}) entre los grupos con al menos 3 ofertas.")
            st.caption("Compará alternativas con la misma unidad; las diferencias también pueden reflejar distintas presentaciones y atributos.")
    with st.expander("Ver dispersión y relación entre tamaño y precio"):
        for field in ("marca", "comercio"):
            valid = series.dropna(subset=[field])
            if not valid.empty:
                show(px.box(valid, x=field, y="precio_unitario", labels=axis,
                            title=f"Dispersión por {field}", color_discrete_sequence=[COFFEE]), 390)
        dimension = "cantidad_capsulas" if group["formato"].iloc[0] == "capsulas" else "peso_g"
        show(px.scatter(series, x=dimension, y="precio_lista_ars", hover_name="nombre_original",
                        labels={"peso_g": "Peso (g)", "cantidad_capsulas": "Cápsulas", "precio_lista_ars": "Precio de lista (ARS)"},
                        title=f"Tamaño y precio · n={len(series)}", color_discrete_sequence=[GREEN]))
        st.caption(label)
