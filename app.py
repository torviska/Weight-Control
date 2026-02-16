import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Body Evolution - Pro", page_icon="⚡", layout="wide")

# Estilo personalizado via CSS para o tema "Dark/Neon"
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00ff41 !important; /* Verde Matrix/Neon */
        font-family: 'Courier New', Courier, monospace;
    }
    .stMetric {
        background-color: #161b22;
        border: 1px solid #00ff41;
        padding: 10px;
        border-radius: 10px;
    }
    /* Estilo para destacar o gráfico de energia */
    .energy-header {
        color: #ffff00 !important; /* Amarelo Elétrico */
    }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📊 BODY EVOLUTION PRO")
st.write("### Sistema de Monitoramento de Performance & Vitalidade")

# --- UPLOAD DO CSV ---
arquivo_subido = st.file_uploader("📥 Carregar Relatório CSV (Exportado do Google Sheets)", type="csv")

if arquivo_subido is not None:
    try:
        # Lendo o CSV (tratando vírgula como separador decimal)
        df = pd.read_csv(arquivo_subido, decimal=',')
        
        # Converte a primeira coluna para Data
        col_data = df.columns[0]
        df[col_data] = pd.to_datetime(df[col_data], dayfirst=True)
        df = df.sort_values(col_data)

        # --- MÉTRICAS DE TOPO ---
        if len(df) >= 1:
            st.divider()
            # Criamos colunas para as métricas principais
            cols = st.columns(len(df.columns) - 1)
            for i, col_name in enumerate(df.columns[1:]):
                ultima_val = df[col_name].iloc[-1]
                delta = None
                if len(df) >= 2:
                    try:
                        delta = float(ultima_val - df[col_name].iloc[-2])
                    except:
                        delta = 0
                
                # Se for a coluna de Energia, formatamos de forma diferente
                label_display = f"⚡ {col_name}" if "Energia" in col_name else col_name
                cols[i].metric(label=label_display, value=f"{ultima_val}", delta=f"{delta:.1f}" if delta is not None else None)

        st.divider()

        # --- GRÁFICOS NEON ---
        tab1, tab2 = st.tabs(["📈 ANÁLISE GRÁFICA", "📋 LOG DE DADOS"])

        with tab1:
            # Gráfico Principal: Peso e Massa Magra
            st.subheader("Evolução de Peso e Massa Muscular")
            st.line_chart(df.set_index(col_data)[['Peso', 'Massa Magra']], color=["#00ff41", "#00d4ff"])

            # Gráfico de Energia (0-10) - Destaque em Amarelo
            if "Energia" in df.columns:
                st.markdown("<h3 class='energy-header'>Níveis de Energia (Vitalidade 0-10)</h3>", unsafe_allow_stdio=True)
                st.bar_chart(df.set_index(col_data)['Energia'], color="#ffff00")

            # Gráficos Secundários
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Gordura Corporal (%)")
                st.area_chart(df.set_index(col_data)['Gordura'], color="#ff0055")
            with c2:
                st.subheader("Hidratação e Cintura")
                # Se tiver a coluna Cintura, podemos plotar aqui
                metricas_sec = [c for c in ['Agua', 'Cintura'] if c in df.columns]
                st.line_chart(df.set_index(col_data)[metricas_sec])

        with tab2:
            st.dataframe(df.sort_values(col_data, ascending=False), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro na leitura: {e}")
        st.info("Dica: Verifique se o nome da coluna no Google Sheets é exatamente 'Energia'.")

else:
    st.info("Aguardando upload do arquivo CSV com a nova coluna 'Energia'...")
