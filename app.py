import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Body Evolution - Pro", page_icon="⚡", layout="wide")

# Estilo Neon
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stMetricValue"] { color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS LOCAL ---
def conectar_banco():
    conn = sqlite3.connect('body_evolution_v4.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progresso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT, peso REAL, massa_magra REAL, 
            gordura REAL, cintura REAL, agua REAL, energia REAL, notas TEXT
        )
    ''')
    conn.commit()
    return conn

conn = conectar_banco()

st.title("📊 BODY EVOLUTION PRO")

# --- BARRA LATERAL: ENTRADA MANUAL E IMPORTAÇÃO ---
with st.sidebar:
    st.header("⚙️ Gestão de Dados")
    
    # Aba de Upload (Caso o histórico suma)
    with st.expander("📤 Importar Backup CSV"):
        arquivo_subido = st.file_uploader("Suba o CSV do Google Sheets", type="csv")
        if arquivo_subido:
            try:
                # Tenta ler com decimal , ou .
                try: df_imp = pd.read_csv(arquivo_subido, decimal=',')
                except: df_imp = pd.read_csv(arquivo_subido, decimal='.')
                
                # Limpa a tabela atual e insere os dados do CSV
                if st.button("Confirmar Importação"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM progresso") # Limpa para não duplicar
                    for _, row in df_imp.iterrows():
                        cursor.execute('''
                            INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, energia, notas)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (str(row[0]), float(row[1]), float(row[2]), float(row[3]), 
                              float(row[4]), float(row[5]), float(row[6]), str(row[7]) if len(row)>7 else ""))
                    conn.commit()
                    st.success("Backup restaurado!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro no CSV: {e}")

    st.divider()
    
    # Formulário Manual
    st.header("📝 Registro do Dia")
    d_data = st.date_input("Data", datetime.date.today())
    d_peso = st.number_input("Peso (kg)", format="%.1f")
    d_magra = st.number_input("M. Magra (kg)", format="%.1f")
    d_gord = st.number_input("Gordura (%)", format="%.1f")
    d_cint = st.number_input("Cintura (cm)", format="%.1f")
    d_agua = st.number_input("Água (%)", format="%.1f")
    d_ener = st.slider("Energia (0-10)", 0, 10, 8)
    d_notas = st.text_area("Notas")
    
    if st.button("🚀 Salvar Registro"):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, energia, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (d_data.strftime("%Y-%m-%d"), d_peso, d_magra, d_gord, d_cint, d_agua, d_ener, d_notas))
        conn.commit()
        st.success("Salvo localmente!")
        st.rerun()

# --- VISUALIZAÇÃO ---
df = pd.read_sql_query("SELECT * FROM progresso", conn)

if not df.empty:
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values
