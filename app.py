import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

# Configuração da página para Mobile
st.set_page_config(page_title="Body Evolution", layout="centered")

# Nome do arquivo de dados
DATA_FILE = "body_data.csv"

# Função para carregar dados
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=['Date'])
    return pd.DataFrame(columns=['Date', 'Weight', 'Body Fat', 'Muscle Mass', 'Waist', 'Body Water'])

df = load_data()

st.title("📊 Body Evolution Tracker")

# --- ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Add New Entry")
    date = st.date_input("Date", datetime.date.today())
    weight = st.number_input("Weight (kg)", format="%.2f")
    fat = st.number_input("Body Fat (%)", format="%.1f")
    muscle = st.number_input("Muscle Mass (kg)", format="%.2f")
    waist = st.number_input("Waist (cm)", format="%.1f")
    water = st.number_input("Body Water (%)", format="%.1f")
    
    if st.button("Save Entry"):
        new_data = pd.DataFrame([[pd.to_datetime(date), weight, fat, muscle, waist, water]], 
                                columns=df.columns)
        df = pd.concat([df, new_data]).drop_duplicates(subset=['Date'], keep='last').sort_values('Date')
        df.to_csv(DATA_FILE, index=False)
        st.success("Saved!")

# --- VISUALIZAÇÃO ---
if not df.empty:
    st.subheader("Your Progress")
    
    # Seletor de métrica para o gráfico
    metric = st.selectbox("Select Metric", ['Weight', 'Body Fat', 'Muscle Mass', 'Waist', 'Body Water'])
    
    # Gráfico Interativo Plotly
    fig = px.line(df, x='Date', y=metric, markers=True, 
                 title=f"Evolution: {metric}",
                 template="plotly_white")
    
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela editável
    st.subheader("Edit History")
    edited_df = st.data_editor(df, num_rows="dynamic")
    
    if st.button("Update History"):
        edited_df.to_csv(DATA_FILE, index=False)
        st.rerun()
else:
    st.info("No data yet. Use the sidebar to add your first entry!")
