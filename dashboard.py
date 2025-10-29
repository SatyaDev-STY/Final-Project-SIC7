import streamlit as st
from paho.mqtt import client as mqtt
import json
import pandas as pd
import time

# === KONFIGURASI MQTT ===
BROKER = "broker.emqx.io"  # ganti jika pakai broker lokal
PORT = 1883
TOPIC = "highvoltage/dashboard"
CLIENT_ID = "mqttx_378f4f86"

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="Monitoring Suhu & Kelembapan", layout="centered")
st.title("🌡️ Sistem Monitoring Suhu dan Kelembapan Ruangan")
st.markdown("Dibuat oleh **Tim HighVoltage - MAN 2 Jakarta**")

# === DATA HISTORIS ===
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Waktu", "Suhu", "Kelembapan"])

# === MQTT CALLBACK ===
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        suhu = data["suhu"]
        kelembapan = data["kelembapan"]
        waktu = time.strftime("%H:%M:%S")

        st.session_state.data.loc[len(st.session_state.data)] = [waktu, suhu, kelembapan]
        st.session_state.suhu = suhu
        st.session_state.kelembapan = kelembapan
    except Exception as e:
        st.warning(f"Error parsing data: {e}")

# === KONEKSI MQTT ===
client = mqtt.Client(client_id=CLIENT_ID)
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# === LOOP DASHBOARD ===
placeholder = st.empty()

while True:
    if "suhu" in st.session_state and "kelembapan" in st.session_state:
        suhu = st.session_state.suhu
        kelembapan = st.session_state.kelembapan

        with placeholder.container():
            st.metric("🌞 Suhu (°C)", f"{suhu:.1f}")
            st.metric("💧 Kelembapan (%)", f"{kelembapan:.1f}")

            if kelembapan < 30:
                st.error("🚨 Udara terlalu kering!")
            elif kelembapan > 60:
                st.warning("⚠️ Udara terlalu lembab!")
            else:
                st.success("✅ Udara normal dan sehat")

            st.line_chart(st.session_state.data.set_index("Waktu")[["Suhu", "Kelembapan"]])

    time.sleep(5)




