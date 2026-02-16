import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Body Evolution", page_icon="📊", layout="centered")

# --- BANCO DE DADOS LOCAL ---
def conectar_banco():
    conn = sqlite3.connect('progresso_peso.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela para controle de peso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peso_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            peso REAL,
            cintura REAL,
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
    cintura = st.number_input("Cintura (cm)", min_value=0.0, step=0.5, format="%.1f")
    notas = st.text_area("Notas")
    
    if st.button("Salvar Progresso"):
        if peso > 0:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO peso_historico (data, peso, cintura, notas)
                VALUES (?, ?, ?, ?)
            ''', (data_sel.strftime("%Y-%m-%d"), peso, cintura, notas))
            conn.commit()
            st.success("💪 Registrado com sucesso!")
            st.rerun()
        else:
            st.error("Insira o seu peso.")

# --- VISUALIZAÇÃO ---
df = pd.read_sql_query("SELECT * FROM peso_historico", conn)

if not df.empty:
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values("data", ascending=False)

    # Gráfico de Evolução
    st.subheader("Evolução do Peso")
    st.line_chart(df.set_index('data')['peso'])

    # Tabela de Histórico
    st.divider()
    st.subheader("Histórico de Medidas")
    df_exibir = df.copy()
    df_exibir['data'] = df_exibir['data'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_exibir.drop(columns=['id']), use_container_width=True, hide_index=True)
    
    if st.checkbox("Limpar histórico"):
        if st.button("Confirmar exclusão de tudo"):
            conn.cursor().execute("DELETE FROM peso_historico")
            conn.commit()
            st.rerun()
else:
    st.info("Ainda não há registros. Comece hoje seu acompanhamento!")
