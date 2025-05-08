import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime
from services.product_db import urun_ekle

class BulkProductLoaderFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="📥 Excel'den Ürün Yükle", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self, text="Excel Dosyası Seç", command=self.dosya_sec).pack(pady=20)

    def dosya_sec(self):
        dosya_yolu = filedialog.askopenfilename(
            title="Excel Dosyası Seçin",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        if not dosya_yolu:
            return

        try:
            df = pd.read_excel(dosya_yolu, dtype={"Barcode": str})
            df.columns = df.columns.str.strip()  # Başlıklarda boşluk varsa temizle

            gerekli_sutunlar = {"Barcode", "Product_Name", "URL"}
            if not gerekli_sutunlar.issubset(df.columns):
                messagebox.showerror("Hata", "Excel dosyasında 'Barcode', 'Product_Name', 'URL' sütunları eksik.")
                return

            eklenen = 0
            for _, row in df.iterrows():
                barcode = row["Barcode"]
                name = row["Product_Name"]
                url = row["URL"]
                date = datetime.now().strftime("%Y-%m-%d")

                if urun_ekle(barcode, name, url, date):
                    eklenen += 1

            messagebox.showinfo("Başarılı", f"✅ {eklenen} ürün başarıyla eklendi/güncellendi.")
        except Exception as e:
            messagebox.showerror("Yükleme Hatası", f"❌ Dosya yüklenemedi:\n{e}")