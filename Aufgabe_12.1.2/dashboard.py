import streamlit as st
from tinydb import TinyDB
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="IIOT Dashboard", layout="wide")

st.title("🏭 IIOT Learning Factory Live Dashboard")

db = TinyDB('bottles_data.json')

st.sidebar.title("Einstellungen")
auto_refresh = st.sidebar.checkbox("Auto-Refresh (1s)", value=True)

docs = db.all()
df = pd.DataFrame(docs)

if not df.empty:
    numeric_columns = [col for col in df.columns if col not in ['bottle', 'recipe', 'drop_oscillation', 'is_cracked', 'timestamp']]
    
    selected_topics = st.sidebar.multiselect(
        "Wähle Topics (Parameter) zum Plotten:", 
        options=numeric_columns, 
        default=['vibration_red', 'vibration_blue', 'vibration_green']
    )
    
    st.markdown(f"**Anzahl der Flaschen in der DB:** {len(df)}")
    
    if selected_topics:
        # Use numeric order for bottles, but show the IDs as categorical labels
        df['bottle'] = df['bottle'].astype(str)
        df['bottle_order'] = pd.to_numeric(df['bottle'], errors='coerce')
        df = df.sort_values('bottle_order')
        df['bottle_str'] = df['bottle']

        fig = px.line(
            df,
            x='bottle_str',
            y=selected_topics,
            markers=True,
            title="Werteverlauf pro Flasche",
            labels={"bottle_str": "Flaschen ID", "value": "Messwert", "variable": "Sensor/Topic"}
        )
        fig.update_xaxes(type='category', tickangle=-45, tickmode='auto')
        st.plotly_chart(fig, use_container_width=True)

        # Zeitdiagramm mit Zeitstempel
        df_time = df.copy()
        if 'timestamp' in df_time.columns:
            df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], errors='coerce')
            time_df = df_time.dropna(subset=['timestamp'])
            if not time_df.empty:
                fig_time = px.line(
                    time_df,
                    x='timestamp',
                    y=selected_topics,
                    markers=True,
                    title="Zeitliche Entwicklung ausgewählter Parameter",
                    labels={"timestamp": "Zeit", "value": "Messwert", "variable": "Sensor/Topic"}
                )
                fig_time.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.warning("Für das Zeitdiagramm sind noch keine gültigen Zeitstempel vorhanden.")
        else:
            st.warning("Die Daten enthalten keinen Zeitstempel für das Zeitdiagramm.")
    else:
        st.info("Bitte mindestens ein Topic aus der linken Leiste auswählen.")
        
    st.subheader("Neueste Daten (Tabelle):")
    st.dataframe(df.tail(10))
    
else:
    st.warning("Keine Daten in der Datenbank (bottles_data.json) gefunden. Läuft das MQTT Skript?")

if auto_refresh:
    time.sleep(1)
    st.rerun()
