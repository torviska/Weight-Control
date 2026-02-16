import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Body Evolution", page_icon="📊", layout="centered")

# --- BANCO DE DADOS LOCAL ---
def conectar_banco():
    conn = sqlite3.connect('body_evolution.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela com as variáveis solicitadas
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

# --- ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Novo Registro")
    data_sel = st.date_input("Data", datetime.date.today())
    
    peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.1f")
    massa_magra = st.number_input("Massa Magra (kg)", min_value=0.0, step=0.1, format="%.1f")
    gordura = st.number_input("Gordura (%)", min_value=0.0, step=0.1, format="%.1f")
    cintura = st.number_input("Cintura (cm)", min_value=0.0, step=0.1, format="%.1f")
    agua = st.number_input("Água (%)", min_value=0.0, step=0.1, format="%.1f")
    
    notas = st.text_area("Notas (Treino/Dieta)")
    
    if st.button("Salvar Registro"):
        if peso > 0:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO progresso (data, peso, massa_magra, gordura, cintura, agua, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data_sel.strftime("%Y-%m-%d"), peso, massa_magra, gordura, cintura, agua, notas))
            conn.commit()
            st.success("💪 Dados salvos com sucesso!")
            st.rerun()
        else:
            st.error("O peso é obrigatório para salvar.")

# --- VISUALIZAÇÃO ---
df = pd.read_sql_query("SELECT * FROM progresso", conn)

if not df.empty:
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values("data", ascending=False)

    tab1, tab2 = st.tabs(["Evolução Visual", "Histórico de Dados"])
    
    with tab1:
        st.subheader("Evolução do Peso e Massa Magra")
        st.line_chart(df.set_index('data')[['peso', 'massa_magra']])
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Gordura Corporal (%)")
            st.line_chart(df.set_index('data')['gordura'])
        with col2:
            st.subheader("Água Corporal (%)")
            st.line_chart(df.set_index('data')['agua'])

    with tab2:
        df_exibir = df.copy()
        df_exibir['data'] = df_exibir['data'].dt.strftime('%d/%m/%Y')
        # Renomeando colunas para a tabela ficar amigável
        df_exibir.columns = ['ID', 'Data', 'Peso (kg)', 'M. Magra (kg)', 'Gordura (%)',
