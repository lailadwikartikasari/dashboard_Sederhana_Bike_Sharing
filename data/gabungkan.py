import pandas as pd

# Membaca dataset pertama (day_csv)
data1 = pd.read_csv("day_csv.csv")  # Pastikan nama file sesuai

# Membaca dataset kedua (hour_csv)
data2 = pd.read_csv("hour_csv.csv")  # Pastikan nama file sesuai

# Menggabungkan dataset secara vertikal
gabung_vertikal = pd.concat([data1, data2], ignore_index=True)

# Menyimpan hasil ke dalam file CSV
gabung_vertikal.to_csv("gabungan_dataset.csv", index=False)  # Simpan tanpa index

print("Dataset berhasil digabungkan dan disimpan sebagai 'gabungan_dataset.csv'")
