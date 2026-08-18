import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# CONFIG & LOAD DATA
# ==============================
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Pastikan file CSV tersedia di direktori yang sama
    df = pd.read_csv("dashboard/main_data.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# ==============================
# HEADER DASHBOARD
# ==============================
st.title("📊 Air Quality Dashboard - Stasiun Aotizhongxin")
st.markdown("Visualisasi ini menjawab 3 pertanyaan bisnis utama terkait tren dan faktor polusi udara.")
st.divider()

# ==============================
# TABS UNTUK PERTANYAAN BISNIS
# ==============================
tab1, tab2, tab3 = st.tabs([
    "📈 Q1: Tren Bulanan (2014-2016)", 
    "🌡️ Q2: Korelasi Musim Dingin", 
    "🚗 Q3: Polusi Jam Sibuk (2015)"
])

# ---------------------------------------------------
# PERTANYAAN 1: Tren Rata-rata PM2.5 Bulanan (2014-2016)
# ---------------------------------------------------
with tab1:
    st.subheader("Bagaimana tren rata-rata tingkat konsentrasi PM2.5 bulanan di stasiun Aotizhongxin sepanjang tahun 2014 hingga 2016, dan pada bulan apa polusi mencapai titik tertinggi?")
    
    # Filtering data 2014-2016
    q1_df = df[(df['year'] >= 2014) & (df['year'] <= 2016)]
    
    if not q1_df.empty:
        # Grouping berdasarkan bulan (1-12)
        monthly_pm25 = q1_df.groupby('month')['PM2.5'].mean().reset_index()
        
        # Mapping nama bulan untuk sumbu X
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']
        monthly_pm25['month_name'] = month_names
        
        rata_rata_tahunan = monthly_pm25['PM2.5'].mean()

        # Visualisasi mengikuti gaya Screenshot 1
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        
        # Garis utama dan marker
        ax1.plot(monthly_pm25['month_name'], monthly_pm25['PM2.5'], 
                 marker='o', color='#DC143C', linewidth=2.5) # Warna Crimson/Merah
        
        # Area fill di bawah garis
        ax1.fill_between(monthly_pm25['month_name'], monthly_pm25['PM2.5'], 
                         color='#DC143C', alpha=0.2)
        
        # Garis putus-putus untuk rata-rata
        ax1.axhline(rata_rata_tahunan, color='black', linestyle='--', 
                    linewidth=2, label=f'Rata-rata ({rata_rata_tahunan:.1f})')
        
        # Styling Grid & Label
        ax1.grid(axis='y', linestyle='-', alpha=0.5, color='#D3D3D3')
        ax1.grid(axis='x', alpha=0) # Hilangkan grid vertikal agar mirip gambar
        ax1.set_ylabel('Rata-rata PM2.5 (µg/m³)')
        ax1.set_xlabel('Bulan')
        ax1.legend(loc='upper center')
        
        st.pyplot(fig1)
        
        # Insight
        highest_month = monthly_pm25.loc[monthly_pm25['PM2.5'].idxmax()]
        st.info(f"**Insight:** Polusi mencapai titik tertinggi pada bulan **{highest_month['month_name']}** "
                f"dengan rata-rata **{highest_month['PM2.5']:.1f} µg/m³**.")
    else:
        st.warning("Data tidak tersedia.")

# ---------------------------------------------------
# PERTANYAAN 2: Korelasi WSPM, RAIN, PM10 (Musim Dingin)
# ---------------------------------------------------
with tab2:
    st.subheader("Bagaimana korelasi antara kecepatan angin (WSPM) dan curah hujan (RAIN) terhadap tingkat konsentrasi PM10 di stasiun Aotizhongxin selama musim dingin (Desember–Februari) pada periode 2013–2016?")
    
    # Filter musim dingin (Bulan 12, 1, 2) periode 2013-2016
    winter_df = df[(df['month'].isin([12, 1, 2])) & (df['year'] >= 2013) & (df['year'] <= 2016)]
    
    if not winter_df.empty:
        # Menghitung korelasi
        korelasi = winter_df[['WSPM', 'RAIN', 'PM10']].corr()
        
        # Visualisasi Heatmap (Paling ideal untuk korelasi)
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        sns.heatmap(korelasi, annot=True, cmap='coolwarm', fmt=".2f", 
                    vmin=-1, vmax=1, center=0, ax=ax2, 
                    linewidths=0.5, linecolor='white')
        
        plt.title('Heatmap Korelasi: WSPM, RAIN, dan PM10 (Musim Dingin)', pad=20)
        st.pyplot(fig2)
        
        # Insight
        corr_wspm = korelasi.loc['WSPM', 'PM10']
        st.info(f"**Insight:** Korelasi kecepatan angin (WSPM) terhadap PM10 adalah **{corr_wspm:.2f}**. "
                "Nilai negatif menunjukkan bahwa semakin kencang angin, konsentrasi PM10 cenderung menurun (angin membantu menyapu polusi).")
    else:
        st.warning("Data musim dingin tidak tersedia.")

# ---------------------------------------------------
# PERTANYAAN 3: PM2.5 Jam Sibuk vs Non-Sibuk (2015)
# ---------------------------------------------------
with tab3:
    st.subheader("Bagaimana perbedaan rata-rata konsentrasi PM2.5 pada jam sibuk lalu lintas (07:00–09:00 dan 17:00–19:00) dibandingkan dengan jam non-sibuk di stasiun Aotizhongxin sepanjang tahun 2015?")
    
    # Filter data tahun 2015
    q3_df = df[df['year'] == 2015]
    
    if not q3_df.empty:
        # Grouping berdasarkan jam (0-23)
        hourly_avg = q3_df.groupby('hour')['PM2.5'].mean().reset_index()
        
        # Visualisasi mengikuti gaya Screenshot 2
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        
        # Garis utama (Merah Gelap / Maroon)
        ax3.plot(hourly_avg['hour'], hourly_avg['PM2.5'], 
                 marker='o', color='#800000', linewidth=2.5)
        
        # Highlight Area untuk Jam Sibuk Lalu Lintas (07:00-09:00 dan 17:00-19:00)
        ax3.axvspan(7, 9, color='#FFC0CB', alpha=0.4, label='Jam Sibuk (Pagi: 07-09)')
        ax3.axvspan(17, 19, color='#FFC0CB', alpha=0.4, label='Jam Sibuk (Sore: 17-19)')
        
        # Styling Axis & Grid
        ax3.set_xticks(range(0, 24))
        ax3.set_xlabel('Jam (00:00 - 23:00)')
        ax3.set_ylabel('Rata-rata PM2.5 (µg/m³)')
        
        ax3.grid(axis='y', linestyle='-', alpha=0.5, color='#D3D3D3')
        ax3.grid(axis='x', alpha=0)
        ax3.legend(loc='lower center')
        
        st.pyplot(fig3)
        
        # Insight Perhitungan
        jam_sibuk_df = q3_df[q3_df['hour'].isin([7,8,9,17,18,19])]
        jam_nonsibuk_df = q3_df[~q3_df['hour'].isin([7,8,9,17,18,19])]
        
        avg_sibuk = jam_sibuk_df['PM2.5'].mean()
        avg_nonsibuk = jam_nonsibuk_df['PM2.5'].mean()
        
        st.info(f"**Insight:** Rata-rata PM2.5 pada Jam Sibuk adalah **{avg_sibuk:.1f} µg/m³**, "
                f"sedangkan pada Jam Non-Sibuk adalah **{avg_nonsibuk:.1f} µg/m³**.")
    else:
        st.warning("Data tahun 2015 tidak tersedia.")
