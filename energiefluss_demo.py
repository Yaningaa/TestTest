
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -------- Datenmodell --------
@st.cache_data
def generate_time_series():
    return pd.date_range("00:00", "23:45", freq="15min").time

def simulate_pv_curve():
    return np.maximum(0, 5 * np.sin(np.linspace(0, np.pi, 96)))

def simulate_consumption(bewohner):
    base_profile = np.array([
        0.2, 0.18, 0.17, 0.16, 0.2, 0.4, 0.6, 0.5, 0.4, 0.35, 0.3, 0.25,
        0.3, 0.4, 0.6, 0.7, 0.9, 1.0, 1.1, 1.0, 0.9, 0.6, 0.4, 0.3
    ])
    return np.repeat(base_profile, 4) * bewohner

def generate_device_profiles(active_wallbox, active_wp, active_klima):
    wallbox = np.zeros(96)
    if active_wallbox:
        wallbox[60:68] = 3.7
    wp = np.full(96, 0.5 if active_wp else 0)
    klima = np.zeros(96)
    if active_klima:
        klima[40:80] = 1.2
    return wallbox, wp, klima

def get_tarif_array(use_standard):
    if use_standard:
        return np.full(96, 0.30)
    else:
        return 0.05 + 0.25 * np.abs(np.sin(np.linspace(0, 3*np.pi, 96)))

# -------- UI: Sidebar --------
st.set_page_config(page_title="Energiefluss-Demo", layout="wide")
st.sidebar.title("⚙️ Einstellungen")

bewohner = st.sidebar.slider("Anzahl Bewohner", 1, 6, 4)
active_wallbox = st.sidebar.checkbox("Wallbox aktivieren", True)
active_wp = st.sidebar.checkbox("Wärmepumpe aktivieren", True)
active_klima = st.sidebar.checkbox("Klimaanlage aktivieren", True)
tariftyp = st.sidebar.radio("Tarifwahl", ["Standard (30 ct/kWh)", "Dynamisch (Börse)"])

# -------- Daten erzeugen --------
zeit = generate_time_series()
pv = simulate_pv_curve()
haushalt = simulate_consumption(bewohner)
wallbox, wp, klima = generate_device_profiles(active_wallbox, active_wp, active_klima)
verbrauch = haushalt + wallbox + wp + klima
tarif = get_tarif_array(tariftyp.startswith("Standard"))

# Stromkosten
verbrauch_kwh = verbrauch * 0.25
kosten = np.sum(verbrauch_kwh * tarif)

# -------- UI Layout --------
col1, col2 = st.columns([3, 1])
col1.title("🔋 Interaktive Energiefluss-Demo")
col2.metric("Gesamtkosten", f"{kosten:.2f} €", help="Basierend auf gewähltem Tarif und Tagesverbrauch")

# -------- Plot 1: PV vs Verbrauch --------
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=zeit, y=pv, mode="lines", name="PV-Produktion", line=dict(width=3)))
fig1.add_trace(go.Scatter(x=zeit, y=verbrauch, mode="lines", name="Gesamtverbrauch", line=dict(width=3)))
fig1.update_layout(
    title="Energiefluss über den Tag",
    xaxis_title="Zeit",
    yaxis_title="Leistung (kW)",
    legend=dict(orientation="h", y=1.15),
    margin=dict(t=50, b=20),
    height=400,
)

# -------- Plot 2: Tarifverlauf --------
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=zeit, y=tarif, mode="lines", name="Strompreis", line=dict(width=3)))
fig2.update_layout(
    title="Strompreisentwicklung",
    xaxis_title="Zeit",
    yaxis_title="Preis (€/kWh)",
    margin=dict(t=50, b=20),
    height=300,
)

# -------- Anzeigen --------
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# -------- Debug/Export --------
with st.expander("📄 Rohdaten anzeigen"):
    df = pd.DataFrame({
        "Zeit": zeit,
        "PV": pv,
        "Haushalt": haushalt,
        "Wallbox": wallbox,
        "Wärmepumpe": wp,
        "Klimaanlage": klima,
        "Gesamtverbrauch": verbrauch,
        "Tarif": tarif,
        "Kosten (15min)": verbrauch_kwh * tarif
    })
    st.dataframe(df, use_container_width=True)
