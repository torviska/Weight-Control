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
            # Garante que as colunas existam
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
        new_row = {
            'Date': pd.to_datetime(date),
            'Weight': weight,
            'Body Fat (kg)': fat_kg,
            'Muscle Mass': muscle,
            'Waist': waist,
            'Body Water': water
        }
        new_data = pd.DataFrame([new_row])
        df = pd.concat([df, new_data]).drop_duplicates(subset=['Date'], keep='last').sort_values('Date')
        df.to_csv(DATA_FILE, index=False)
        st.success("Saved!")
        st.rerun()

# --- VISUALIZAÇÃO ---
if not df.empty:
    st.subheader("Your Progress")
    
    # Seletor de métrica
    metrics_options = ['Weight', 'Body Fat (kg)', 'Muscle Mass', 'Waist', 'Body Water']
    metric = st.selectbox("Select Metric", metrics_options)
    
    # Gráfico
    fig = px.line(df, x='Date', y=metric, markers=True, title=f"Evolution: {metric}")
    fig.update_layout(hovermode="x unified", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.divider()
    st.subheader("History")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Update History"):
        edited_df.to_csv(DATA_FILE, index=False)
        st.success("Updated!")
        st.rerun()
else:
    st.info("No data yet. use the sidebar to add entries.")
