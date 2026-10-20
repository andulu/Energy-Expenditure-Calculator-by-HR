import streamlit as st
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

# Configuração da página
st.set_page_config(
    page_title="Calculadora ISO 8996:2021",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Calculadora de Taxa Metabólica - ISO 8996:2021")
st.write("Estimativa da taxa metabólica (M) e gasto energético total baseada na Frequência Cardíaca (Nível 3 - Anexo C).")

# --- TABELAS DA NORMA ISO 8996:2021 (Tabela C.1) ---
idades = np.array([20, 25, 30, 35, 40, 45, 50, 55, 60, 65])
massa_magra = np.array([40, 50, 60, 70, 80, 90, 100, 110])

tabela_mulheres = np.array([
    [3.87, 5.04, 6.21, 7.38, 8.55, 9.73, 10.90, 12.07],
    [3.74, 4.88, 6.02, 7.16, 8.31, 9.45, 10.59, 11.73],
    [3.60, 4.71, 5.82, 6.93, 8.04, 9.15, 10.26, 11.38],
    [3.44, 4.52, 5.60, 6.68, 7.76, 8.84, 9.92, 11.00],
    [3.28, 4.32, 5.37, 6.42, 7.46, 8.51, 9.55, 10.60],
    [3.10, 4.11, 5.12, 6.13, 7.14, 8.15, 9.16, 10.17],
    [2.92, 3.89, 4.86, 5.83, 6.80, 7.78, 8.75, 9.72],
    [2.68, 3.65, 4.58, 5.51, 6.44, 7.37, 8.30, 9.23],
    [2.50, 3.39, 4.28, 5.16, 6.05, 6.94, 7.82, 8.71],
    [2.27, 3.11, 3.95, 4.79, 5.63, 6.47, 7.31, 8.15]
])

tabela_homens = np.array([
    [4.61, 5.96, 7.32, 8.67, 10.03, 11.38, 12.73, 14.09],
    [4.53, 5.86, 7.20, 8.54, 9.88, 11.21, 12.55, 13.89],
    [4.43, 5.75, 7.07, 8.39, 9.72, 11.04, 12.36, 13.68],
    [4.33, 5.64, 6.94, 8.24, 9.55, 10.85, 12.15, 13.46],
    [4.23, 5.51, 6.80, 8.08, 9.37, 10.65, 11.94, 13.22],
    [4.12, 5.38, 6.65, 7.91, 9.18, 10.44, 11.70, 12.97],
    [4.00, 5.24, 6.49, 7.73, 8.97, 10.21, 11.46, 12.70],
    [3.87, 5.09, 6.31, 7.53, 8.75, 9.97, 11.19, 12.41],
    [3.74, 4.93, 6.13, 7.32, 8.52, 9.71, 10.91, 12.10],
    [3.59, 4.76, 5.93, 7.10, 8.26, 9.43, 10.60, 11.77]
])

# --- FUNÇÕES DE CÁLCULO ---
def calcular_wbl(sexo, peso, altura_m):
    """Calcula a Massa Corporal Magra (Lean Body Weight) em kg"""
    if sexo == "Masculino":
        return (1.08 - (peso / (80 * (altura_m ** 2)))) * peso
    else:
        return (0.86 - (peso / (107.5 * (altura_m ** 2)))) * peso

def calcular_area_dubois(peso, altura_m):
    """Calcula a área de superfície corporal ADu em m² (DuBois)"""
    altura_cm = altura_m * 100
    return 0.007184 * (peso ** 0.425) * (altura_cm ** 0.725)

def interpolar_um_sobre_rm(sexo, idade, wbl):
    """Interpolação bilinear de 1/RM"""
    grid = tabela_homens if sexo == "Masculino" else tabela_mulheres
    idade_clamped = np.clip(idade, 20, 65)
    wbl_clamped = np.clip(wbl, 40, 110)
    interp_func = RegularGridInterpolator((idades, massa_magra), grid, bounds_error=False, fill_value=None)
    return float(interp_func((idade_clamped, wbl_clamped)))

def converter_w_m2_para_kcal_min(m_w_m2, a_du):
    """Converte M em W/m² para W totais e kcal/min"""
    watts_totais = m_w_m2 * a_du
    kcal_min = watts_totais * 0.014333
    return watts_totais, kcal_min

# --- INTERFACE LATERAL DE ENTRADA ---
st.sidebar.header("📋 Dados Antropométricos")

sexo = st.sidebar.selectbox("Sexo:", ["Feminino", "Masculino"])
idade = st.sidebar.number_input("Idade (anos):", min_value=18, max_value=80, value=25, step=1)
peso = st.sidebar.number_input("Peso (kg):", min_value=30.0, max_value=150.0, value=60.0, step=0.1)
altura = st.sidebar.number_input("Altura (m):", min_value=1.20, max_value=2.20, value=1.65, step=0.01)

# Cálculo dos parâmetros do participante
wbl = calcular_wbl(sexo, peso, altura)
um_sobre_rm = interpolar_um_sobre_rm(sexo, idade, wbl)
rm = 1.0 / um_sobre_rm
a_du = calcular_area_dubois(peso, altura)

# Exibição rápida do perfil no menu lateral
st.sidebar.markdown("---")
st.sidebar.markdown(f"**$W_{{bl}}$ (Massa Magra):** {wbl:.2f} kg")
st.sidebar.markdown(f"**$A_{{Du}}$ (Área Corporal):** {a_du:.2f} m²")
st.sidebar.markdown(f"**Fator $RM$:** {rm:.4f}")

# --- ORGANIZAÇÃO DAS ABAS ---
aba1, aba2 = st.tabs(["⚡ Cálculo Instantâneo (FC Única)", "📈 Análise por Período (Múltiplos Minutos)"])

# =========================================================
# ABA 1: CÁLCULO PONTO A PONTO
# =========================================================
with aba1:
    st.subheader("Cálculo a partir de uma Frequência Cardíaca Média")
    hr_media = st.number_input("Frequência Cardíaca Média (bpm):", min_value=40, max_value=220, value=95, step=1)

    m_metabolismo = ((hr_media - 70) * rm) + 100
    watts_totais, kcal_min = converter_w_m2_para_kcal_min(m_metabolismo, a_du)

    st.markdown("---")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Taxa Metabólica (M)", f"{m_metabolismo:.2f} W/m²")
    col_m2.metric("Potência Total", f"{watts_totais:.2f} W")
    col_m3.metric("Gasto por Minuto", f"{kcal_min:.2f} kcal/min")

    if m_metabolismo < 125:
        categoria = "Descanso / Atividade Leve"
        cor = "blue"
    elif 125 <= m_metabolismo < 235:
        categoria = "Taxa Metabólica Baixa"
        cor = "green"
    elif 235 <= m_metabolismo < 360:
        categoria = "Taxa Metabólica Moderada"
        cor = "orange"
    else:
        categoria = "Taxa Metabólica Alta / Muito Alta"
        cor = "red"

    st.subheader(f"Classificação pela Norma: :{cor}[**{categoria}**]")

# =========================================================
# ABA 2: ANÁLISE POR PERÍODO / MÚLTIPLOS MINUTOS
# =========================================================
with aba2:
    st.subheader("Análise Contínua de Período Monitorado")
    st.write("Insira os valores de Frequência Cardíaca registrados minuto a minuto durante a atividade.")

    # Opção de entrada de dados
    opcao_entrada = st.radio("Como deseja inserir os dados?", ["Digitar / Colar lista de BPMs", "Upload de arquivo (CSV/Excel)"], horizontal=True)

    lista_hr = []

    if opcao_entrada == "Digitar / Colar lista de BPMs":
        texto_bpm = st.text_area(
            "Cole os valores de BPM por minuto (separados por vírgula, espaço ou quebra de linha):",
            value="85, 90, 95, 110, 115, 120, 105, 98, 92, 88",
            height=120
        )
        if texto_bpm.strip():
            # Limpa e converte a string colada em uma lista de números
            import re
            valores = re.findall(r'\d+', texto_bpm)
            lista_hr = [float(v) for v in valores if 40 <= float(v) <= 220]

    else:
        arquivo = st.file_uploader("Selecione o arquivo CSV ou Excel (deve conter uma coluna com valores de FC):", type=["csv", "xlsx"])
        if arquivo is not None:
            try:
                if arquivo.name.endswith(".csv"):
                    df_upload = pd.read_csv(arquivo)
                else:
                    df_upload = pd.read_excel(arquivo)
                coluna = st.selectbox("Selecione a coluna que contém os batimentos cardíacos (BPM):", df_upload.columns)
                lista_hr = df_upload[coluna].dropna().tolist()
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")

    if len(lista_hr) > 0:
        duracao_min = len(lista_hr)
        
        # Cria Tabela com os cálculos minuto a minuto
        df_resultados = pd.DataFrame({"Minuto": range(1, duracao_min + 1), "FC (bpm)": lista_hr})
        df_resultados["M (W/m²)"] = ((df_resultados["FC (bpm)"] - 70) * rm) + 100
        df_resultados["Potência (W)"] = df_resultados["M (W/m²)"] * a_du
        df_resultados["Gasto (kcal/min)"] = df_resultados["Potência (W)"] * 0.014333

        # Totais e Médias do Período
        fc_media_periodo = np.mean(lista_hr)
        gasto_total_kcal = df_resultados["Gasto (kcal/min)"].sum()
        m_medio_periodo = df_resultados["M (W/m²)"].mean()
        watts_medios = df_resultados["Potência (W)"].mean()

        st.markdown("---")
        st.markdown(f"### ⏱️ Resumo da Atividade Monitorada ({duracao_min} minutos)")

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric("Duração Total", f"{duracao_min} min")
        col_t2.metric("FC Média do Período", f"{fc_media_periodo:.1f} bpm")
        col_t3.metric("Médias da Atividade", f"{m_medio_periodo:.1f} W/m²")
        col_t4.metric("🔥 Gasto Energético Total", f"{gasto_total_kcal:.2f} kcal", delta_color="normal")

        # Gráfico da evolução temporal da Taxa Metabólica e FC
        st.subheader("📈 Comportamento ao Longo da Atividade")
        st.line_chart(df_resultados.set_index("Minuto")[["FC (bpm)", "Gasto (kcal/min)"]])

        # Tabela expansível
        with st.expander("📋 Ver tabela detalhada minuto a minuto"):
            st.dataframe(df_resultados.style.format({
                "FC (bpm)": "{:.0f}",
                "M (W/m²)": "{:.2f}",
                "Potência (W)": "{:.2f}",
                "Gasto (kcal/min)": "{:.2f}"
            }), use_container_width=True)

    else:
        st.info("Insira ou faça upload dos dados de Frequência Cardíaca para calcular a atividade.")
