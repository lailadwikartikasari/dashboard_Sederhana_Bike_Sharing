import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("D:/STUPEN/dashboard_Bike_Sharing/dashboard/Bike_Sharing.csv")

# Membersihkan dataset: Menghapus kolom yang duplikat jika ada
df = df.loc[:, ~df.columns.duplicated()]

# Sidebar untuk logo atau informasi tambahan
st.sidebar.image("D:/STUPEN/BELAJAR ANALISIS DATA PYTHON/data/logo.jpeg", use_column_width=True)
st.sidebar.markdown("## Navigasi")
st.sidebar.markdown("Gunakan fitur ini untuk menavigasi aplikasi.")

# Pilihan tanggal
selected_date = st.sidebar.date_input("Pilih Tanggal")
if 'date' in df.columns:
    df_filtered = df[df['date'] == str(selected_date)]
else:
    df_filtered = df.copy()

# Judul Aplikasi
st.title("Analisis Penyewaan Sepeda")

# Tampilkan dataset
if st.checkbox("Tampilkan DataFrame"):
    st.write(df_filtered.head())

# 1. Pengaruh Cuaca terhadap Penyewaan Sepeda
st.subheader("Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda")
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x='weathersit_x_y', y='cnt_x_y', data=df_filtered, hue='weathersit_x_y', palette='coolwarm', ax=ax)
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Jumlah Penyewaan Sepeda")
st.pyplot(fig)

# 2. Pengaruh Suhu, Kelembaban, dan Kecepatan Angin terhadap Penyewaan Sepeda
st.subheader("Pengaruh Faktor Cuaca terhadap Penyewaan Sepeda")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

sns.scatterplot(ax=axes[0], x='temp_x_y', y='cnt_x_y', data=df_filtered, color='red', alpha=0.5)
axes[0].set_title("Hubungan Suhu dengan Penyewaan Sepeda")
axes[0].set_xlabel("Suhu")
axes[0].set_ylabel("Jumlah Penyewaan Sepeda")

sns.scatterplot(ax=axes[1], x='hum_x_y', y='cnt_x_y', data=df_filtered, color='blue', alpha=0.5)
axes[1].set_title("Hubungan Kelembaban dengan Penyewaan Sepeda")
axes[1].set_xlabel("Kelembaban")
axes[1].set_ylabel("Jumlah Penyewaan Sepeda")

sns.scatterplot(ax=axes[2], x='windspeed_x_y', y='cnt_x_y', data=df_filtered, color='green', alpha=0.5)
axes[2].set_title("Hubungan Kecepatan Angin dengan Penyewaan Sepeda")
axes[2].set_xlabel("Kecepatan Angin")
axes[2].set_ylabel("Jumlah Penyewaan Sepeda")

st.pyplot(fig)

# 3. Total Penyewaan Sepeda per Musim
st.subheader("Total Penyewaan Sepeda per Musim")
season_rental_counts = df_filtered.groupby('season_x_y')['cnt_x_y'].sum()

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=season_rental_counts.index, y=season_rental_counts.values, palette='viridis', ax=ax)
ax.set_title('Total Bike Rentals per Season')
ax.set_xlabel('Musim')
ax.set_ylabel('Total Penyewaan')
ax.set_xticklabels(['Spring', 'Summer', 'Fall', 'Winter'])  # Asumsi nilai musim
st.pyplot(fig)
