import streamlit as st
import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt

# -------- CARREGAR ARQUIVO ---------
FILE_PATH = "https://imunogenetica.famerp.br/tabela_marcia.xlsx"
df = pd.read_excel(FILE_PATH)

st.title("📈 Dashboard de Sobrevida (Kaplan-Meier)")

# --- Converter datas ---
df["DTDIAG"] = pd.to_datetime(df["DTDIAG"], errors="coerce")
df["DTULTINFO"] = pd.to_datetime(df["DTULTINFO"], errors="coerce")

# --- Calcular tempo de sobrevivência ---
df["tempo_sobrevida"] = (df["DTULTINFO"] - df["DTDIAG"]).dt.days
df["evento"] = 1  # todos são óbitos

# -----------------------------------------------------------
# 🔹 ADICIONAR COLUNA ANO DO DIAGNÓSTICO
# -----------------------------------------------------------
df["ANO_DIAG"] = df["DTDIAG"].dt.year

# ---------------- FILTROS -----------------
st.sidebar.header("Filtros")

# 🔹 Filtro por ANO
anos = sorted(df["ANO_DIAG"].dropna().unique())
filtro_ano = st.sidebar.multiselect(
    "Filtrar por Ano do Diagnóstico (DTDIAG):",
    anos,
    default=anos
)

# 🔹 Filtro TOPOGRUP
topogrup_opts = sorted(df["TOPOGRUP"].dropna().unique())
filtro_topogrup = st.sidebar.multiselect(
    "Filtrar por TOPOGRUP:",
    topogrup_opts,
    default=topogrup_opts
)

# 🔹 Filtro EC
ec_opts = sorted(df["EC"].dropna().unique())
filtro_ec = st.sidebar.multiselect(
    "Filtrar por EC:",
    ec_opts,
    default=ec_opts
)

# ----------- APLICAR FILTROS -----------
df_filt = df.copy()
df_filt = df_filt[df_filt["ANO_DIAG"].isin(filtro_ano)]
df_filt = df_filt[df_filt["TOPOGRUP"].isin(filtro_topogrup)]
df_filt = df_filt[df_filt["EC"].isin(filtro_ec)]


# ----------- Mostrar dados filtrados -----------
st.subheader("📁 Dados filtrados")
st.dataframe(df_filt)


# ----------- SELEÇÃO DE AGRUPAMENTO PARA KM -----------
st.sidebar.header("Comparação de grupos")
grupo_comparacao = st.sidebar.selectbox(
    "Comparar curvas por:",
    ["Nenhum", "TOPOGRUP", "EC", "ANO_DIAG"]  # 👈 adicionamos ANO
)

# ---------------- GRÁFICO KM -----------------
st.subheader("📉 Curva de Kaplan-Meier")

kmf = KaplanMeierFitter()
plt.figure(figsize=(10, 6))

if df_filt.empty:
    st.warning("Nenhum dado disponível com os filtros selecionados.")
else:
    if grupo_comparacao == "Nenhum":
        kmf.fit(df_filt["tempo_sobrevida"], event_observed=df_filt["evento"], label="Todos")
        kmf.plot_survival_function()

    else:
        grupos = df_filt[grupo_comparacao].dropna().unique()

        for g in grupos:
            subset = df_filt[df_filt[grupo_comparacao] == g]
            if len(subset) > 0:
                kmf.fit(subset["tempo_sobrevida"], event_observed=subset["evento"], label=f"{grupo_comparacao} = {g}")
                kmf.plot_survival_function()

    plt.xlabel("Dias")
    plt.ylabel("Probabilidade de Sobrevida")
    plt.title("Curva de Sobrevida (Kaplan-Meier)")
    plt.grid(True)

    st.pyplot(plt)
