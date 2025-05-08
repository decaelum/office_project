import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pandas as pd
from services.product_db import urun_ekle_veya_guncelle

class ProductUploadFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="📦 Ürün Yükleme Paneli", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self, text="📄 Excel'den Ürünleri Yükle", command=self.excelden_yukle).pack(pady=10)
        tk.Button(self, text="📝 Elle Ürün Ekle", command=self.elle_urun_ekle).pack(pady=10)

    def excelden_yukle(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel Dosyaları", "*.xlsx")])
        if not dosya_yolu:
            return

        try:
            df = pd.read_excel(dosya_yolu, dtype=str)
        except Exception as e:
            messagebox.showerror("Hata", f"Excel dosyası okunamadı:\n{e}")
            return

        beklenen_sutunlar = {"barcode", "product_name", "url", "last_control"}
        if not beklenen_sutunlar.issubset(set(map(str.lower, df.columns))):
            messagebox.showerror("Hata", "Excel dosyası uygun formatta değil.")
            return

        sayac = 0
        for _, row in df.iterrows():
            # 🔄 Tarih boşsa bugünün tarihi atanır
            last_control = row.get("last_control") or datetime.now().strftime("%Y-%m-%d")

            urun_ekle_veya_guncelle(
                barcode=row["barcode"],
                product_name=row["product_name"],
                url=row["url"],
                last_control=last_control
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