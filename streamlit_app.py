import streamlit as st
import math

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Auxiliar de Usinagem",
    page_icon="⚙️",
    layout="wide"
)

# ============================================================
# TABELA DE MATERIAIS (DADOS INTERNOS)
# ============================================================
MATERIAIS = {
    "Aço 1020 (baixo carbono)": {"vc_desbaste": 100, "vc_acabamento": 150},
    "Aço 1045 (médio carbono)": {"vc_desbaste": 80, "vc_acabamento": 125},
    "Aço 4340 (liga)": {"vc_desbaste": 55, "vc_acabamento": 90},
    "Aço Inoxidável 304": {"vc_desbaste": 55, "vc_acabamento": 90},
    "Alumínio 6061": {"vc_desbaste": 275, "vc_acabamento": 425},
    "Alumínio 7075": {"vc_desbaste": 200, "vc_acabamento": 325},
    "Ferro Fundido Cinzento": {"vc_desbaste": 65, "vc_acabamento": 100},
    "Bronze": {"vc_desbaste": 80, "vc_acabamento": 125},
}

# ============================================================
# FUNÇÕES DE CÁLCULO
# ============================================================
def calcular_rpm(vc, diametro):
    """Calcula a rotação (RPM). Fórmula: n = (Vc × 1000) / (π × D)"""
    if diametro <= 0:
        return 0
    return (vc * 1000) / (math.pi * diametro)

def calcular_avanco(rpm, avanco_dente, num_dentes):
    """Calcula o avanço da mesa (mm/min). Fórmula: Vf = n × fz × z"""
    return rpm * avanco_dente * num_dentes

def calcular_tempo(comprimento, avanco):
    """Calcula o tempo de usinagem (min). Fórmula: Tc = L / Vf"""
    if avanco <= 0:
        return 0
    return comprimento / avanco

def calcular_conicidade(d_maior, d_menor, comprimento):
    """Calcula o ângulo de inclinação do carro superior (graus e minutos)."""
    if comprimento <= 0 or d_maior <= d_menor:
        return None, None
    tg_alpha = (d_maior - d_menor) / (2 * comprimento)
    alpha_rad = math.atan(tg_alpha)
    alpha_graus = math.degrees(alpha_rad)
    graus = int(alpha_graus)
    minutos = int((alpha_graus - graus) * 60)
    return alpha_graus, (graus, minutos)

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================
st.title("⚙️ Auxiliar de Usinagem Manual")
st.markdown("""
Este programa auxilia operadores de máquinas-ferramenta convencionais 
e alunos no cálculo rápido dos parâmetros de usinagem.
""")

st.divider()

# ============================================================
# SEÇÃO DE MATERIAIS
# ============================================================
st.subheader("🔩 Material da Peça")

opcao_material = st.radio(
    "Como deseja informar a velocidade de corte?",
    ["Selecionar material da lista", "Inserir valor manualmente"],
    horizontal=True
)

if opcao_material == "Selecionar material da lista":
    material_selecionado = st.selectbox(
        "Selecione o material:",
        list(MATERIAIS.keys())
    )
    
    tipo_operacao = st.radio(
        "Tipo de operação:",
        ["Desbaste", "Acabamento"],
        horizontal=True
    )
    
    if tipo_operacao == "Desbaste":
        vc_sugerida = MATERIAIS[material_selecionado]["vc_desbaste"]
    else:
        vc_sugerida = MATERIAIS[material_selecionado]["vc_acabamento"]
    
    st.info(f"💡 Velocidade de corte sugerida para **{material_selecionado}** ({tipo_operacao}): **{vc_sugerida} m/min**")
    
    vc = st.number_input(
        "Velocidade de Corte - Vc (m/min):",
        min_value=1.0,
        max_value=1000.0,
        value=float(vc_sugerida),
        step=10.0
    )
else:
    vc = st.number_input(
        "Velocidade de Corte - Vc (m/min):",
        min_value=1.0,
        max_value=1000.0,
        value=120.0,
        step=10.0,
        help="Insira o valor conforme catálogo do fabricante da ferramenta"
    )

st.divider()

# ============================================================
# SEÇÃO DE PARÂMETROS DE ENTRADA
# ============================================================
st.subheader("📥 Parâmetros de Entrada")

col1, col2 = st.columns(2)

with col1:
    diametro = st.number_input(
        "Diâmetro - D (mm):",
        min_value=1.0,
        max_value=1000.0,
        value=50.0,
        step=5.0,
        help="Diâmetro da peça (torneamento) ou da ferramenta (fresamento)"
    )
    
    avanco_dente = st.number_input(
        "Avanço por Dente - fz (mm/dente):",
        min_value=0.01,
        max_value=1.0,
        value=0.10,
        step=0.01,
        format="%.2f"
    )

with col2:
    num_dentes = st.number_input(
        "Número de Dentes - z:",
        min_value=1,
        max_value=20,
        value=4,
        step=1
    )
    
    comprimento = st.number_input(
        "Comprimento de Usinagem - L (mm) [opcional]:",
        min_value=0.0,
        max_value=10000.0,
        value=200.0,
        step=10.0,
        help="Deixe 0 se não quiser calcular o tempo"
    )

st.divider()

# ============================================================
# BOTÕES DE AÇÃO
# ============================================================
col_b1, col_b2 = st.columns([3, 1])

with col_b1:
    botao_calcular = st.button("🔢 CALCULAR PARÂMETROS", use_container_width=True, type="primary")

with col_b2:
    botao_limpar = st.button("🗑️ Limpar", use_container_width=True)

# ============================================================
# LÓGICA DE CÁLCULO
# ============================================================
if botao_calcular:
    # Validações
    erros = []
    if diametro <= 0:
        erros.append("O diâmetro deve ser maior que zero.")
    if vc <= 0:
        erros.append("A velocidade de corte deve ser maior que zero.")
    if avanco_dente <= 0:
        erros.append("O avanço por dente deve ser maior que zero.")
    if num_dentes <= 0:
        erros.append("O número de dentes deve ser maior que zero.")
    
    if erros:
        for erro in erros:
            st.error(f"❌ {erro}")
    else:
        # Cálculos principais
        rpm = calcular_rpm(vc, diametro)
        avanco = calcular_avanco(rpm, avanco_dente, num_dentes)
        tempo = calcular_tempo(comprimento, avanco) if comprimento > 0 else 0
        
        # Exibição dos resultados
        st.divider()
        st.subheader("📊 Resultados")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.metric(label="Rotação (RPM)", value=f"{rpm:.0f}")
        
        with col_r2:
            st.metric(label="Avanço (mm/min)", value=f"{avanco:.1f}")
        
        with col_r3:
            if tempo > 0:
                st.metric(label="Tempo (min)", value=f"{tempo:.2f}")
            else:
                st.metric(label="Tempo (min)", value="---")
        
        # Detalhamento dos cálculos
        with st.expander("🔍 Ver detalhamento dos cálculos"):
            st.markdown(f"""
            **Rotação:** n = (Vc × 1000) / (π × D) = ({vc} × 1000) / (π × {diametro}) = **{rpm:.2f} rpm**
            
            **Avanço:** Vf = n × fz × z = {rpm:.2f} × {avanco_dente} × {num_dentes} = **{avanco:.2f} mm/min**
            """)
            if tempo > 0:
                st.markdown(f"""
                **Tempo:** Tc = L / Vf = {comprimento} / {avanco:.2f} = **{tempo:.2f} min** ({tempo*60:.0f} segundos)
                """)

if botao_limpar:
    st.rerun()

st.divider()

# ============================================================
# SEÇÃO DE CONICIDADE
# ============================================================
st.subheader("📐 Cálculo de Conicidade")
st.markdown("""
Para calcular o **ângulo de inclinação do carro superior** do torno, 
informe os diâmetros e o comprimento do cone.
""")

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    d_maior = st.number_input(
        "Diâmetro Maior - D (mm):",
        min_value=1.0,
        max_value=1000.0,
        value=43.0,
        step=1.0
    )

with col_c2:
    d_menor = st.number_input(
        "Diâmetro Menor - d (mm):",
        min_value=1.0,
        max_value=1000.0,
        value=27.0,
        step=1.0
    )

with col_c3:
    comp_cone = st.number_input(
        "Comprimento do Cone - L (mm):",
        min_value=1.0,
        max_value=10000.0,
        value=65.0,
        step=1.0
    )

if st.button("📐 Calcular Ângulo do Cone", use_container_width=True):
    if d_maior <= d_menor:
        st.error("❌ O diâmetro maior deve ser maior que o diâmetro menor.")
    elif comp_cone <= 0:
        st.error("❌ O comprimento do cone deve ser maior que zero.")
    else:
        alpha_graus, (graus, minutos) = calcular_conicidade(d_maior, d_menor, comp_cone)
        
        st.success(f"**Ângulo de Inclinação (α): {graus}° {minutos}'** ({alpha_graus:.2f}°)")
        
        with st.expander("🔍 Ver detalhamento do cálculo"):
            tg_alpha = (d_maior - d_menor) / (2 * comp_cone)
            st.markdown(f"""
            **Fórmula:** tg(α) = (D - d) / (2 × L)
            
            **Substituindo:** tg(α) = ({d_maior} - {d_menor}) / (2 × {comp_cone}) = {tg_alpha:.4f}
            
            **Ângulo:** α = arctg({tg_alpha:.4f}) = **{graus}° {minutos}'**
            """)

st.divider()

# ============================================================
# TABELA DE REFERÊNCIA (RODAPÉ)
# ============================================================
with st.expander("📚 Tabela de Referência - Velocidade de Corte (Vc)"):
    dados_tabela = []
    for material, valores in MATERIAIS.items():
        dados_tabela.append({
            "Material": material,
            "Vc Desbaste (m/min)": valores["vc_desbaste"],
            "Vc Acabamento (m/min)": valores["vc_acabamento"]
        })
    
    st.table(dados_tabela)
    st.caption("Fonte: Adaptado de Sandvik Coromant (2010) e Diniz et al. (2013).")

st.caption("Desenvolvido como parte de TCC em Engenharia Mecânica")
