import streamlit as st
from paho.mqtt import client as mqtt
import pandas as pd
import json
import time

# === KONFIGURASI MQTT ===
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "highvoltage/dashboard"
CLIENT_ID = "mqttx_4211c8fd"

# === KONFIGURASI STREAMLIT ===
st.set_page_config(page_title="Monitoring Suhu & Kelembapan", layout="centered")
st.title("🌡️ Sistem Monitoring Suhu dan Kelembapan Ruangan")
st.markdown("Dibuat oleh **Tim HighVoltage - MAN 2 Jakarta**")

# === INISIALISASI DATA ===
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Waktu", "Suhu", "Kelembapan"])

# === CALLBACK MQTT ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.connected = True
        client.subscribe(TOPIC)
        print("Terhubung ke broker MQTT dan subscribe ke topik:", TOPIC)
    else:
        print("Gagal terhubung ke broker, kode:", rc)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        suhu = float(data.get("suhu", 0))
        kelembapan = float(data.get("kelembapan", 0))
        waktu = time.strftime("%H:%M:%S")

        # Simpan ke DataFrame
        st.session_state.data.loc[len(st.session_state.data)] = [waktu, suhu, kelembapan]
        st.session_state.latest_suhu = suhu
        st.session_state.latest_kelembapan = kelembapan

    except Exception as e:
        print("Error parsing message:", e)

# === SETUP CLIENT MQTT ===
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()
except Exception as e:
    st.error(f"Gagal terhubung ke broker MQTT: {e}")

# === TAMPILKAN DATA DI DASHBOARD ===
if "latest_suhu" in st.session_state and "latest_kelembapan" in st.session_state:
    suhu = st.session_state.latest_suhu
    kelembapan = st.session_state.latest_kelembapan

    st.metric("🌞 Suhu (°C)", f"{suhu:.1f}")
    st.metric("💧 Kelembapan (%)", f"{kelembapan:.1f}")

    if kelembapan < 30:
        st.error("🚨 Udara terlalu kering!")
    elif kelembapan > 60:
        st.warning("⚠️ Udara terlalu lembab!")
    else:
        st.success("✅ Udara normal dan sehat")

    st.line_chart(st.session_state.data.set_index("Waktu")[["Suhu", "Kelembapan"]])
else:
    st.warning("Menunggu data dari ESP32...")

st.markdown("---")
st.write("🔁 Data diperbarui otomatis setiap 5 detik")
time.sleep(5)
st.rerun()
