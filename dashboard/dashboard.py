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
logo_path = os.path.join(BASE_DIR, "D:/STUPEN/dashboard_Bike_Sharing/data/logo.jpeg")

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
    st.sidebar.header("📊 Dashboard Controls")
    
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
    st.header("🚴‍♂️ Rentals by Season & Weather")
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

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=agg_df, x='season_cat', y='cnt', hue='weathersit_cat', palette="viridis", ax=ax)
        ax.set_xlabel("Season")
        ax.set_ylabel(y_label)
        ax.set_title(f"Bike Rentals by Season & Weather ({agg_option})")
        ax.legend(title="Weather", bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig)
    
    st.header("🌡️ Temperature, Humidity & Rental Count")
    if all(col in main_data_df.columns for col in ['temp', 'hum', 'cnt']):
        color_scale = st.selectbox("Pilih Skema Warna", ["coolwarm", "viridis", "magma"])
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=main_data_df, x='temp', y='cnt', hue='hum', palette=color_scale, s=80, ax=ax)
        ax.set_xlabel("Temperature")
        ax.set_ylabel("Rental Count")
        ax.set_title("Temperature vs. Rental Count (Colored by Humidity)")
        ax.legend(title="Humidity", bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig)
    
    # Histogram & Boxplot
    st.header("📊 Additional Visualizations")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(main_data_df, x='cnt', bins=30, color="#2ca02c", ax=ax)
        ax.set_title("Histogram of Rental Count")
        ax.set_xlabel("Rental Count")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=main_data_df, x='cnt', color="#d62728", ax=ax)
        ax.set_title("Boxplot of Rental Count")
        ax.set_xlabel("Rental Count")
        st.pyplot(fig)
    
    # Clustering kategori rental
    st.header("📌 Rental Count Categories (Clustering)")
    bins = [0, 100, 200, 300, 400, main_data_df['cnt'].max()]
    cluster_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    main_data_df['cnt_cluster'] = pd.cut(main_data_df['cnt'], bins=bins, labels=cluster_labels)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.countplot(data=main_data_df, x='cnt_cluster', order=cluster_labels, palette="mako", ax=ax)
    ax.set_xlabel("Rental Count Category")
    ax.set_ylabel("Number of Days")
    ax.set_title("Distribution of Rental Count Categories")
    st.pyplot(fig)

if __name__ == "__main__":
    main()
