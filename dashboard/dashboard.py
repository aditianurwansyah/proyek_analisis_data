import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema visualisasi
sns.set_theme(style="whitegrid")

# --- JUDUL DASHBOARD ---
st.title("☁️ Kualitas Udara Aotizhongxin")
st.markdown("**Dashboard Analisis Polusi Udara dan Faktor Pendukungnya**")
st.markdown("Dashboard ini dirancang agar selaras dengan seluruh pertanyaan analisis di notebook.")

# --- MEMUAT DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    return df

df = load_data()

# --- FILTER INTERAKTIF (SIDEBAR) ---
st.sidebar.header("🔍 Filter Data Utama")
tahun_tersedia = sorted(df['year'].unique())
tahun_pilihan = st.sidebar.multiselect(
    "Pilih Tahun yang Ingin Ditampilkan:",
    options=tahun_tersedia,
    default=tahun_tersedia
)

if not tahun_pilihan:
    filtered_df = df.copy()
else:
    filtered_df = df[df['year'].isin(tahun_pilihan)].copy()

# --- RINGKASAN METRIK ---
st.markdown("### 📊 Ringkasan Data Utama")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Rata-rata PM2.5", value=f"{filtered_df['PM2.5'].mean():.1f} µg/m³")
with col2:
    st.metric(label="Rata-rata PM10", value=f"{filtered_df['PM10'].mean():.1f} µg/m³")
with col3:
    st.metric(label="Suhu Rata-rata", value=f"{filtered_df['TEMP'].mean():.1f} °C")

st.divider()

# --- VISUALISASI 1: Tren Bulanan (Sesuai Pertanyaan 1 Notebook) ---
st.subheader("1. Tren Rata-rata Tingkat Konsentrasi PM2.5 Bulanan")
st.markdown("Grafik ini menunjukkan fluktuasi rata-rata polusi PM2.5 setiap bulannya.")

monthly_df = filtered_df.groupby('month')['PM2.5'].mean().reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.lineplot(data=monthly_df, x='month', y='PM2.5', marker='o', color='red', linewidth=2, ax=ax1)
ax1.set_xlabel("Bulan", fontsize=11)
ax1.set_ylabel("Rata-rata PM2.5 (µg/m³)", fontsize=11)
ax1.set_xticks(range(1, 13))
ax1.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig1)

# --- VISUALISASI 2: Pengaruh Kecepatan Angin (Sesuai Pertanyaan 2 Notebook - Ramah Non-Teknis) ---
st.subheader("2. Pengaruh Kecepatan Angin Terhadap PM10 (Musim Dingin)")
st.markdown("Menampilkan bagaimana hembusan angin membantu membersihkan polusi PM10 pada musim dingin (Desember - Februari).")

musim_dingin = filtered_df[filtered_df['month'].isin([12, 1, 2])].copy()
if not musim_dingin.empty:
    def kategori_angin(x):
        if x < 1:
            return "1. Sangat Tenang (<1 m/s)"
        elif x <= 3:
            return "2. Sedang (1-3 m/s)"
        else:
            return "3. Kencang (>3 m/s)"
    
    musim_dingin['Kategori Angin'] = musim_dingin['WSPM'].apply(kategori_angin)
    wind_pm10 = musim_dingin.groupby('Kategori Angin')['PM10'].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.barplot(data=wind_pm10, x='Kategori Angin', y='PM10', palette='Blues_d', ax=ax2)
    ax2.set_xlabel("Kondisi Hembusan Angin", fontsize=11)
    ax2.set_ylabel("Rata-rata PM10", fontsize=11)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    st.pyplot(fig2)
else:
    st.warning("Data musim dingin tidak tersedia untuk tahun yang dipilih.")

# --- VISUALISASI 3: Jam Sibuk vs Non-Sibuk 2015 (Sesuai Pertanyaan 3 Notebook) ---
st.subheader("3. Perbandingan Rata-rata PM2.5 pada Jam Sibuk vs Non-Sibuk (Tahun 2015)")
st.markdown("Diagram batang ini membandingkan tingkat polusi antara jam sibuk lalu lintas (07:00-09:00 & 17:00-19:00) dengan jam non-sibuk khusus pada tahun 2015.")

# Memfilter data khusus tahun 2015 untuk visualisasi 3
df_2015_vis = filtered_df[filtered_df['year'] == 2015].copy()

if not df_2015_vis.empty:
    def kategori_jam(hour):
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            return 'Jam Sibuk (07:00-09:00 & 17:00-19:00)'
        else:
            return 'Bukan Jam Sibuk'

    df_2015_vis['kategori_waktu'] = df_2015_vis['hour'].apply(kategori_jam)
    rata_rata_pm25_2015 = df_2015_vis.groupby('kategori_waktu')['PM2.5'].mean().reset_index()

    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.barplot(data=rata_rata_pm25_2015, x='kategori_waktu', y='PM2.5', palette='Set2', ax=ax3)
    ax3.set_xlabel("Kategori Waktu", fontsize=11)
    ax3.set_ylabel("Rata-rata PM2.5 (µg/m³)", fontsize=11)
    ax3.grid(axis='y', linestyle='--', alpha=0.6)
    st.pyplot(fig3)
else:
    st.warning("Tahun 2015 belum dicentang pada filter sidebar di atas. Pastikan tahun 2015 dipilih agar grafik jam sibuk muncul.")
