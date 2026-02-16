import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Body Evolution - Pro", page_icon="⚡", layout="wide")

# Estilo Neon Corrigido
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00ff41 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricValue"] {
        color: #00ff41;
    }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📊 BODY EVOLUTION PRO")

# --- UPLOAD DO CSV ---
arquivo_subido = st.file_uploader("📥 Carregar Relatório CSV", type="csv")

if arquivo_subido is not None:
    try:
        # Lê o CSV tratando a vírgula decimal
        df = pd.read_csv(arquivo_subido, decimal=',')
        
        # Converte a primeira coluna (Data)
        col_data = df.columns[0]
        df[col_data] = pd.to_datetime(df[col_data], dayfirst=True)
        df = df.sort_values(col_data)

        # --- MÉTRICAS DE TOPO ---
        st.divider()
        metricas = df.columns[1:]
        cols = st.columns(len(metricas))
        
        for i, col_name in enumerate(metricas):
            atual = df[col_name].iloc[-1]
            delta = None
            if len(df) >= 2:
                delta = float(atual - df[col_name].iloc[-2])
            
            label = f"⚡ {col_name}" if "Energia" in col_name else col_name
            cols[i].metric(label=label, value=f"{atual}", delta=f"{delta:.1f}" if delta is not None else None)

        # --- GRÁFICOS ---
        st.divider()
        t1, t2 = st.tabs(["📈 Gráficos", "📋 Dados"])
        
        with t1:
            st.subheader("Peso e Massa Magra")
            st.line_chart(df.set_index(col_data)[['Peso', 'Massa Magra']], color=["#00ff41", "#00d4ff"])
            
            if "Energia" in df.columns:
                st.subheader("Nível de Energia (0-10)")
                st.bar_chart(df.set_index(col_data)['Energia'], color="#ffff00")
            
            st.subheader("Gordura Corporal (%)")
            st.area_chart(df.set_index(col_data)['Gordura'], color="#ff0055")

        with t2:
            df_view = df.copy()
            df_view[col_data] = df_view[col_data].dt.strftime('%d/%m/%Y')
            st.dataframe(df_view.sort_values(col_data, ascending=False), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando upload do CSV exportado do Google Sheets.")
