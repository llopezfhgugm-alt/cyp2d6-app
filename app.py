import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

st.set_page_config(
    page_title="CYP2D6 Duplicación",
    page_icon="🧬",
    layout="wide"
)

# ----------------------------
# CONFIGURACIÓN
# ----------------------------
REF_DELTA_CT_4_45 = -0.193

references = pd.DataFrame({
    "Target": ["CYP2D6 *1/*4x2", "CYP2D6 *2x2/*4", "CYP2D6 *4/*45"],
    "Duplicated_allele": [0.612, -0.343, 0.0],
    "Interpretacion": [
        "Alelo *4 duplicado",
        "Alelo *4 NO duplicado",
        "Una copia de *4 y otra de otro alelo"
    ]
})

# ----------------------------
# INTERFAZ
# ----------------------------
st.title("🧬 Interpretador CYP2D6 - Duplicaciones")

st.warning("⚠️ Uso orientado a investigación. Validar antes de aplicación clínica.")

col1, col2 = st.columns([1, 1])

with col1:
    sample_id = st.text_input("ID de muestra")

    fam = st.number_input("FAM Ct Mean", value=22.0)
    vic = st.number_input("VIC Ct Mean", value=22.0)

    calcular = st.button("Calcular")

with col2:
    st.info("Referencia base: CYP2D6 *4/*45")

# ----------------------------
# CÁLCULO
# ----------------------------
if calcular:

    delta_ct = fam - vic
    delta_delta_ct = delta_ct - REF_DELTA_CT_4_45
    rq = 2 ** (-delta_delta_ct)
    duplicated_allele = np.log2(rq)

    refs = references.copy()
    refs["distancia"] = (refs["Duplicated_allele"] - duplicated_allele).abs()
    mejor = refs.sort_values("distancia").iloc[0]

    # ----------------------------
    # CONTROL DE CALIDAD
    # ----------------------------
    st.subheader("🔎 Control de calidad")

    if fam < 15 or fam > 35:
        st.warning("⚠️ FAM Ct fuera de rango esperado")

    if vic < 15 or vic > 35:
        st.warning("⚠️ VIC Ct fuera de rango esperado")

    # ----------------------------
    # RESULTADO
    # ----------------------------
    st.subheader("📊 Resultado")

    if "*4x2" in mejor['Target']:
        st.success("✅ Alelo *4 duplicado")
    elif "2x2/*4" in mejor['Target']:
        st.error("❌ Alelo *4 NO duplicado")
    else:
        st.info("➖ Patrón compatible con *4/*45")

    st.write(f"**Resultado técnico:** {mejor['Target']}")

    # ----------------------------
    # MÉTRICAS
    # ----------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ΔCt", f"{delta_ct:.3f}")
    c2.metric("ΔΔCt", f"{delta_delta_ct:.3f}")
    c3.metric("RQ", f"{rq:.3f}")
    c4.metric("log2(RQ)", f"{duplicated_allele:.3f}")

    # ----------------------------
    # GRÁFICA
    # ----------------------------
    plot_df = pd.concat([
        refs[["Target", "Duplicated_allele"]].assign(Tipo="Referencia"),
        pd.DataFrame({
            "Target": ["Test"],
            "Duplicated_allele": [duplicated_allele],
            "Tipo": ["Muestra"]
        })
    ])

    fig = px.bar(
        plot_df,
        x="Target",
        y="Duplicated_allele",
        color="Tipo",
        text="Duplicated_allele",
        color_discrete_map={
            "Referencia": "gray",
            "Muestra": "red"
        },
        title="Comparación con referencias"
    )

    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # INFORME AUTOMÁTICO
    # ----------------------------
    st.subheader("🧾 Informe")

    fecha = datetime.datetime.now().strftime("%Y-%m-%d")

    informe = f"""
INFORME CYP2D6

Fecha: {fecha}
ID muestra: {sample_id}

FAM Ct: {fam}
VIC Ct: {vic}

Delta Ct: {delta_ct:.3f}
Delta Delta Ct: {delta_delta_ct:.3f}
RQ: {rq:.3f}

Resultado: {mejor['Target']}
Interpretación: {mejor['Interpretacion']}
"""

    st.text_area("Vista previa del informe", informe, height=250)

    st.download_button(
        label="📥 Descargar informe",
        data=informe,
        file_name=f"{sample_id}_CYP2D6.txt",
        mime="text/plain"
    )
