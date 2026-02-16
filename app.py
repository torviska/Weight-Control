import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Body Evolution", page_icon="📊", layout="centered")

# --- BANCO DE DADOS LOCAL (INDESSTRUTÍVEL) ---
def conectar_banco():
    conn = sqlite3.connect('body_evolution_v3.db', check_same_thread=False)
    cursor = conn.cursor()
    # Criando a tabela final com todas as colunas que você quer seguir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progresso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            peso REAL,
            massa_magra REAL,
            gordura REAL,
            cintura REAL,
            agua REAL,
            notas TEXT
        )
    ''')
    conn.commit()
    return conn

conn = conectar_banco()

st.title("📊 Body Evolution")
st.write("Acompanhamento de Composição Corporal")

# --- ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Novo Registro")
    st.write("Insira os dados manualmente abaixo:")
    
    data_sel = st.date_input("Data do Registro", datetime.date.today())
    
    col_a, col_b = st.columns(2)
    with col_a:
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.1f")
        gordura = st.number_input("Gordura (%)", min_value=0.0, step=0.1, format="%.1f")
    with col_b:
        m_magra = st.number_input("M. Magra (kg)", min_value=0.0, step=0.1, format="%.1f")
        agua = st.number_input("Água (%)", min_value=0.0, step=0.1, format="%.1f")
    
    cintura = st.number_input("Cintura (cm)", min_value=0.0, step=0.1, format="%.1f")
    notas = st.text_area("Notas / Observações")
    
    if st.button("Salvar Registro"):
        if peso > 0:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data_sel.strftime("%Y-%m-%d"), peso, m_magra, gordura, cintura, agua, notas))
            conn.commit()
            st.success(f"💪 Registro de {data_sel.strftime('%d/%m')} salvo!")
            st.rerun()
        else:
            st.error("O peso é necessário.")

# --- VISUALIZAÇÃO DOS DADOS ---
df = pd.read_sql_query("SELECT * FROM progresso", conn)

if not df.empty:
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values("data", ascending=False)

    # Gráficos em Abas
    tab1, tab2 = st.tabs(["📈 Evolução", "📜 Histórico"])
    
    with tab1:
        st.subheader("Peso vs Massa Magra")
        st.line_chart(df.set_index('data')[['peso', 'massa_magra']])
        
        st.subheader("Composição (%)")
        st.line_chart(df.set_index('data')[['gordura', 'agua']])
        
        st.subheader("Medida Cintura (cm)")
        st.area_chart(df.set_index('data')['cintura'])

    with tab2:
        df_exibicao = df.copy()
        df_exibicao['data'] = df_exibicao['data'].dt.strftime('%d/%m/%Y')
        # Limpeza visual da tabela
        df_exibicao.columns = ['ID', 'Data', 'Peso (kg)', 'M. Magra (kg)', 'Gordura (%)', 'Cintura (cm)', 'Água (%)', 'Notas']
        st.dataframe(df_exibicao.drop(columns=['ID']), use_container_width=True, hide_index=True)
