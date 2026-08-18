import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema visualisasi
sns.set_theme(style="whitegrid")

# 1. Menyiapkan Judul Dashboard yang Menarik
st.title("☁️ Kualitas Udara Aotizhongxin")
st.markdown("**Menelusuri Jejak Polusi Udara (PM2.5) dan Cara Menghindarinya**")
st.markdown("Dashboard ini dirancang untuk membantu masyarakat memahami kapan polusi udara berada di titik terburuk dan faktor alam apa yang mempengaruhinya.")

# 2. Memuat Data
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    return df

df = load_data()

# --- 3. FITUR BARU: FILTER INTERAKTIF (SIDEBAR) ---
st.sidebar.header("🔍 Filter Data")

# Mengambil daftar tahun unik dari dataset
tahun_tersedia = sorted(df['year'].unique())
tahun_pilihan = st.sidebar.multiselect(
    "Pilih Tahun yang Ingin Ditampilkan:",
    options=tahun_tersedia,
    default=tahun_tersedia # Secara default menampilkan semua tahun
)

# Filter dataset berdasarkan pilihan tahun di sidebar
# Jika tidak ada tahun yang dipilih, tampilkan semua data agar tidak error
if not tahun_pilihan:
    filtered_df = df.copy()
else:
    filtered_df = df[df['year'].isin(tahun_pilihan)].copy()

# --- 4. MENAMPILKAN METRIK UTAMA ---
st.markdown("### 📊 Ringkasan Data Utama")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Rata-rata Polusi PM2.5", value=f"{filtered_df['PM2.5'].mean():.1f} µg/m³")
with col2:
    st.metric(label="Suhu Rata-rata", value=f"{filtered_df['TEMP'].mean():.1f} °C")
with col3:
    st.metric(label="Titik Polusi Tertinggi", value=f"{filtered_df['PM2.5'].max():.0f} µg/m³")

st.divider()

# --- VISUALISASI 1: Tren Bulanan (Area Chart) ---
st.subheader("1. Di bulan apa udara paling kotor?")
st.markdown("Polusi memburuk secara signifikan pada **musim dingin** (November - Februari).")

monthly_df = filtered_df.groupby('month')['PM2.5'].mean().reset_index()
nama_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']
monthly_df['month_name'] = nama_bulan

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(monthly_df['month_name'], monthly_df['PM2.5'], color='crimson', marker='o', linewidth=3)
ax1.fill_between(monthly_df['month_name'], monthly_df['PM2.5'], color='crimson', alpha=0.2)

rata_rata_tahunan = filtered_df['PM2.5'].mean()
ax1.axhline(rata_rata_tahunan, color='black', linestyle='--', linewidth=2, label=f'Rata-rata Tahunan ({rata_rata_tahunan:.1f})')

ax1.set_xlabel("Bulan", fontsize=12)
ax1.set_ylabel("Rata-rata PM2.5 (µg/m³)", fontsize=12)
ax1.legend()
st.pyplot(fig1)

# --- VISUALISASI 2: Pola Harian (Line Chart) ---
st.subheader("2. Jam berapa kita harus menghindari aktivitas di luar?")
st.markdown("Waktu terbaik untuk beraktivitas adalah **sore hari (14:00 - 16:00)**, sementara malam dan pagi hari menunjukkan tingkat polusi tertinggi.")

hourly_df = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=hourly_df, x='hour', y='PM2.5', color='darkred', linewidth=3, marker='o', ax=ax2)

ax2.axvspan(20, 23, color='red', alpha=0.1, label='Jam Polusi Tinggi')
ax2.axvspan(0, 8, color='red', alpha=0.1)

ax2.set_xlabel("Jam (00:00 - 23:00)", fontsize=12)
ax2.set_ylabel("Rata-rata PM2.5 (µg/m³)", fontsize=12)
ax2.set_xticks(range(0, 24))
ax2.legend()
st.pyplot(fig2)

# --- VISUALISASI 3: Pengaruh Angin (Bar Chart) ---
st.subheader("3. Apakah angin kencang membantu membersihkan udara?")
st.markdown("Ya. Semakin kencang angin berhembus, kabut polusi udara akan semakin cepat tersapu.")

def kategori_angin(x):
    if x < 1:
        return "1. Sangat Tenang (<1 m/s)"
    elif x <= 3:
        return "2. Sedang (1-3 m/s)"
    else:
        return "3. Kencang (>3 m/s)"

# Menggunakan filtered_df agar data mengikuti filter tahun di sidebar
filtered_df['Kategori Angin'] = filtered_df['WSPM'].apply(kategori_angin)
wind_df = filtered_df.groupby('Kategori Angin')['PM2.5'].mean().reset_index()

fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(data=wind_df, x='Kategori Angin', y='PM2.5', palette='crest', ax=ax3)
ax3.set_xlabel("Kondisi Hembusan Angin", fontsize=12)
ax3.set_ylabel("Rata-rata PM2.5 (µg/m³)", fontsize=12)
st.pyplot(fig3)
