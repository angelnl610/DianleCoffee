import pandas as pd
import plotly.express as px
from ui.charts import show, COFFEE, ars
import streamlit as st


def market_decisions(group, summary):
    st.subheader("¿Qué oportunidades vale la pena investigar?")
    st.caption("Estas señales resumen todos los segmentos incluidos en los filtros, no solamente el segmento seleccionado.")
    for insight in summary["insights"]:
        st.write(insight)
    matrix = pd.DataFrame(summary["oportunidades"])
    with st.expander("Ver matriz completa de oportunidades"):
        st.dataframe(matrix[["formato", "fuente", "canal", "region", "fecha", "unidad", "mediana",
                         "minimo_unitario", "maximo_unitario", "iqr", "ofertas", "productos_unitarios",
                         "comercios_unitarios", "n_unitario", "cobertura_unitaria_pct", "debajo_referencia",
                         "sobre_referencia", "debajo_referencia_pct", "sobre_referencia_pct", "atipicos",
                         "promociones_observadas", "estado_promo_conocido", "promociones_pct",
                         "antiguedad_dias", "evidencia", "accion"]],
                 hide_index=True)
    st.caption("Las brechas se calculan respecto de la mediana unitaria de cada segmento. "
               "Las señales describen la oferta observada.")

    st.subheader("3. ¿Cómo se comparan productos concretos?")
    st.write("Elegí entre dos y cuatro alternativas. El precio unitario permite comparar envases de distinto tamaño; el precio por envase indica cuánto se paga por una presentación.")
    products = group.groupby("grupo_producto").agg(
        producto=("nombre_original", "first"), observaciones=("grupo_producto", "size"),
        comercios=("comercio", "nunique"), mediana_lista_ars=("precio_lista_ars", "median"),
        mediana_unitaria=("precio_unitario", "median"), unidad=("unidad", "first"),
    )
    if len(products) < 2:
        st.info("Elegí un segmento con al menos dos productos observados.")
        return
    labels = {f"{name} · {key}": key for key, name in products["producto"].items()}
    selected = st.multiselect("Elegí entre 2 y 4 productos del segmento", list(labels),
                              max_selections=4, key="productos_comparados")
    if len(selected) < 2:
        st.info("Seleccioná al menos dos productos para ver sus diferencias.")
    if len(selected) >= 2:
        keys = [labels[label] for label in selected]
        compared = products.loc[keys].reset_index()
        for metric, difference in (("mediana_lista_ars", "brecha_envase_pct"),
                                   ("mediana_unitaria", "brecha_unitaria_pct")):
            reference = compared[metric].iloc[0]
            compared[difference] = ((compared[metric] / reference - 1) * 100).round(2) if pd.notna(reference) else None
        show(px.bar(compared, x="mediana_unitaria", y="producto", orientation="h",
                    title="Comparación de precios unitarios", color_discrete_sequence=[COFFEE],
                    labels={"mediana_unitaria": f"Mediana ({compared['unidad'].iloc[0]})", "producto": ""}))
        valid = compared.dropna(subset=["mediana_unitaria"])
        if len(valid) >= 2:
            cheapest = valid.loc[valid["mediana_unitaria"].idxmin()]
            st.markdown(f"**Menor precio unitario entre las alternativas elegidas:** {cheapest['producto']} · {ars(cheapest['mediana_unitaria'])} ({cheapest['unidad']}).")
        else:
            st.info("No hay suficientes precios unitarios verificables para comparar las alternativas.")
        st.dataframe(compared.drop(columns=["grupo_producto"]), hide_index=True, column_config={
            "producto": "Producto", "observaciones": "Ofertas", "comercios": "Comercios",
            "mediana_lista_ars": "Mediana por envase (ARS)", "mediana_unitaria": "Mediana por unidad",
            "unidad": "Unidad", "brecha_envase_pct": st.column_config.NumberColumn("Diferencia por envase (%)", format="%.1f"),
            "brecha_unitaria_pct": st.column_config.NumberColumn("Diferencia unitaria (%)", format="%.1f")})
        st.caption(f"Brechas respecto del primer producto elegido: {compared['producto'].iloc[0]}.")
        details = group[group["grupo_producto"].isin(keys)]
        st.markdown("**Precios y promociones por comercio**")
        st.dataframe(details[["nombre_original", "comercio", "precio_lista_ars", "precio_promo_ars",
                              "estado_promocion", "condiciones_promocion", "precio_unitario", "unidad"]]
                     .sort_values(["nombre_original", "comercio"]), hide_index=True)
        st.caption("La mediana por envase depende del tamaño. Compará el precio unitario cuando esté disponible.")
