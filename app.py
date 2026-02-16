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

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Gestão de Dados")
    
    with st.expander("📤 Importar Backup CSV"):
        arquivo_subido = st.file_uploader("Suba o CSV do Google Sheets", type="csv")
        if arquivo_subido:
            try:
                # Tenta ler com decimal , ou .
                try: df_imp = pd.read_csv(arquivo_subido, decimal=',')
                except: df_imp = pd.read_csv(arquivo_subido, decimal='.')
                
                if st.button("Confirmar Importação"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM progresso")
                    
                    for _, row in df_imp.iterrows():
                        # Lógica flexível: se a coluna não existir no CSV, usa 0 ou ""
                        # row[0]=Data, row[1]=Peso, row[2]=M.Magra, row[3]=Gordura, row[4]=Cintura, row[5]=Agua, row[6]=Energia, row[7]=Notas
                        d = str(row[0])
                        p = float(row[1]) if len(row) > 1 else 0.0
                        m = float(row[2]) if len(row) > 2 else 0.0
                        g = float(row[3]) if len(row) > 3 else 0.0
                        c = float(row[4]) if len(row) > 4 else 0.0
                        a = float(row[5]) if len(row) > 5 else 0.0
                        e = float(row[6]) if len(row) > 6 else 0.0
                        n = str(row[7]) if len(row) > 7 else ""
                        
                        cursor.execute('''
                            INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, energia, notas)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (d, p, m, g, c, a, e, n))
                    
                    conn.commit()
                    st.success("Dados importados!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro no CSV: {e}")

    st.divider()
    st.header("📝 Registro Manual")
    d_data = st.date_input("Data", datetime.date.today())
    d_peso = st.number_input("Peso (kg)", format="%.1f")
    d_magra = st.number_input("M. Magra (kg)", format="%.1f")
    d_gord = st.number_input("Gordura (%)", format="%.1f")
    d_cint = st.number_input("Cintura (cm)", format="%.1f")
    d_agua = st.number_input("Água (%)", format="%.1f")
    d_ener = st.slider("Energia (0-10)", 0, 10, 8)
    d_notas = st.text_area("Notas")
    
    if st.button("🚀 Salvar"):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, energia, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (d_data.strftime("%Y-%m-%d"), d_peso, d_magra, d_gord, d_cint, d_agua, d_ener, d_notas))
        conn.commit()
        st.rerun()

# --- VISUALIZAÇÃO ---
df = pd.read_sql_query("SELECT * FROM progresso", conn)

if not df.empty:
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values("data")

    # Métricas
    cols_nomes = ["peso", "massa_magra", "gordura", "cintura", "agua", "energia"]
    m_cols = st.columns(len(cols_nomes))
    for i, c in enumerate(cols_nomes):
        val = df[c].iloc[-1]
        dif = val - df[c].iloc[-2] if len(df) > 1 else 0
        m_cols[i].metric(c.replace("_", " ").title(), f"{val}", f"{dif:.1f}")

    st.divider()
    t1, t2 = st.tabs(["📈 Gráficos", "📋 Tabela"])
    with t1:
        st.line_chart(df.set_index('data')[['peso', 'massa_magra']], color=["#00ff41", "#00d4ff"])
        st.bar_chart(df.set_index('data')['energia'], color="#ffff00")
    with t2:
        st.dataframe(df.sort_values("data", ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("Sem dados. Use a lateral.")
