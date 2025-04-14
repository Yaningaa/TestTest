
# Energiefluss-Demo-App (Startfehler korrigiert: set_page_config zuerst!)

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="🔋 Energieflusss-Demo", page_icon="☀️")

sprachwahl = st.sidebar.selectbox("🌍 Sprache / Language", ["Deutsch", "English"])
lang = "de" if sprachwahl == "Deutsch" else "en"

texts = {
    "de": {
        "title": "🔋 Energieflusss-Demo",
        "household": "Haushaltsgröße (1–8 Personen)",
        "wallbox": "🚗 Wallbox",
        "heatpump": "❄️ Wärmepumpe",
        "ac": "🌿 Klimaanlage",
        "solar": "☀️ PV-Erzeugung",
        "battery": "🔋 Batterie",
        "battery_level": "Füllstand",
        "co2_saving": "CO₂ Ersparnis",
        "savings": "Ersparnis",
        "note": "*Diese Demo dient der Veranschaulichung typischer Energieflüsse eines modernen Haushalts.*",
        "economy": "📊 Wirtschaftlichkeitsvergleich",
        "scenarios": "🔀 Szenarienvergleich: mit/ohne Speicher",
        "diagram": "🏠 Energiefluss-Visualisierung",
        "weather": "☁️ Wettersimulation"
    },
    "en": {
        "title": "🔋 Energy Flow Demo",
        "household": "Household Size (1–8 people)",
        "wallbox": "🚗 Wallbox",
        "heatpump": "❄️ Heat Pump",
        "ac": "🌿 Air Conditioner",
        "solar": "☀️ Solar Generation",
        "battery": "🔋 Battery",
        "battery_level": "Battery Level",
        "co2_saving": "CO₂ Savings",
        "savings": "Cost Savings",
        "note": "*This demo illustrates typical energy flows of a modern household.*",
        "economy": "📊 Economic Comparison",
        "scenarios": "🔀 Scenario Comparison: with/without Storage",
        "diagram": "🏠 Energy Flow Visualization",
        "weather": "☁️ Weather Simulation"
    }
}[lang]

st.markdown("""<style>
html, body, [class*="css"] {
    background-color: #042f2e;
    color: white;
}
.metric-label { color: #a8d97f !important; }
.stSlider > div > div { background-color: #97bf0d; }
</style>""", unsafe_allow_html=True)

st.title(texts["title"])

col_sidebar1, col_sidebar2 = st.sidebar.columns(2)
wetter = col_sidebar1.radio(texts["weather"], ["Sonne", "Wintersonne", "Schnee", "Bewölkt"], index=0)
haushalt = col_sidebar2.slider(texts["household"], 1, 8, 4)

wallbox = st.sidebar.checkbox(texts["wallbox"], True)
waermepumpe = st.sidebar.checkbox(texts["heatpump"], False)
klimaanlage = st.sidebar.checkbox(texts["ac"], False)

zeit = pd.date_range("00:00", "23:45", freq="15min")

def pv_erzeugung(wettertyp):
    tagesverlauf = np.sin(np.linspace(0, np.pi, len(zeit)))
    faktor = {
        "Sonne": 1.0,
        "Wintersonne": 0.6,
        "Bewölkt": 0.4,
        "Schnee": 0.2,
    }[wettertyp]
    return pd.Series(tagesverlauf * faktor * 7, index=zeit)

def lastprofil_h0(personen):
    h0_basis = np.array([
        0.25, 0.22, 0.20, 0.18, 0.20, 0.35, 0.60, 0.80,
        0.70, 0.60, 0.50, 0.45, 0.40, 0.42, 0.50, 0.60,
        0.75, 0.85, 0.90, 0.80, 0.60, 0.45, 0.35, 0.30
    ])
    h0_interp = np.repeat(h0_basis, 4)
    tagesverbrauch = 2.5 * personen
    return pd.Series(h0_interp * tagesverbrauch / h0_interp.sum(), index=zeit)

pv = pv_erzeugung(wetter)
verbrauch = lastprofil_h0(haushalt)

st.subheader(texts["diagram"])
st.image("https://raw.githubusercontent.com/yourusername/yourrepo/main/hausgrafik.png", caption="Energiefluss-Diagramm", use_column_width=True)

col_steuerung, col_visual, col_metrics = st.columns([1, 2, 1])

with col_steuerung:
    st.markdown(f"**{texts['solar']}:** {pv.max():.1f} kW (⌀ {pv.mean():.2f})")
    st.markdown(f"**Hausverbrauch:** {verbrauch.mean():.2f} kW")
    st.markdown(f"**{texts['battery']}:**")
    soc = 60
    st.progress(soc / 100)
    st.markdown(f"{texts['battery_level']}: **{soc}%**")

with col_visual:
    df = pd.DataFrame({"PV [kW]": pv, "Verbrauch [kW]": verbrauch})
    st.line_chart(df)

with col_metrics:
    co2_kg = sum(pv - verbrauch if (pv > verbrauch).any() else 0) * 0.4
    kosten_eur = sum(verbrauch - pv if (verbrauch > pv).any() else 0) * 0.3
    st.metric(texts["co2_saving"], f"{co2_kg:.0f} kg")
    st.metric(texts["savings"], f"{kosten_eur:.2f} €")

st.markdown("---")
st.subheader(texts["scenarios"])
eigenverbrauch_ohne = np.minimum(pv, verbrauch)
autarkie_ohne = 100 * eigenverbrauch_ohne.sum() / verbrauch.sum()
autarkie_mit = min(autarkie_ohne + 20, 100)

col1, col2 = st.columns(2)
col1.metric("Autarkie ohne Speicher [%]", f"{autarkie_ohne:.1f}")
col2.metric("Autarkie mit Speicher [%]", f"{autarkie_mit:.1f}")

st.subheader(texts["economy"])
sparpotenzial = kosten_eur * 12
co2_potenzial = co2_kg * 12
st.markdown(f"**Jährliche Ersparnis:** {sparpotenzial:.2f} €")
st.markdown(f"**Jährliche CO₂-Einsparung:** {co2_potenzial:.0f} kg")

st.markdown("---")
st.markdown(texts["note"])
