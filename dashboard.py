import streamlit as st
import pandas as pd
import json
from paho.mqtt import client as mqtt
import time

# === KONFIGURASI MQTT ===
BROKER = "test.mosquitto.org"  # ganti dengan IP broker lokal jika pakai lokal
PORT = 1883
TOPIC = "highvoltage/dashboard"

# === KONFIGURASI STREAMLIT ===
st.set_page_config(page_title="Monitoring Suhu & Kelembapan", layout="centered")
st.title("🌡️ Sistem Monitoring Suhu dan Kelembapan Ruangan")
st.markdown("Dibuat oleh **Tim HighVoltage - MAN 2 Jakarta**")

# === DATA HISTORIS ===
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Waktu", "Suhu", "Kelembapan"])

# === CALLBACK MQTT ===
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        suhu = payload["suhu"]
        kelembapan = payload["kelembapan"]
        waktu = time.strftime("%H:%M:%S")
        st.session_state.data.loc[len(st.session_state.data)] = [waktu, suhu, kelembapan]
    except Exception as e:
        print(f"Error parsing data: {e}")

# === KONEKSI KE BROKER ===
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# === TAMPILAN DASHBOARD ===
placeholder = st.empty()

while True:
    with placeholder.container():
        if not st.session_state.data.empty:
            suhu = st.session_state.data["Suhu"].iloc[-1]
            kelembapan = st.session_state.data["Kelembapan"].iloc[-1]

            col1, col2 = st.columns(2)
            col1.metric("🌞 Suhu (°C)", f"{suhu:.1f}")
            col2.metric("💧 Kelembapan (%)", f"{kelembapan:.1f}")

            if kelembapan < 30:
                st.error("🚨 Udara terlalu kering!")
            elif kelembapan > 60:
                st.warning("⚠️ Udara terlalu lembab!")
            else:
                st.success("✅ Udara normal dan sehat")

            st.line_chart(st.session_state.data.set_index("Waktu")[["Suhu", "Kelembapan"]])
        else:
            st.info("Menunggu data dari ESP32...")

        time.sleep(2)
