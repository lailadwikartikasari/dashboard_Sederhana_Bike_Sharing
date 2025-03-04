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
    st.subheader("📆 Penyewaan Sepeda Berdasarkan Hari dalam Seminggu")

    # Pastikan kolom yang diperlukan tersedia
    if 'dteday_y_x' in filtered_df.columns and 'cnt_y_x' in filtered_df.columns:
        
        # Hitung total penyewaan sepeda per hari
        daily_df = filtered_df.groupby('dteday_y_x')['cnt_y_x'].sum().reset_index()
        
        # Tambahkan kolom nama hari
        daily_df['day_of_week'] = pd.to_datetime(daily_df['dteday_y_x']).dt.day_name()

        # Hitung rata-rata penyewaan per hari dalam seminggu
        daily_trend = daily_df.groupby('day_of_week')['cnt_y_x'].sum()

        # Urutkan sesuai dengan urutan hari dalam seminggu
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        daily_trend = daily_trend.reindex(days_order)

        # Plot tren peminjaman sepeda per hari dalam seminggu
        plt.figure(figsize=(8, 5))
        plt.plot(daily_trend.index, daily_trend.values, marker='o', linestyle='-', markersize=8, markerfacecolor='red', markeredgecolor='black')
        plt.xlabel('Hari')
        plt.ylabel('Jumlah Penyewaan')
        plt.title('Penyewaan Sepeda Berdasarkan Hari dalam Seminggu')
        plt.grid()

        # Tampilkan plot di Streamlit
        st.pyplot(plt)

    else:
        st.warning("Kolom 'dteday_y_x' atau 'cnt_y_x' tidak ditemukan dalam dataset yang digunakan.")

    # Visualisasi Tren Per Jam
    st.subheader("⏰ Penyewaan Sepeda Berdasarkan Jam dalam Sehari")

    # Pastikan kolom yang diperlukan tersedia
    if 'hr_x' in filtered_df.columns and 'cnt_y_x' in filtered_df.columns:
        
        # Hitung total penyewaan sepeda per jam
        hourly_df = filtered_df.groupby("hr_x")['cnt_y_x'].sum().reset_index()

        # Hitung Jumlah penyewaan sepeda untuk setiap jam
        hourly_trend = hourly_df.groupby('hr_x')['cnt_y_x'].sum()

        # Plot tren peminjaman sepeda per jam
        plt.figure(figsize=(8, 5))
        plt.plot(hourly_trend.index, hourly_trend.values, marker='o', linestyle='-', markersize=8, 
                markerfacecolor='red', markeredgecolor='black')

        # Label dan judul
        plt.xlabel('Jam')
        plt.ylabel('Jumlah Penyewaan')
        plt.title('Penyewaan Sepeda Berdasarkan Jam dalam Sehari')
        plt.xticks(range(0, 24))  # Pastikan sumbu X menampilkan semua jam
        plt.grid()

        # Tampilkan plot di Streamlit
        st.pyplot(plt)

    else:
        st.warning("Kolom 'hr_x' atau 'cnt_y_x' tidak ditemukan dalam dataset yang digunakan.")

    # Visualisasi pola musiman
    st.subheader("☁️ Apakah kondisi cuaca berpengaruh terhadap jumlah penyewaan sepeda?")

    # Mapping kondisi cuaca
    weathersit_mapping = {1: "Clear", 2: "Mist", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
    color_mapping = {"Clear": "green", "Mist": "orange", "Light Rain/Snow": "red", "Heavy Rain/Snow": "blue"}

    # Periksa apakah kolom yang diperlukan ada dalam DataFrame
    if 'weathersit_y_x' in filtered_df.columns and 'cnt_y_x' in filtered_df.columns:
        # Kelompokkan data berdasarkan kondisi cuaca dan hitung Jumlah peminjaman
        seasonal_trend = filtered_df.groupby("weathersit_y_x")['cnt_y_x'].sum().sort_values()
        
        # Ubah indeks ke nama kondisi cuaca yang lebih jelas
        seasonal_trend.index = seasonal_trend.index.map(weathersit_mapping)

        # Tentukan warna berdasarkan mapping
        colors = [color_mapping[label] for label in seasonal_trend.index]

        # Membuat plot
        fig, ax = plt.subplots(figsize=(8, 5))
        seasonal_trend.plot(kind='bar', color=colors, ax=ax)
        ax.set_xlabel("Kondisi Cuaca")  # Perbaikan label sumbu X
        ax.set_ylabel("Jumlah Peminjaman")
        ax.set_title("Pola Peminjaman Sepeda Berdasarkan Kondisi Cuaca")
        plt.xticks(rotation=45)
        plt.grid(axis='y')

        # Tampilkan plot di Streamlit
        st.pyplot(fig)

    else:
        st.warning("Kolom 'weathersit_y_x' atau 'cnt_y_x' tidak ditemukan untuk visualisasi pola peminjaman berdasarkan cuaca.")

if __name__ == "__main__":
    main()
