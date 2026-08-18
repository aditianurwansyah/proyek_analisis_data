import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema visualisasi
sns.set_theme(style="whitegrid")

# --- JUDUL DASHBOARD ---
st.title("☁️ Kualitas Udara Aotizhongxin")
st.markdown("**Dashboard Analisis Polusi Udara dan Faktor Pendukungnya**")
st.markdown("Dashboard ini dilengkapi dengan filter interaktif ganda dan insight otomatis untuk setiap pertanyaan analisis.")

# --- MEMUAT DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    return df

df = load_data()

# ==========================================
# --- FITUR INTERAKTIF (SIDEBAR) ---
# ==========================================
st.sidebar.header("🔍 Kontrol & Filter Data")

# Fitur Interaktif Pertama: Multiselect Tahun
tahun_tersedia = sorted(df['year'].unique())
tahun_pilihan = st.sidebar.multiselect(
    "Pilih Tahun yang Ingin Ditampilkan:",
    options=tahun_tersedia,
    default=tahun_tersedia
)

# Fitur Interaktif Kedua: Slider Rentang Bulan (Manipulasi Data Langsung)
rentang_bulan = st.sidebar.slider(
    "Pilih Rentang Bulan:",
    min_value=1,
    max_value=12,
    value=(1, 12),
    help="Geser slider untuk memfilter data berdasarkan bulan tertentu."
)

# --- PENERAPAN FILTER KE DATASET ---
if not tahun_pilihan:
    filtered_df = df.copy()
else:
    filtered_df = df[df['year'].isin(tahun_pilihan)].copy()

# Filter berdasarkan slider bulan
filtered_df = filtered_df[
    (filtered_df['month'] >= rentang_bulan[0]) & 
    (filtered_df['month'] <= rentang_bulan[1])
]

# --- RINGKASAN METRIK ---
st.markdown("### 📊 Ringkasan Data Utama (Berdasarkan Filter)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Rata-rata PM2.5", value=f"{filtered_df['PM2.5'].mean():.1f} µg/m³")
with col2:
    st.metric(label="Rata-rata PM10", value=f"{filtered_df['PM10'].mean():.1f} µg/m³")
with col3:
    st.metric(label="Suhu Rata-rata", value=f"{filtered_df['TEMP'].mean():.1f} °C")

st.divider()

# ==========================================
# --- VISUALISASI 1: Tren Bulanan  ---
# ==========================================
st.subheader("1. Bagaimana tren rata-rata tingkat konsentrasi PM2.5 bulanan di stasiun Aotizhongxin sepanjang tahun 2014 hingga 2016, dan pada bulan apa polusi mencapai titik tertinggi?")
st.markdown("Grafik ini menunjukkan fluktuasi rata-rata polusi PM2.5 setiap bulannya sesuai rentang bulan yang dipilih.")

monthly_df = filtered_df.groupby('month')['PM2.5'].mean().reset_index()

if not monthly_df.empty:
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=monthly_df, x='month', y='PM2.5', marker='o', color='red', linewidth=2, ax=ax1)
    ax1.set_xlabel("Bulan", fontsize=11)
    ax1.set_ylabel("Rata-rata PM2.5 (µg/m³)", fontsize=11)
    ax1.set_xticks(range(1, 13))
    ax1.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig1)

    # Insight Otomatis Pertanyaan 1
    max_row = monthly_df.loc[monthly_df['PM2.5'].idxmax()]
    kamus_nama_bulan = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    nama_bulan_max = kamus_nama_bulan.get(int(max_row['month']), str(int(max_row['month'])))
    st.info(f"**Insight:** Berdasarkan data yang aktif, tingkat polusi PM2.5 tertinggi mencapai titik puncaknya pada bulan **{nama_bulan_max}** dengan rata-rata konsentrasi sebesar **{max_row['PM2.5']:.1f} µg/m³**.")
else:
    st.warning("Tidak ada data yang tersedia untuk rentang bulan/tahun yang dipilih.")

st.divider()

# ==========================================
# --- VISUALISASI 2: Heatmap Korelasi WSPM, RAIN, dan PM10 ---
# ==========================================
st.subheader("2. Bagaimana korelasi antara kecepatan angin (WSPM) dan curah hujan (RAIN) terhadap tingkat konsentrasi PM10 di stasiun Aotizhongxin selama musim dingin (Desember–Februari) pada periode 2013–2016?")
st.markdown("Visualisasi matriks korelasi menggunakan *heatmap* untuk melihat hubungan antarvariabel cuaca dan polutan.")

winter_df = filtered_df[(filtered_df['month'].isin([12, 1, 2])) & (filtered_df['year'] >= 2013) & (filtered_df['year'] <= 2016)]

if not winter_df.empty:
    korelasi = winter_df[['WSPM', 'RAIN', 'PM10']].corr()
    
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    sns.heatmap(korelasi, annot=True, cmap='coolwarm', fmt=".2f", 
                vmin=-1, vmax=1, center=0, ax=ax2, 
                linewidths=0.5, linecolor='white')
    
    ax2.set_title('Heatmap Korelasi: WSPM, RAIN, dan PM10 (Musim Dingin)', pad=20)
    st.pyplot(fig2)
    
    corr_wspm = korelasi.loc['WSPM', 'PM10']
    st.info(f"**Insight:** Korelasi kecepatan angin (WSPM) terhadap PM10 adalah **{corr_wspm:.2f}**. "
            "Nilai negatif menunjukkan bahwa semakin kencang angin, konsentrasi PM10 cenderung menurun.")
else:
    st.warning("Data musim dingin untuk periode 2013–2016 tidak ditemukan pada filter yang aktif saat ini.")

st.divider()

# ==========================================
# --- VISUALISASI 3: Jam Sibuk vs Non-Sibuk 2015 ---
# ==========================================
st.subheader("3. Bagaimana perbedaan rata-rata konsentrasi PM2.5 pada jam sibuk lalu lintas (07:00–09:00 dan 17:00–19:00) dibandingkan dengan jam non-sibuk di stasiun Aotizhongxin sepanjang tahun 2015?")
st.markdown("Diagram batang ini membandingkan tingkat polusi antara jam sibuk lalu lintas dengan jam non-sibuk khusus pada tahun 2015.")

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

    # Insight Otomatis Pertanyaan 3
    val_sibuk = df_2015_vis[df_2015_vis['kategori_waktu'].str.contains('Jam Sibuk')]['PM2.5'].mean()
    val_nonsibuk = df_2015_vis[df_2015_vis['kategori_waktu'] == 'Bukan Jam Sibuk']['PM2.5'].mean()
    st.info(f"**Insight:** Pada tahun 2015, rata-rata konsentrasi PM2.5 saat **Jam Sibuk** tercatat sebesar **{val_sibuk:.1f} µg/m³**, sedangkan pada waktu **Non-Sibuk** adalah **{val_nonsibuk:.1f} µg/m³**.")
else:
    st.warning("Data untuk tahun 2015 tidak masuk dalam filter tahun atau rentang bulan yang sedang dipilih.")
