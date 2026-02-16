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
    conn = sqlite3.connect('body_evolution_v6.db', check_same_thread=False)
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
        st.info("Ordem esperada: Data | Peso | Gordura | Massa Magra | Cintura | Energia")
        arquivo_subido = st.file_uploader("Suba o CSV", type="csv")
        
        if arquivo_subido:
            try:
                # Tenta ler com vírgula ou ponto
                try: df_imp = pd.read_csv(arquivo_subido, decimal=',')
                except: df_imp = pd.read_csv(arquivo_subido, decimal='.')
                
                if st.button("Confirmar Importação"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM progresso") 
                    
                    # Correção de Datas (Blinda contra erros de data)
                    df_imp.iloc[:, 0] = pd.to_datetime(df_imp.iloc[:, 0], dayfirst=True, errors='coerce')
                    df_imp = df_imp.dropna(subset=[df_imp.columns[0]]) 
                    
                    count = 0
                    for _, row in df_imp.iterrows():
                        # --- MAPEAMENTO DA SUA NOVA PLANILHA ---
                        # Coluna A [0] -> Data
                        d = row.iloc[0].strftime("%Y-%m-%d")
                        
                        # Coluna B [1] -> Peso
                        p = float(row.iloc[1]) if len(row) > 1 else 0.0
                        
                        # Coluna C [2] -> Gordura (Mudou de lugar!)
                        g = float(row.iloc[2]) if len(row) > 2 else 0.0
                        
                        # Coluna D [3] -> Massa Magra (Mudou de lugar!)
                        m = float(row.iloc[3]) if len(row) > 3 else 0.0
                        
                        # Coluna E [4] -> Cintura
                        c = float(row.iloc[4]) if len(row) > 4 else 0.0
                        
                        # Coluna F [5] -> Energia
                        e = float(row.iloc[5]) if len(row) > 5 else 0.0
                        
                        # Coluna G -> Agua (Não está na imagem, definindo padrão 0)
                        a = float(row.iloc[6]) if len(row) > 6 else 0.0
                        
                        # Notas
                        n = str(row.iloc[7]) if len(row) > 7 else ""
                        
                        cursor.execute('''
                            INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, energia, notas)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (d, p, m, g, c, a, e, n))
                        count += 1
                    
                    conn.commit()
                    st.success(f"{count} registros importados com a nova ordem!")
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
    d_ener = st.slider("Energia (0-10)", 0, 10, 8)
    d_agua = st.number_input("Água (%)", format="%.1f") # Mantive manual se quiseres inserir
    d_notas = st.text_area("Notas")
    
    if st.button("🚀 Salvar"):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, energia, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (d_data.strftime("%Y-%m-%d"), d_peso, d_magra, d_gord, d_cint, d_agua, d_ener, d_notas))
        conn.commit()
        st.success("Salvo!")
        st.rerun()

# --- VISUALIZAÇÃO ---
try:
    df = pd.read_sql_query("SELECT * FROM progresso", conn)

    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df = df.dropna(subset=['data'])
        df = df.sort_values("data")

        if not df.empty:
            # Métricas Recentes
            cols_nomes = ["peso", "gordura", "massa_magra", "cintura", "energia"]
            m_cols = st.columns(len(cols_nomes))
            for i, c in enumerate(cols_nomes):
                if c in df.columns:
                    val = df[c].iloc[-1]
                    dif = val - df[c].iloc[-2] if len(df) > 1 else 0
                    m_cols[i].metric(c.replace("_", " ").title(), f"{val}", f"{dif:.1f}")

            st.divider()
            t1, t2 = st.tabs(["📈 Gráficos", "📋 Tabela"])
            with t1:
                st.line_chart(df.set_index('data')[['peso', 'massa_magra']], color=["#00ff41", "#00d4ff"])
                
                c1, c2 = st.columns(2)
                with c1: st.area_chart(df.set_index('data')['gordura'], color="#ff0055")
                with c2: st.bar_chart(df.set_index('data')['energia'], color="#ffff00")
                
            with t2:
                st.dataframe(df.sort_values("data", ascending=False), use_container_width=True, hide_index=True)
        else:
             st.warning("Dados inválidos. Importe o CSV novamente.")
    else:
        st.info("Sem dados. Importe o CSV na lateral.")

except Exception as e:
    st.error(f"Erro: {e}")
