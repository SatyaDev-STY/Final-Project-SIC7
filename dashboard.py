import streamlit as st
import requests
import time
import pandas as pd

# === KONFIGURASI ===
ESP32_URL = "http://192.168.1.6/data"

st.set_page_config(page_title="Monitoring Suhu & Kelembapan", layout="centered")

st.title("🌡️ Sistem Monitoring Suhu dan Kelembapan Ruangan")
st.markdown("Dibuat oleh **Tim HighVoltage - MAN 2 Jakarta**")

# Inisialisasi session state untuk menyimpan data historis
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Waktu", "Suhu", "Kelembapan"])

# === FUNGSI AMBIL DATA DARI ESP32 ===
def ambil_data():
    try:
        res = requests.get(ESP32_URL, timeout=5)
        if res.status_code == 200:
            data = res.json()
            suhu = data["suhu"]
            kelembapan = data["kelembapan"]
            waktu = time.strftime("%H:%M:%S")

            # Simpan ke DataFrame
            st.session_state.data.loc[len(st.session_state.data)] = [waktu, suhu, kelembapan]
            return suhu, kelembapan
        else:
            return None, None
    except Exception as e:
        st.warning(f"Gagal ambil data: {e}")
        return None, None

# === TAMPILKAN DATA ===
suhu, kelembapan = ambil_data()

if suhu is not None and kelembapan is not None:
    st.metric("🌞 Suhu (°C)", f"{suhu:.1f}")
    st.metric("💧 Kelembapan (%)", f"{kelembapan:.1f}")

    # Logika status udara
    if kelembapan < 30:
        st.error("🚨 Udara terlalu kering!")
    elif kelembapan > 60:
        st.warning("⚠️ Udara terlalu lembab!")
    else:
        st.success("✅ Udara normal dan sehat")

    # === GRAFIK REAL-TIME ===
    st.line_chart(st.session_state.data.set_index("Waktu")[["Suhu", "Kelembapan"]])
else:
    st.warning("Menunggu data dari ESP32...")

# === REFRESH OTOMATIS ===
st.markdown("---")
st.write("🔁 Data otomatis diperbarui setiap 5 detik")
time.sleep(5)
st.experimental_rerun()
