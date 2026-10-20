import streamlit as st
import numpy as np
from scipy.interpolate import RegularGridInterpolator

# Configuração da página
st.set_page_config(
    page_title="Calculadora ISO 8996:2021",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Calculadora de Taxa Metabólica - ISO 8996:2021")
st.write("Estimativa da taxa metabólica (M) baseada na Frequência Cardíaca (Nível 3 - Anexo C).")

# --- TABELAS DA NORMA ISO 8996:2021 (Tabela C.1) ---
idades = np.array([20, 25, 30, 35, 40, 45, 50, 55, 60, 65])
massa_magra = np.array([40, 50, 60, 70, 80, 90, 100, 110])

# Tabela C.1 - Mulheres (1/RM)
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

# Tabela C.1 - Homens (1/RM)
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

# Funções de apoio
def calcular_wbl(sexo, peso, altura_m):
    """Calcula a Massa Corporal Magra (Lean Body Weight) em kg"""
    if sexo == "Masculino":
        return (1.08 - (peso / (80 * (altura_m ** 2)))) * peso
    else:
        return (0.86 - (peso / (107.5 * (altura_m ** 2)))) * peso

def interpolar_um_sobre_rm(sexo, idade, wbl):
    """Interpolação bilinear de 1/RM com base na Idade e Wbl"""
    grid = tabela_homens if sexo == "Masculino" else tabela_mulheres
    
    # Limita entradas às faixas da norma para evitar erros fora do domínio
    idade_clamped = np.clip(idade, 20, 65)
    wbl_clamped = np.clip(wbl, 40, 110)
    
    interp_func = RegularGridInterpolator((idades, massa_magra), grid, bounds_error=False, fill_value=None)
    return float(interp_func((idade_clamped, wbl_clamped)))

# --- INTERFACE DE ENTRADA ---
st.sidebar.header("📋 Dados do Participante")

sexo = st.sidebar.selectbox("Sexo:", ["Feminino", "Masculino"])
idade = st.sidebar.number_input("Idade (anos):", min_value=18, max_value=80, value=25, step=1)
peso = st.sidebar.number_input("Peso (kg):", min_value=30.0, max_value=150.0, value=60.0, step=0.1)
altura = st.sidebar.number_input("Altura (m):", min_value=1.20, max_value=2.20, value=1.65, step=0.01)
hr_media = st.sidebar.number_input("Frequência Cardíaca Média (bpm):", min_value=40, max_value=220, value=95, step=1)

# --- PROCESSAMENTO DOS CÁLCULOS ---
wbl = calcular_wbl(sexo, peso, altura)
um_sobre_rm = interpolar_um_sobre_rm(sexo, idade, wbl)
rm = 1.0 / um_sobre_rm
m_metabolismo = ((hr_media - 70) * rm) + 100

# --- APRESENTAÇÃO DOS RESULTADOS ---
st.subheader("📊 Resultados Obtidos")

col1, col2, col3 = st.columns(3)
col1.metric("Massa Magra (Wbl)", f"{wbl:.2f} kg")
col2.metric("Coeficiente (1/RM)", f"{um_sobre_rm:.3f}")
col3.metric("Fator RM", f"{rm:.4f}")

st.markdown("---")

st.markdown(f"### ⚡ Taxa Metabólica Estimada (M): **{m_metabolismo:.2f} W/m²**")

# Classificação da Carga de Trabalho (Grau de Esforço)
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

# Explicativo detalhado dos passos
with st.expander("🔍 Ver memória de cálculo passo a passo"):
    st.write(f"1. **Massa Magra ($W_{{bl}}$):**Calculada em **{wbl:.2f} kg** usando a fórmula específica para o sexo {sexo.lower()}.")
    st.write(f"2. **Interpolação (Tabela C.1):** Para {idade} anos e {wbl:.2f} kg de massa magra, obteve-se $1/RM = {um_sobre_rm:.3f}$.")
    st.write(f"3. **Inversão do Coeficiente ($RM$):** $RM = 1 / {um_sobre_rm:.3f} = {rm:.4f}$.")
    st.write(f"4. **Fórmula da Taxa Metabólica ($M$):** $M = (({hr_media} - 70) \\times {rm:.4f}) + 100 = {m_metabolismo:.2f} \\text{{ W/m²}}$.")
