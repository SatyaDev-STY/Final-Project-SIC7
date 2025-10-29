import streamlit as st
import requests
import time

ESP32_IP = "http://192.168.1.6/data"  # Ganti dengan IP ESP32 kamu

st.title("🌡️ Monitoring Suhu & Kelembapan Ruangan")
st.write("Mengirim Data Dari ESP32")

temp_placeholder = st.empty()
hum_placeholder = st.empty()
status_placeholder = st.empty()

while True:
    try:
        res = requests.get(ESP32_IP)
        data = res.json()

        suhu = data["suhu"]
        kelembapan = data["kelembapan"]

        temp_placeholder.metric("Suhu (°C)", f"{suhu:.1f}")
        hum_placeholder.metric("Kelembapan (%)", f"{kelembapan:.1f}")

        if kelembapan < 30:
            status_placeholder.error("Udara tidak sehat: terlalu kering!")
        elif kelembapan > 60:
            status_placeholder.warning("Udara tidak sehat: terlalu lembab!")
        else:
            status_placeholder.success("Udara normal ✅")

        time.sleep(2)

    except Exception as e:
        st.error(f"Gagal ambil data: {e}")
        time.sleep(3)
