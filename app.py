import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="CYP2D6 Duplicación", page_icon="🧬", layout="wide")

# ------------------------------------------------
# Referencias extraídas del Excel del usuario
# ------------------------------------------------
# Delta Ct de la referencia CYP2D6 *4/*45 ≈ -0.193
REF_DELTA_CT_4_45 = -0.193

references = pd.DataFrame({
    "Target": ["CYP2D6 *1/*4x2", "CYP2D6 *2x2/*4", "CYP2D6 *4/*45"],
    "Duplicated_allele": [0.612, -0.343, 0.0],
    "Interpretacion": [
        "Alelo 4 duplicado",
        "Alelo 4 no duplicado",
        "Una copia de *4 y otra de otro alelo"
    ]
})

st.title("🧬 Calculadora de duplicación CYP2D6")
st.markdown(
    "Introduce los valores **FAM Ct Mean** y **VIC Ct Mean** para estimar "
    "qué alelo está duplicado."
)

col1, col2 = st.columns([1, 1])

with col1:
    fam = st.number_input("FAM Ct Mean", value=22.082, format="%.3f")
    vic = st.number_input("VIC Ct Mean", value=21.711, format="%.3f")
    calcular = st.button("Calcular")

with col2:
    st.info("La referencia base usada para ΔΔCt es CYP2D6 *4/*45.")

if calcular:
    # Fórmulas equivalentes al Excel:
    # Delta Ct = FAM - VIC
    # Delta Delta Ct = Delta Ct(test) - Delta Ct(ref *4/*45)
    # RQ = 2^(-Delta Delta Ct)
    # Duplicated allele = log2(RQ)
    delta_ct = fam - vic
    delta_delta_ct = delta_ct - REF_DELTA_CT_4_45
    rq = 2 ** (-delta_delta_ct)
    duplicated_allele = np.log2(rq)

    refs = references.copy()
    refs["distancia"] = (refs["Duplicated_allele"] - duplicated_allele).abs()
    mejor = refs.sort_values("distancia").iloc[0]

    st.subheader("Resultado")
    st.success(f"Más compatible con: {mejor['Target']}")
    st.write(f"**Interpretación:** {mejor['Interpretacion']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Delta Ct", f"{delta_ct:.3f}")
    c2.metric("Delta Delta Ct", f"{delta_delta_ct:.3f}")
    c3.metric("RQ", f"{rq:.3f}")
    c4.metric("Duplicated allele", f"{duplicated_allele:.3f}")

    plot_df = pd.concat([
        refs[["Target", "Duplicated_allele"]].assign(Tipo="Referencia"),
        pd.DataFrame({
            "Target": ["Test"],
            "Duplicated_allele": [duplicated_allele],
            "Tipo": ["Muestra"]
        })
    ], ignore_index=True)

    fig = px.bar(
        plot_df,
        x="Target",
        y="Duplicated_allele",
        color="Tipo",
        text="Duplicated_allele",
        title="CYP2D6 - comparación con referencias"
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(
        yaxis_title="Duplicated allele (log2)",
        xaxis_title="Muestra / referencia"
    )

    st.plotly_chart(fig, use_container_width=True)
