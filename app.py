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
