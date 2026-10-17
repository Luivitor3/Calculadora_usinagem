import streamlit as st
import math
import pandas as pd
from datetime import datetime
import io

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Auxiliar de Usinagem",
    page_icon="⚙️",
    layout="wide"
)

# ============================================================
# INICIALIZAÇÃO DO HISTÓRICO (SESSION STATE)
# ============================================================
if "historico" not in st.session_state:
    st.session_state.historico = []

# ============================================================
# TABELA DE MATERIAIS (COM kc - FORÇA ESPECÍFICA DE CORTE)
# ============================================================
MATERIAIS = {
    "Aço 1020 (baixo carbono)": {"vc_desbaste": 100, "vc_acabamento": 150, "kc": 2000},
    "Aço 1045 (médio carbono)": {"vc_desbaste": 80, "vc_acabamento": 125, "kc": 2200},
    "Aço 4340 (liga)": {"vc_desbaste": 55, "vc_acabamento": 90, "kc": 2500},
    "Aço Inoxidável 304": {"vc_desbaste": 55, "vc_acabamento": 90, "kc": 2800},
    "Alumínio 6061": {"vc_desbaste": 275, "vc_acabamento": 425, "kc": 700},
    "Alumínio 7075": {"vc_desbaste": 200, "vc_acabamento": 325, "kc": 900},
    "Ferro Fundido Cinzento": {"vc_desbaste": 65, "vc_acabamento": 100, "kc": 1500},
    "Bronze": {"vc_desbaste": 80, "vc_acabamento": 125, "kc": 1200},
}

# ============================================================
# FUNÇÕES DE CÁLCULO
# ============================================================
def calcular_rpm(vc, diametro):
    if diametro <= 0:
        return 0
    return (vc * 1000) / (math.pi * diametro)

def calcular_avanco(rpm, avanco_dente, num_dentes):
    return rpm * avanco_dente * num_dentes

def calcular_tempo(comprimento, avanco):
    if avanco <= 0:
        return 0
    return comprimento / avanco

def calcular_potencia(avanco, profundidade, largura, kc, rendimento=0.8):
    """
    Calcula a potência de corte (kW).
    Fórmula: Pc = (Vf × ap × ae × kc) / (60 × 10⁶ × η)
    """
    if avanco <= 0 or profundidade <= 0 or largura <= 0 or kc <= 0:
        return 0
    pc = (avanco * profundidade * largura * kc) / (60 * 1000000)
    return pc / rendimento

def calcular_conicidade(d_maior, d_menor, comprimento):
    if comprimento <= 0 or d_maior <= d_menor:
        return None, None
    tg_alpha = (d_maior - d_menor) / (2 * comprimento)
    alpha_rad = math.atan(tg_alpha)
    alpha_graus = math.degrees(alpha_rad)
    graus = int(alpha_graus)
    minutos = int((alpha_graus - graus) * 60)
    return alpha_graus, (graus, minutos)

def calcular_rosca_metrica(diametro_nominal, passo):
    d_externo = diametro_nominal
    d_interno = diametro_nominal - (1.2268 * passo)
    altura_rosca = 0.6134 * passo
    return {
        "diametro_nominal": diametro_nominal,
        "passo": passo,
        "diametro_interno": d_interno,
        "altura_rosca": altura_rosca
    }

def calcular_cabecote_divisor(numero_divisoes, relacao_cabecote=40):
    if numero_divisoes <= 0:
        return None
    voltas = relacao_cabecote / numero_divisoes
    return voltas

# ============================================================
# TÍTULO
# ============================================================
st.title("⚙️ Auxiliar de Usinagem Manual")
st.markdown("""
Este programa serve para auxiliar operadores de máquinas-ferramenta convencionais 
e alunos no cálculo rápido dos parâmetros de usinagem.
""")

# ============================================================
# ABAS PRINCIPAIS
# ============================================================
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🔢 Cálculos Principais",
    "📐 Conicidade",
    "🔩 Roscas",
    "⚙️ Cabeçote Divisor",
    "📜 Histórico"
])

# ============================================================
# ABA 1: CÁLCULOS PRINCIPAIS
# ============================================================
with aba1:
    st.subheader("🔩 Material da Peça")
    
    opcao_material = st.radio(
        "Como deseja informar a velocidade de corte?",
        ["Selecionar material da lista", "Inserir valor manualmente"],
        horizontal=True,
        key="radio_material"
    )
    
    if opcao_material == "Selecionar material da lista":
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            material_selecionado = st.selectbox(
                "Selecione o material:",
                list(MATERIAIS.keys()),
                key="select_material"
            )
        with col_m2:
            tipo_operacao = st.radio(
                "Tipo de operação:",
                ["Desbaste", "Acabamento"],
                horizontal=True,
                key="radio_operacao"
            )
        
        if tipo_operacao == "Desbaste":
            vc_sugerida = MATERIAIS[material_selecionado]["vc_desbaste"]
        else:
            vc_sugerida = MATERIAIS[material_selecionado]["vc_acabamento"]
        
        st.info(f"💡 Velocidade de corte sugerida: **{vc_sugerida} m/min**")
        
        vc = st.number_input(
            "Velocidade de Corte - Vc (m/min):",
            min_value=1.0, max_value=1000.0,
            value=float(vc_sugerida), step=10.0,
            key="vc_input"
        )
    else:
        vc = st.number_input(
            "Velocidade de Corte - Vc (m/min):",
            min_value=1.0, max_value=1000.0,
            value=120.0, step=10.0,
            key="vc_manual"
        )
        material_selecionado = "Manual"
        tipo_operacao = "---"
    
    st.divider()
    st.subheader("📥 Parâmetros de Entrada")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        diametro = st.number_input(
            "Diâmetro - D (mm):",
            min_value=1.0, max_value=1000.0, value=50.0, step=5.0, key="diametro"
        )
        
        sub_c1, sub_c2 = st.columns([1, 1.5])
        with sub_c1:
            nao_sabe_fz = st.checkbox("Não sei o fz", key="check_fz")
        with sub_c2:
            st.write("") 
            
        avanco_dente = st.number_input(
            "Avanço por Dente - fz (mm/dente):",
            min_value=0.01, max_value=1.0, value=0.10, step=0.01, format="%.2f",
            key="avanco_dente", disabled=nao_sabe_fz
        )
    
    with col2:
        num_dentes = st.number_input(
            "Número de Dentes - z:", 
            min_value=1, 
            max_value=20, 
            value=1,
            step=1, 
            key="num_dentes",
            help="Para fresamento, insira o número de dentes da fresa (ex: 4). Para torneamento, insira 1." # <--- Aviso adicionado
        )
        
        # Espaço invisível para manter o alinhamento com as caixinhas de seleção
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        
        profundidade = st.number_input(
            "Profundidade de Corte - ap (mm):", min_value=0.1, max_value=20.0, value=2.0, step=0.5, key="profundidade"
        )
    with col3:
        largura = st.number_input(
            "Largura de Corte - ae (mm):", min_value=0.1, max_value=200.0, value=10.0, step=1.0, key="largura"
        )
        
        # Mantém a caixinha como estava
        nao_sabe_comprimento = st.checkbox("Não sei o L", key="check_comp")
            
        comprimento = st.number_input(
            "Comprimento de Usinagem - L (mm):", min_value=0.0, max_value=10000.0, value=200.0, step=10.0,
            key="comprimento", disabled=nao_sabe_comprimento
        )
    
    st.divider()
    
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        botao_calcular = st.button("🔢 CALCULAR PARÂMETROS", use_container_width=True, type="primary", key="btn_calcular")
    with col_b2:
        botao_limpar = st.button("🗑️ Limpar", use_container_width=True, key="btn_limpar")
    
    if botao_calcular:
        erros = []
        if diametro <= 0:
            erros.append("O diâmetro deve ser maior que zero.")
        if vc <= 0:
            erros.append("A velocidade de corte deve ser maior que zero.")
        
        if erros:
            for erro in erros:
                st.error(f"❌ {erro}")
        else:
            rpm = calcular_rpm(vc, diametro)
            
            st.divider()
            st.subheader("📊 Resultados")
            
            st.metric("Rotação (RPM)", f"{rpm:.0f}")
            
            if not nao_sabe_fz:
                avanco = calcular_avanco(rpm, avanco_dente, num_dentes)
                kc = MATERIAIS.get(material_selecionado, {}).get("kc", 2000)
                potencia = calcular_potencia(avanco, profundidade, largura, kc)
                
                col_r2, col_r3 = st.columns(2)
                col_r2.metric("Avanço (mm/min)", f"{avanco:.1f}")
                col_r3.metric("Potência (kW)", f"{potencia:.2f}")
                
                if not nao_sabe_comprimento:
                    tempo = calcular_tempo(comprimento, avanco)
                    st.metric("Tempo (min)", f"{tempo:.2f}")
                else:
                    st.info("⏱️ Tempo não calculado (Comprimento não informado).")
                
                # Salvar no histórico
                st.session_state.historico.append({
                    "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Material": material_selecionado,
                    "Operação": tipo_operacao,
                    "Vc (m/min)": vc,
                    "D (mm)": diametro,
                    "ae (mm)": largura,
                    "RPM": f"{rpm:.0f}",
                    "Avanço (mm/min)": f"{avanco:.1f}",
                    "Tempo (min)": f"{tempo:.2f}" if not nao_sabe_comprimento else "---",
                    "Potência (kW)": f"{potencia:.3f}"
                })
                
                # Botão de exportar
                df = pd.DataFrame([st.session_state.historico[-1]])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar este resultado (CSV)",
                    data=csv,
                    file_name=f"usinagem_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("ℹ️ Avanço e Potência não calculados (Avanço por Dente não informado).")
    
    if botao_limpar:
        st.rerun()

# ============================================================
# ABA 2: CONICIDADE
# ============================================================
with aba2:
    st.subheader("📐 Cálculo de Conicidade")
    st.markdown("""
    Calcula o **ângulo de inclinação do carro superior** do torno.
    """)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        d_maior = st.number_input("Diâmetro Maior - D (mm):", min_value=1.0, value=43.0, key="d_maior")
    with col_c2:
        d_menor = st.number_input("Diâmetro Menor - d (mm):", min_value=1.0, value=27.0, key="d_menor")
    with col_c3:
        comp_cone = st.number_input("Comprimento do Cone - L (mm):", min_value=1.0, value=65.0, key="comp_cone")
    
    if st.button("📐 Calcular Ângulo do Cone", use_container_width=True, key="btn_cone"):
        if d_maior <= d_menor:
            st.error("❌ O diâmetro maior deve ser maior que o diâmetro menor.")
        else:
            alpha_graus, (graus, minutos) = calcular_conicidade(d_maior, d_menor, comp_cone)
            st.success(f"**Ângulo de Inclinação (α): {graus}° {minutos}'** ({alpha_graus:.2f}°)")
            
            with st.expander("🔍 Ver detalhamento"):
                tg_alpha = (d_maior - d_menor) / (2 * comp_cone)
                st.markdown(f"""
                **Fórmula:** tg(α) = (D - d) / (2 × L)
                
                tg(α) = ({d_maior} - {d_menor}) / (2 × {comp_cone}) = {tg_alpha:.4f}
                
                α = arctg({tg_alpha:.4f}) = **{graus}° {minutos}'**
                """)

# ============================================================
# ABA 3: ROSCAS
# ============================================================
with aba3:
    st.subheader("🔩 Cálculo de Rosca Métrica")
    st.markdown("""
    Calcula as dimensões principais de uma **rosca métrica** (perfil triangular 60°).
    """)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        diametro_nominal = st.number_input(
            "Diâmetro Nominal (mm):",
            min_value=1.0, max_value=100.0,
            value=10.0, step=1.0, key="rosca_diam"
        )
    with col_r2:
        passo = st.number_input(
            "Passo (mm):",
            min_value=0.1, max_value=10.0,
            value=1.5, step=0.1, format="%.1f", key="rosca_passo"
        )
    
    if st.button("🔩 Calcular Rosca", use_container_width=True, key="btn_rosca"):
        resultado = calcular_rosca_metrica(diametro_nominal, passo)
        
        st.success("**Dimensões da Rosca Métrica:**")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Diâmetro Nominal", f"{resultado['diametro_nominal']:.1f} mm")
        col_res2.metric("Diâmetro Interno", f"{resultado['diametro_interno']:.2f} mm")
        col_res3.metric("Altura da Rosca", f"{resultado['altura_rosca']:.2f} mm")
        
        with st.expander("🔍 Ver detalhamento"):
            st.markdown(f"""
            **Fórmulas (perfil triangular 60°):**
            
            - Diâmetro interno: d = D - 1,2268 × P
            - Altura da rosca: h = 0,6134 × P
            
            **Cálculo:**
            
            - d = {diametro_nominal} - 1,2268 × {passo} = **{resultado['diametro_interno']:.2f} mm**
            - h = 0,6134 × {passo} = **{resultado['altura_rosca']:.2f} mm**
            """)

# ============================================================
# ABA 4: CABEÇOTE DIVISOR
# ============================================================
with aba4:
    st.subheader("⚙️ Cálculo de Cabeçote Divisor")
    st.markdown("""
    Calcula o número de voltas da manivela para fresamento de divisões.
    """)
    
    col_cab1, col_cab2 = st.columns(2)
    with col_cab1:
        numero_divisoes = st.number_input(
            "Número de Divisões (z):",
            min_value=1, max_value=200,
            value=6, step=1, key="cab_divisoes"
        )
    with col_cab2:
        relacao_cabecote = st.number_input(
            "Relação do Cabeçote (R):",
            min_value=1, max_value=100,
            value=40, step=1, key="cab_relacao",
            help="Padrão: 40:1"
        )
    
    if st.button("⚙️ Calcular Divisão", use_container_width=True, key="btn_cabecote"):
        voltas = calcular_cabecote_divisor(numero_divisoes, relacao_cabecote)
        
        if voltas:
            voltas_inteiras = int(voltas)
            fracao = voltas - voltas_inteiras
            
            st.success("**Resultado da Divisão:**")
            
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("Voltas da Manivela", f"{voltas_inteiras}")
            col_res2.metric("Fração de Volta", f"{fracao:.4f}")
            
            st.markdown("**Sugestão de disco divisor:**")
            
            discos = [15, 16, 17, 18, 19, 20, 21, 23, 27, 29, 31, 33, 37, 39, 41, 43, 47, 49]
            
            for disco in discos:
                if fracao > 0:
                    furos = fracao * disco
                    if abs(furos - round(furos)) < 0.01 and round(furos) > 0:
                        st.markdown(f"- Disco de **{disco} furos**: avançar **{round(furos)} furos**")
            
            with st.expander("🔍 Ver detalhamento"):
                st.markdown(f"""
                **Fórmula:** N = R / z
                
                N = {relacao_cabecote} / {numero_divisoes} = **{voltas:.4f} voltas**
                
                Ou seja: **{voltas_inteiras} volta(s)** + **{fracao:.4f}** de volta
                """)

# ============================================================
# ABA 5: HISTÓRICO
# ============================================================
with aba5:
    st.subheader("📜 Histórico de Cálculos")
    
    if st.session_state.historico:
        df_historico = pd.DataFrame(st.session_state.historico)
        st.dataframe(df_historico, use_container_width=True)
        
        csv_historico = df_historico.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar histórico completo (CSV)",
            data=csv_historico,
            file_name=f"historico_usinagem_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        if st.button("🗑️ Limpar Histórico", key="btn_limpar_hist"):
            st.session_state.historico = []
            st.rerun()
    else:
        st.info("Nenhum cálculo realizado ainda. Os resultados aparecerão aqui.")

# ============================================================
# RODAPÉ
# ============================================================
st.divider()
st.caption("Desenvolvido como parte de TCC em Engenharia Mecânica | Versão 2.2")
