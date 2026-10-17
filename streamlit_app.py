import streamlit as st
import math

st.set_page_config(
    page_title="Auxiliar de Usinagem",
    page_icon="⚙️",
    layout="centered"
)

st.title("⚙️ Auxiliar de Usinagem Manual")
st.markdown("""
Este programa auxilia operadores de máquinas-ferramenta convencionais 
e alunos no cálculo rápido dos parâmetros de usinagem.
""")

st.divider()

st.subheader("📥 Parâmetros de Entrada")

col1, col2 = st.columns(2)

with col1:
    vc = st.number_input(
        "Velocidade de Corte - Vc (m/min):",
        min_value=1.0, max_value=1000.0, value=120.0, step=10.0
    )
    diametro = st.number_input(
        "Diâmetro - D (mm):",
        min_value=1.0, max_value=1000.0, value=50.0, step=5.0
    )

with col2:
    avanco_dente = st.number_input(
        "Avanço por Dente - fz (mm/dente):",
        min_value=0.01, max_value=1.0, value=0.10, step=0.01, format="%.2f"
    )
    num_dentes = st.number_input(
        "Número de Dentes - z:",
        min_value=1, max_value=20, value=4, step=1
    )

comprimento = st.number_input(
    "Comprimento de Usinagem - L (mm) [opcional]:",
    min_value=0.0, max_value=10000.0, value=200.0, step=10.0
)

st.divider()

if st.button("🔢 CALCULAR PARÂMETROS", use_container_width=True, type="primary"):
    if diametro <= 0 or vc <= 0 or avanco_dente <= 0 or num_dentes <= 0:
        st.error("❌ Todos os valores devem ser maiores que zero.")
    else:
        rpm = (vc * 1000) / (math.pi * diametro)
        avanco = rpm * avanco_dente * num_dentes
        tempo = comprimento / avanco if comprimento > 0 else 0

        st.divider()
        st.subheader("📊 Resultados")

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Rotação (RPM)", f"{rpm:.0f}")
        col_r2.metric("Avanço (mm/min)", f"{avanco:.1f}")
        col_r3.metric("Tempo (min)", f"{tempo:.2f}" if tempo > 0 else "---")

        with st.expander("🔍 Ver detalhamento dos cálculos"):
            st.markdown(f"""
            **Rotação:** n = (Vc × 1000) / (π × D) = ({vc} × 1000) / (π × {diametro}) = **{rpm:.2f} rpm**
            
            **Avanço:** Vf = n × fz × z = {rpm:.2f} × {avanco_dente} × {num_dentes} = **{avanco:.2f} mm/min**
            
            **Tempo:** Tc = L / Vf = {comprimento} / {avanco:.2f} = **{tempo:.2f} min**
            """)

st.divider()

with st.expander("📚 Tabela de Referência - Velocidade de Corte (Vc)"):
    st.markdown("""
    | Material | Vc Desbaste (m/min) | Vc Acabamento (m/min) |
    |----------|---------------------|------------------------|
    | Aço 1020 | 80 - 120 | 120 - 180 |
    | Aço 1045 | 60 - 100 | 100 - 150 |
    | Alumínio 6061 | 200 - 350 | 350 - 500 |
    | Ferro Fundido | 50 - 80 | 80 - 120 |
    """)

st.caption("Desenvolvido como parte de TCC em Engenharia Mecânica")
