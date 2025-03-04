import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur gaya Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Tentukan path absolut ke file CSV dan gambar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "Bike_Sharing.csv")

@st.cache_data
def load_data():
    """Load dataset dengan pengecekan error."""
    if not os.path.exists(data_path):
        st.error(f"File data tidak ditemukan: {data_path}")
        return None
    try:
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.title("🚴‍♂️ Bike Sharing Dashboard")

    # Load data
    merged_data_df = load_data()
    if merged_data_df is None or merged_data_df.empty:
        st.warning("Data tidak tersedia atau kosong.")
        return

    # Sidebar untuk filter interaktif
    st.sidebar.header("Navigasi")

    # Konversi dteday ke datetime
    if 'dteday_y_x' in merged_data_df.columns:
        merged_data_df['dteday_y_x'] = pd.to_datetime(merged_data_df['dteday_y_x'], errors='coerce')
        merged_data_df.dropna(subset=['dteday_y_x'], inplace=True)
    else:
        st.error("Kolom 'dteday_y_x' tidak ditemukan dalam dataset.")
        return

    # Pilihan rentang tanggal
    min_date = merged_data_df['dteday_y_x'].min().date()
    max_date = merged_data_df['dteday_y_x'].max().date()
    start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        return

    # Filter data berdasarkan rentang tanggal
    filtered_df = merged_data_df[(merged_data_df['dteday_y_x'] >= pd.to_datetime(start_date)) & 
                                 (merged_data_df['dteday_y_x'] <= pd.to_datetime(end_date))]
    
    if filtered_df.empty:
        st.warning("Tidak ada data setelah diterapkan filter. Silakan ubah filter Anda.")
        return

    # Tampilkan preview data
    st.subheader("📜 Data Preview")
    st.write(filtered_df.head())

    # Visualisasi Tren Harian
    st.subheader("📆 Tren Peminjaman Sepeda Harian")
    if 'dteday_y_x' in filtered_df.columns and 'cnt_y_x' in filtered_df.columns:
        daily_df = filtered_df.groupby('dteday_y_x')['cnt_y_x'].sum().reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(daily_df['dteday_y_x'], daily_df['cnt_y_x'], marker='o', linestyle='-', color='b', label="Total Peminjaman")
        ax.set_xlabel("Tanggal")
        ax.set_ylabel("Total Peminjaman")
        ax.set_title("Tren Peminjaman Sepeda Harian")
        ax.legend()
        plt.xticks(rotation=45)
        plt.grid()
        st.pyplot(fig)
    else:
        st.warning("Kolom 'dteday' atau 'cnt' tidak ditemukan untuk visualisasi tren harian.")

    # Visualisasi Tren Per Jam
    st.subheader("⏰ Tren Peminjaman Sepeda Per Jam")
    if 'hr_x' in filtered_df.columns and 'cnt_y_x' in filtered_df.columns:
        hourly_df = filtered_df.groupby("hr_x")['cnt_y_x'].sum().reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=hourly_df, x='hr_x', y='cnt_y_x', palette="viridis", ax=ax)
        ax.set_xlabel("Jam")
        ax.set_ylabel("Total Peminjaman")
        ax.set_title("Tren Peminjaman Sepeda Per Jam")
        
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=10, color='black', weight='bold')

        plt.xticks(hourly_df['hr_x'].unique())
        plt.grid()
        st.pyplot(fig)
    else:
        st.warning("Kolom 'hr_x' atau 'cnt' tidak ditemukan untuk visualisasi tren per jam.")

    # Visualisasi pola musiman
    st.subheader("☁️ Apakah ada pola musiman dalam peminjaman sepeda?")

    # Mapping kondisi cuaca
    weathersit_mapping = {1: "Clear", 2: "Mist", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}

    # Periksa apakah kolom yang diperlukan ada dalam DataFrame
    if 'weathersit_y_x' in filtered_df.columns and 'cnt_y_x' in filtered_df.columns:
        # Kelompokkan data berdasarkan kondisi cuaca dan hitung rata-rata peminjaman
        seasonal_trend = filtered_df.groupby("weathersit_y_x")['cnt_y_x'].mean().sort_values()
        
        # Ubah indeks ke nama kondisi cuaca yang lebih jelas
        seasonal_trend.index = seasonal_trend.index.map(weathersit_mapping)

        # Membuat plot
        fig, ax = plt.subplots(figsize=(8, 5))
        seasonal_trend.plot(kind='bar', color=['green', 'orange', 'brown', 'blue'], ax=ax)
        ax.set_xlabel("Kondisi Cuaca")  # Perbaikan label sumbu X
        ax.set_ylabel("Rata-rata Peminjaman")
        ax.set_title("Pola Peminjaman Sepeda Berdasarkan Kondisi Cuaca")
        plt.xticks(rotation=45)
        plt.grid(axis='y')

        # Tampilkan plot di Streamlit
        st.pyplot(fig)

    else:
        st.warning("Kolom 'weathersit_y_x' atau 'cnt_y_x' tidak ditemukan untuk visualisasi pola peminjaman berdasarkan cuaca.")

if __name__ == "__main__":
    main()
