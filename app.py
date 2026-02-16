import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Body Evolution", page_icon="📊", layout="centered")

# --- BANCO DE DADOS LOCAL ---
def conectar_banco():
    conn = sqlite3.connect('progresso_corpo.db', check_same_thread=False)
    cursor = conn.cursor()
    # Criando a tabela com as variáveis completas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evolucao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            peso REAL,
            cintura REAL,
            pescoco REAL,
            quadril REAL,
            peito REAL,
            biceps REAL,
            coxa REAL,
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
    
    # Peso e Medidas Principais
    peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.1f")
    cintura = st.number_input("Cintura (cm)", min_value=0.0, step=0.1, format="%.1f")
    pescoco = st.number_input("Pescoço (cm)", min_value=0.0, step=0.1, format="%.1f")
    quadril = st.number_input("Quadril (cm)", min_value=0.0, step=0.1, format="%.1f")
    
    # Medidas Musculares
    with st.expander("Ver mais medidas"):
        peito = st.number_input("Peito (cm)", min_value=0.0, step=0.1, format="%.1f")
        biceps = st.number_input("Bíceps (cm)", min_value=0.0, step=0.1, format="%.1f")
        coxa = st.number_input("Coxa (cm)", min_value=0.0, step=0.1, format="%.1f")
    
    notas = st.text_area("Notas do treino/dieta")
    
    if st.button("Salvar Evolução"):
        if peso > 0:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO evolucao (data, peso, cintura, pescoco, quadril, peito, biceps, coxa, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data_sel.strftime("%Y-%m-%d"), peso, cintura, pescoco, quadril, peito, biceps, coxa, notas))
            conn.commit()
            st.success("💪 Evolução guardada!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("O peso é obrigatório.")

# --- VISUALIZAÇÃO ---
df = pd.read_sql_query("SELECT * FROM evolucao", conn)

if not df.empty:
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values("data", ascending=False)

    # Gráficos em abas
    tab1, tab2, tab3 = st.tabs(["Gráficos", "Tabela Completa", "Análise"])
    
    with tab1:
        st.subheader("Peso")
        st.line_chart(df.set_index('data')['peso'])
        
        st.subheader("Medidas (Cintura e Quadril)")
        st.line_chart(df.set_index('data')[['cintura', 'quadril']])

    with tab2:
        df_exibir = df.copy()
        df_exibir['data'] = df_exibir['data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_exibir.drop(columns=['id']), use_container_width=True, hide_index=True)

    with tab3:
        if len(df) >= 2:
            # Cálculo simples de diferença
            ultima = df.iloc[0]
            penultima = df.iloc[1]
            diff_peso = ultima['peso'] - penultima['peso']
            
            st.metric("Variação de Peso", f"{ultima['peso']} kg", f"{diff_peso:.1f} kg")
            st.write(f"**Última nota:** {ultima['notas']}")
        else:
            st.write("Dados insuficientes para análise de variação.")
            
else:
    st.info("Ainda sem registros. Introduza os seus dados na lateral!")
