import streamlit as st
import pandas as pd
import time
import paho.mqtt.client as mqtt
import json
import threading

# =============================
# KONFIGURASI MQTT
# =============================
MQTT_BROKER = "test.mosquitto.org"     # Ganti sesuai broker kamu
MQTT_PORT = 1883
MQTT_TOPIC = "highvoltage/dahsboard"  # Ganti sesuai topic kamu

st.set_page_config(page_title="Monitoring Suhu & Kelembapan", layout="centered")

st.title("🌡️ Sistem Monitoring Suhu & Kelembapan via MQTT")
st.markdown("Dibuat oleh **Tim HighVoltage - MAN 2 Jakarta**")

# =============================
# INISIALISASI DATA
# =============================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Waktu", "Suhu", "Kelembapan"])
if "last_data" not in st.session_state:
    st.session_state.last_data = {"suhu": None, "kelembapan": None}

# =============================
# CALLBACK MQTT
# =============================
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        suhu = float(payload.get("suhu", 0))
        kelembapan = float(payload.get("kelembapan", 0))
        waktu = time.strftime("%H:%M:%S")

        # Simpan ke session state
        st.session_state.last_data = {"suhu": suhu, "kelembapan": kelembapan}
        st.session_state.data.loc[len(st.session_state.data)] = [waktu, suhu, kelembapan]
    except Exception as e:
        print("Error parsing message:", e)

# =============================
# SETUP MQTT CLIENT (PAHO)
# =============================
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

# Jalankan MQTT client di thread terpisah
thread = threading.Thread(target=mqtt_thread, daemon=True)
thread.start()

# =============================
# STREAMLIT DASHBOARD
# =============================
placeholder = st.empty()

while True:
    suhu = st.session_state.last_data["suhu"]
    kelembapan = st.session_state.last_data["kelembapan"]

    with placeholder.container():
        if suhu is not None and kelembapan is not None:
            col1, col2 = st.columns(2)
            col1.metric("🌞 Suhu (°C)", f"{suhu:.1f}")
            col2.metric("💧 Kelembapan (%)", f"{kelembapan:.1f}")

            # Status udara
            if kelembapan < 30:
                st.error("🚨 Udara terlalu kering! Nyalakan humidifier 💧")
            elif kelembapan > 60:
                st.warning("⚠️ Udara terlalu lembab! Gunakan dehumidifier ")
            else:
                st.success("✅ Udara normal dan sehat 🌿")

            # Grafik realtime
            st.subheader("📈 Grafik Suhu & Kelembapan (Realtime)")
            st.line_chart(st.session_state.data.set_index("Waktu")[["Suhu", "Kelembapan"]])
        else:
            st.warning("Menunggu data MQTT...")

        st.markdown("---")
        st.caption("Data otomatis diperbarui setiap 5 detik")

    time.sleep(5)
