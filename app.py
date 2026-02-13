import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# Configuração da página
st.set_page_config(page_title="Weight Control", page_icon="💪", layout="centered")

st.title("📊 Body Evolution (Cloud Save)")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler os dados
def get_data():
    return conn.read(ttl="0s") # ttl=0 garante que ele leia os dados mais recentes

df = get_data()

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
        # Preparar a nova linha
        new_row = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"),
            "Weight": weight,
            "Body Fat (kg)": fat_kg,
            "Muscle Mass": muscle,
            "Waist": waist,
            "Body Water": water
        }])
        
        # Adicionar aos dados existentes
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Salvar na planilha
        conn.update(data=updated_df)
        st.success("Saved to Google Sheets!")
        st.rerun()

# --- VISUALIZAÇÃO ---
if not df.empty:
    st.subheader("Your Progress")
    
    # Seletor de métrica
    metrics_options = ['Weight', 'Body Fat (kg)', 'Muscle Mass', 'Waist', 'Body Water']
    metric = st.selectbox("Select Metric", metrics_options)
    
    # Gráfico
    import plotly.express as px
    fig = px.line(df, x='Date', y=metric, markers=True, title=f"Evolution: {metric}")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.divider()
    st.subheader("Cloud History")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data found in Google Sheets. Add your first entry!")
