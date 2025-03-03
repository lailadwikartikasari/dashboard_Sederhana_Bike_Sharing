import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur gaya Seaborn
sns.set_theme(style="whitegrid", context="talk")

# Tentukan path absolut ke file CSV dan gambar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "merged_data.csv")
logo_path = os.path.join(BASE_DIR, "data", "logo.jpg")  # Sesuaikan path jika perlu

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
    
    # Coba tampilkan logo jika ada
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
    else:
        st.sidebar.warning("Logo tidak ditemukan!")
    
    # Pilihan rentang tanggal
    if 'dteday' in merged_data_df.columns:
        merged_data_df['dteday'] = pd.to_datetime(merged_data_df['dteday'], errors='coerce')
        merged_data_df = merged_data_df.dropna(subset=['dteday'])
        
        min_date = merged_data_df['dteday'].min()
        max_date = merged_data_df['dteday'].max()
        start_date, end_date = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])
        
        if start_date > end_date:
            st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
            return
        
        # Filter data berdasarkan tanggal
        merged_data_df = merged_data_df[(merged_data_df['dteday'] >= pd.Timestamp(start_date)) & 
                                    (merged_data_df['dteday'] <= pd.Timestamp(end_date))]
    
    # Pilihan musim (Season)
    season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    if 'season' in merged_data_df.columns:
        merged_data_df['season_cat'] = merged_data_df['season'].map(season_mapping)
        selected_season = st.sidebar.multiselect("Filter Musim", merged_data_df['season_cat'].unique(), default=merged_data_df['season_cat'].unique())
        merged_data_df = merged_data_df[merged_data_df['season_cat'].isin(selected_season)]
    
    # Validasi jika dataset kosong setelah filter
    if merged_data_df.empty:
        st.warning("Tidak ada data setelah diterapkan filter. Silakan ubah filter Anda.")
        return
    
    # Tampilkan preview data
    st.subheader("📜 Data Preview")
    st.write(merged_data_df.head())
    
    # Pilihan agregasi
    agg_option = st.radio("Pilih Metode Agregasi", ["Rata-rata", "Total"], horizontal=True)
    
    # Visualisasi Tren Harian
    st.subheader("📆 Tren Peminjaman Sepeda Harian")
    if 'dteday' in merged_data_df.columns and 'cnt' in merged_data_df.columns:
        daily_df = merged_data_df.groupby('dteday')['cnt'].mean().reset_index() if agg_option == "Rata-rata" else merged_data_df.groupby('dteday')['cnt'].sum().reset_index()
        y_label = "Rata-rata Peminjaman" if agg_option == "Rata-rata" else "Total Peminjaman"
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(daily_df['dteday'], daily_df['cnt'], marker='o', linestyle='-', color='b', label=y_label)
        ax.set_xlabel("Tanggal")
        ax.set_ylabel(y_label)
        ax.set_title(f"Tren Peminjaman Sepeda Harian ({agg_option})")
        ax.legend()
        plt.xticks(rotation=45)
        plt.grid()
        st.pyplot(fig)
    
    # Visualisasi Tren Per Jam
    st.subheader("⏰ Tren Peminjaman Sepeda Per Jam")
    if 'hr' in merged_data_df.columns and 'cnt' in merged_data_df.columns:
        hourly_df = merged_data_df.groupby("hr")['cnt'].mean().reset_index() if agg_option == "Rata-rata" else merged_data_df.groupby("hr")['cnt'].sum().reset_index()
        y_label = "Rata-rata Peminjaman" if agg_option == "Rata-rata" else "Total Peminjaman"
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=hourly_df, x='hr', y='cnt', palette="viridis", ax=ax)
        ax.set_xlabel("Jam")
        ax.set_ylabel(y_label)
        ax.set_title(f"Tren Peminjaman Sepeda Per Jam ({agg_option})")
        
        # Tambahkan label nilai pada setiap batang
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=10, color='black', weight='bold')
        
        plt.xticks(hourly_df['hr'].unique())
        plt.grid()
        st.pyplot(fig)
    
    # Visualisasi pola musiman
    st.subheader("☁️ Apakah ada pola musiman dalam peminjaman sepeda?")
    if 'season_cat' in merged_data_df.columns and 'cnt' in merged_data_df.columns:
        seasonal_trend = merged_data_df.groupby("season_cat")['cnt'].mean().sort_values()
        fig, ax = plt.subplots(figsize=(8, 5))
        seasonal_trend.plot(kind='bar', color=['green', 'orange', 'brown', 'blue'], ax=ax)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Rata-rata Peminjaman")
        ax.set_title("Pola Peminjaman Sepeda Berdasarkan Musim")
        plt.xticks(rotation=45)
        plt.grid(axis='y')
        st.pyplot(fig)

if __name__ == "__main__":
    main()