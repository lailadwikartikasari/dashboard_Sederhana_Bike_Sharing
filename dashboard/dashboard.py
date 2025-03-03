import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur gaya Seaborn
sns.set(style="whitegrid", context="talk")

# Tentukan path absolut ke file CSV dan gambar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "merged_data.csv")
logo_path = os.path.join(BASE_DIR, 'D:/STUPEN/dashboard_Bike_Sharing/data/logo.jpg')

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
    main_data_df = load_data()
    if main_data_df is None:
        return

    # Sidebar untuk filter interaktif
    st.sidebar.header("Navigasi")
    
    # Coba tampilkan logo jika ada
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
    else:
        st.sidebar.warning("Logo tidak ditemukan!")
    
    # Pilihan rentang tanggal
    if 'dteday' in main_data_df.columns:
        main_data_df['dteday'] = pd.to_datetime(main_data_df['dteday'])
        min_date = main_data_df['dteday'].min()
        max_date = main_data_df['dteday'].max()
        start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])
        
        # Filter data berdasarkan tanggal
        main_data_df = main_data_df[(main_data_df['dteday'] >= pd.Timestamp(start_date)) & 
                                    (main_data_df['dteday'] <= pd.Timestamp(end_date))]

    # Pilihan musim (Season)
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    if 'season' in main_data_df.columns:
        main_data_df['season_cat'] = main_data_df['season'].map(season_mapping)
        selected_season = st.sidebar.multiselect("Filter Musim", main_data_df['season_cat'].unique(), default=main_data_df['season_cat'].unique())
        main_data_df = main_data_df[main_data_df['season_cat'].isin(selected_season)]
    
    # Tampilkan preview data
    st.subheader("📜 Data Preview")
    st.write(main_data_df.head())

    # Visualisasi dan Analisis
    st.header("🚴‍♂️ Bagaimana tren peminjaman sepeda secara harian dan per jam?")

    if 'weathersit' in main_data_df.columns:
        weathersit_mapping = {1: "Clear", 2: "Mist", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
        main_data_df['weathersit_cat'] = main_data_df['weathersit'].map(weathersit_mapping)

        # Pilihan jenis agregasi
        agg_option = st.radio("Pilih Metode Agregasi", ["Rata-rata", "Total"], horizontal=True)

        if agg_option == "Rata-rata":
            agg_df = main_data_df.groupby(['season_cat', 'weathersit_cat'])['cnt'].mean().reset_index()
            y_label = "Average Rental Count"
        else:
            agg_df = main_data_df.groupby(['season_cat', 'weathersit_cat'])['cnt'].sum().reset_index()
            y_label = "Total Rental Count"

        # Pilihan visualisasi
        show_daily = st.checkbox("Tampilkan Tren Harian", value=True)
        show_hourly = st.checkbox("Tampilkan Tren Per Jam", value=True)

        # Visualisasi Tren Harian
        if show_daily and 'dteday' in main_data_df.columns and 'cnt' in main_data_df.columns:
            day_df = main_data_df.groupby('dteday')['cnt'].sum().reset_index()

            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(day_df['dteday'], day_df['cnt'], marker='o', linestyle='-', color='b')
            ax.set_xlabel("Tanggal")
            ax.set_ylabel("Jumlah Peminjaman")
            ax.set_title("Tren Peminjaman Sepeda Harian")
            plt.xticks(rotation=45)
            plt.grid()
            st.pyplot(fig)

        # Visualisasi Tren Per Jam
        if show_hourly and 'hr' in main_data_df.columns and 'cnt' in main_data_df.columns:
            hour_df = main_data_df.groupby("hr")["cnt"].mean().reset_index()

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(hour_df["hr"], hour_df["cnt"], marker='o', linestyle='-', color='r')
            ax.set_xlabel("Jam")
            ax.set_ylabel("Rata-rata Peminjaman")
            ax.set_title("Tren Peminjaman Sepeda Per Jam")
            plt.xticks(range(0, 24))
            plt.grid()
            st.pyplot(fig)

    st.header("☁️ Apakah ada pola musiman dalam peminjaman sepeda?")

    if 'season' in main_data_df.columns and 'cnt' in main_data_df.columns:
        # Buat data untuk visualisasi musiman
        seasonal_trend = main_data_df.groupby("season_cat")["cnt"].mean().sort_values()

        # Visualisasi pola peminjaman berdasarkan musim
        fig, ax = plt.subplots(figsize=(8, 5))
        seasonal_trend.plot(kind='bar', color=['green', 'orange', 'brown', 'blue'], ax=ax)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Rata-rata Peminjaman")
        ax.set_title("Pola Peminjaman Sepeda Berdasarkan Musim")
        plt.xticks(rotation=45)
        plt.grid(axis='y')

        # Tampilkan di Streamlit
        st.pyplot(fig)

if __name__ == "__main__":
    main()
