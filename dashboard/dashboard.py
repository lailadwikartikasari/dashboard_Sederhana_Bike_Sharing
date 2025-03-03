import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Atur gaya Seaborn
sns.set(style="whitegrid", context="talk")

# Tentukan path absolut ke file CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "merged_data.csv")

def load_data():
    """Load dataset dengan pengecekan error."""
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
    st.sidebar.image("D:/STUPEN/BELAJAR ANALISIS DATA PYTHON/data/logo.jpeg", use_column_width=True)

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

    # ============================
    # Interaktif: Rentals by Season & Weather
    # ============================
    st.header("🚴‍♂️ Rentals by Season & Weather")

    if 'weathersit' in main_data_df.columns:
        weathersit_mapping = {1: "Clear", 2: "Mist", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
        main_data_df['weathersit_cat'] = main_data_df['weathersit'].map(weathersit_mapping)
        
        # Pilihan jenis agregasi (total atau rata-rata penyewaan)
        agg_option = st.radio("Pilih Metode Agregasi", ["Rata-rata", "Total"], horizontal=True)
        
        if agg_option == "Rata-rata":
            agg_df = main_data_df.groupby(['season_cat', 'weathersit_cat'])['cnt'].mean().reset_index()
            agg_df.rename(columns={'cnt': 'avg_rental'}, inplace=True)
            y_label = "Average Rental Count"
        else:
            agg_df = main_data_df.groupby(['season_cat', 'weathersit_cat'])['cnt'].sum().reset_index()
            agg_df.rename(columns={'cnt': 'total_rental'}, inplace=True)
            y_label = "Total Rental Count"

        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.barplot(data=agg_df, x='season_cat', y=agg_df.columns[-1], hue='weathersit_cat', palette="viridis", ax=ax1)
        ax1.set_xlabel("Season")
        ax1.set_ylabel(y_label)
        ax1.set_title(f"Bike Rentals by Season & Weather ({agg_option})")
        ax1.legend(title="Weather", bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig1)

    # ============================
    # Interaktif: Temperature, Humidity & Rental Count
    # ============================
    st.header("🌡️ Temperature, Humidity & Rental Count")

    if all(col in main_data_df.columns for col in ['temp', 'hum', 'cnt']):
        # Pilihan skala warna
        color_scale = st.selectbox("Pilih Skema Warna", ["coolwarm", "viridis", "magma"])
        
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=main_data_df, x='temp', y='cnt', hue='hum', palette=color_scale, s=80, ax=ax2)
        ax2.set_xlabel("Temperature")
        ax2.set_ylabel("Rental Count")
        ax2.set_title("Temperature vs. Rental Count (Colored by Humidity)")
        ax2.legend(title="Humidity", bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig2)

    # ============================
    # Additional Visualizations
    # ============================
    st.header("📊 Additional Visualizations")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Histogram of Rental Count**")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.histplot(main_data_df, x='cnt', bins=30, color="#2ca02c", ax=ax3)
        ax3.set_title("Histogram of Rental Count")
        ax3.set_xlabel("Rental Count")
        ax3.set_ylabel("Frequency")
        st.pyplot(fig3)
    
    with col2:
        st.markdown("**Boxplot of Rental Count**")
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=main_data_df, x='cnt', color="#d62728", ax=ax4)
        ax4.set_title("Boxplot of Rental Count")
        ax4.set_xlabel("Rental Count")
        st.pyplot(fig4)

    # ============================
    # Clustering: Rental Count Categories
    # ============================
    st.header("📌 Rental Count Categories (Clustering)")

    bins = [0, 100, 200, 300, 400, main_data_df['cnt'].max()]
    cluster_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    main_data_df['cnt_cluster'] = pd.cut(main_data_df['cnt'], bins=bins, labels=cluster_labels)
    
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    sns.countplot(data=main_data_df, x='cnt_cluster', order=cluster_labels, palette="mako", ax=ax5)
    ax5.set_xlabel("Rental Count Category")
    ax5.set_ylabel("Number of Days")
    ax5.set_title("Distribution of Rental Count Categories")
    st.pyplot(fig5)

    # Informasi tambahan
    st.markdown("""
    **📌 Keterangan:**  
    - **Very Low:** Penyewaan kurang dari 100  
    - **Low:** Penyewaan antara 100-200  
    - **Medium:** Penyewaan antara 200-300  
    - **High:** Penyewaan antara 300-400  
    - **Very High:** Penyewaan di atas 400  
    """)

if __name__ == "__main__":
    main()