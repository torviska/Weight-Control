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
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
            # Garante que as colunas existam se o arquivo for antigo
            required_columns = ['Date', 'Weight', 'Body Fat (kg)', 'Muscle Mass', 'Waist', 'Body Water']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0.0
            return df
        except:
            pass
    return pd.DataFrame(columns=['Date', 'Weight', 'Body Fat (kg)', 'Muscle Mass', 'Waist', 'Body Water'])

df = load_data()

st.title("📊 Body Evolution Tracker")

# --- ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Add New Entry")
    date = st.date_input("Date", datetime.date.today())
    weight = st.number_input("Weight (kg)", format="%.2f", step=0.1)
    fat_kg = st.number_input("Body Fat (kg)", format="%.2f", step=0.1)
    muscle = st.number_input("Muscle Mass (kg)", format="%.2f", step=0.1)
    waist = st.number_input("Waist (cm)", format="%.1f", step=0.5)
    water = st.number_input("Body Water (%)", format="%.1f", step=0.1)
    
    if st.button("Save Entry"):
        new_data = pd.DataFrame([[pd.to_datetime(date), weight, fat_kg, muscle, waist, water]], 
                                columns=['Date', 'Weight', 'Body Fat (kg)', 'Muscle Mass', 'Waist', 'Body Water'])
        
        # Remove duplicados da mesma data e ordena
        df = pd.concat([df, new_data]).drop_duplicates(subset=['Date'], keep='last').sort_values('Date')
        df.to_csv(DATA_FILE, index=False)
        st.success("Saved successfully!")
        st.rerun()

# --- VISUALIZAÇÃO ---
if not df.empty:
    st.subheader("Your Progress")
    
    # Seletor de métrica para o gráfico
    metrics_options = ['Weight', 'Body Fat (kg)', 'Muscle Mass', 'Wa
