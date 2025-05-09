import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pandas as pd
from datetime import datetime
from services.product_db import urun_ekle_veya_guncelle, veritabani_olustur

class ProductUploadFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="📦 Ürün Yükleme Paneli", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self, text="📄 Excel'den Ürünleri Yükle", command=self.excelden_yukle).pack(pady=10)
        tk.Button(self, text="📝 Elle Ürün Ekle", command=self.elle_urun_ekle).pack(pady=10)

    def excelden_yukle(self):
        veritabani_olustur()
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel Dosyaları", "*.xlsx")])

        if not dosya_yolu:
            return

        try:
            df = pd.read_excel(dosya_yolu, dtype=str)
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]  # Normalize kolon isimleri
        except Exception as e:
            messagebox.showerror("Hata", f"Excel dosyası okunamadı:\n{e}")
            return

        beklenen_sutunlar = {"barcode", "product_name", "url"}
        if not beklenen_sutunlar.issubset(set(df.columns)):
            messagebox.showerror("Hata", "Excel dosyası uygun formatta değil. 'barcode', 'product_name' ve 'url' kolonları zorunludur.")
            return

        # Eksik 'last_control' kolonunu ekle ve bugünün tarihi ile doldur
        if "last_control" not in df.columns:
            df["last_control"] = datetime.now().strftime("%Y-%m-%d")

        sayac = 0
        for _, row in df.iterrows():
            urun_ekle_veya_guncelle(
                barcode=row["barcode"],
                name=row["product_name"],  # Doğru parametre ismi: name
                url=row["url"],
                kontrol_tarihi=row["last_control"]  # Doğru parametre ismi: kontrol_tarihi
            )
       
            sayac += 1

        messagebox.showinfo("Başarılı", f"✅ {sayac} ürün başarıyla yüklendi veya güncellendi.")

    def elle_urun_ekle(self):
        barcode = simpledialog.askstring("Barkod", "Barkodu girin:")
        if not barcode:
            return
        product_name = simpledialog.askstring("Ürün Adı", "Ürün adını girin:")
        url = simpledialog.askstring("URL", "Ürün URL'sini girin:")
        last_control = simpledialog.askstring("Tarih", "Son kontrol tarihi (örnek: 2025-05-08):")

        if not (product_name or url or last_control):
            messagebox.showwarning("Eksik Veri", "En az bir alan doldurulmalıdır.")
            return

        urun_ekle_veya_guncelle(
            barcode=barcode,
            product_name=product_name,
            url=url,
            last_control=last_control
        )
        messagebox.showinfo("Başarılı", f"✅ '{barcode}' barkodlu ürün eklendi veya güncellendi.")