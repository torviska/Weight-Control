import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Body Evolution - Pro", page_icon="⚡", layout="wide")

# Estilo Neon Corrigido (Troquei stdio por html)
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        color: #00ff41;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 BODY EVOLUTION PRO")

# --- UPLOAD DO CSV ---
arquivo_subido = st.file_uploader("📥 Carregar Relatório CSV (Google Sheets)", type="csv")

if arquivo_subido is not None:
    try:
        # Tenta ler o CSV. Se falhar com vírgula, tenta com ponto.
        try:
            df = pd.read_csv(arquivo_subido, decimal=',')
        except:
            df = pd.read_csv(arquivo_subido, decimal='.')
        
        # Converte a primeira coluna (Data) de forma inteligente
        col_data = df.columns[0]
        df[col_data] = pd.to_datetime(df[col_data], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[col_data]) # Remove linhas vazias
        df = df.sort_values(col_data)

        # --- MÉTRICAS DE TOPO ---
        st.divider()
        metricas_disponiveis = df.columns[1:]
        cols = st.columns(len(metricas_disponiveis))
        
        for i, col_name in enumerate(metricas_disponiveis):
            atual = df[col_name].iloc[-1]
            delta = None
            if len(df) >= 2:
                try:
                    delta = float(atual) - float(df[col_name].iloc[-2])
                except:
                    delta = 0
            
            label = f"⚡ {col_name}" if "Energia" in col_name else col_name
            cols[i].metric(label=label, value=f"{atual}", delta=f"{delta:.1f}" if delta is not None else None)

        # --- GRÁFICOS ---
        st.divider()
        t1, t2 = st.tabs(["📈 Gráficos de Evolução", "📋 Tabela de Dados"])
        
        with t1:
            # Gráfico de Peso e Massa Magra (Se existirem)
            cols_grafico = [c for c in ["Peso", "Massa Magra"] if c in df.columns]
            if cols_grafico:
                st.subheader("Peso e Massa Muscular")
                st.line_chart(df.set_index(col_data)[cols_grafico], color=["#00ff41", "#00d4ff"])
            
            # Gráfico de Energia
            if "Energia" in df.columns:
                st.subheader("Nível de Energia (0-10)")
                st.bar_chart(df.set_index(col_data)['Energia'], color="#ffff00")
            
            # Outras métricas (Gordura, Água, Cintura)
            outras = [c for c in ["Gordura", "Agua", "Cintura"] if c in df.columns]
            if outras:
                st.subheader("Composição e Medidas")
                st.line_chart(df.set_index(col_data)[outras])

        with t2:
            df_view = df.copy()
            df_view[col_data] = df_view[col_data].dt.strftime('%d/%m/%Y')
            st.dataframe(df_view.sort_values(col_data, ascending=False), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        st.info("Verifique se o CSV foi exportado corretamente do Google Sheets.")
else:
    st.info("Aguardando upload do CSV. No Google Sheets: Arquivo > Fazer download > CSV.")
