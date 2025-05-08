import tkinter as tk
from tkinter import messagebox
from services.product_db import urun_ekle
from datetime import datetime

class ManualProductEntryFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="📦 Elle Ürün Girişi", font=("Arial", 14, "bold")).pack(pady=10)

        # Barkod
        tk.Label(self, text="Barkod:").pack(pady=5)
        self.entry_barcode = tk.Entry(self)
        self.entry_barcode.pack(pady=5)

        # Ürün Adı
        tk.Label(self, text="Ürün Adı:").pack(pady=5)
        self.entry_name = tk.Entry(self)
        self.entry_name.pack(pady=5)

        # URL
        tk.Label(self, text="Ürün URL:").pack(pady=5)
        self.entry_url = tk.Entry(self)
        self.entry_url.pack(pady=5)

        # Kaydet Butonu
        tk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=15)

    def kaydet(self):
        barcode = self.entry_barcode.get()
        name = self.entry_name.get()
        url = self.entry_url.get()
        date = datetime.now().strftime("%Y-%m-%d")

        if not barcode or not name or not url:
            messagebox.showwarning("Uyarı", "Tüm alanlar doldurulmalıdır.")
            return

        success = urun_ekle(barcode, name, url, date)
        if success:
            messagebox.showinfo("Başarılı", "✅ Ürün başarıyla kaydedildi.")
            self.entry_barcode.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            self.entry_url.delete(0, tk.END)
        else:
            messagebox.showerror("Hata", "❌ Ürün eklenemedi. Barkod zaten kayıtlı olabilir.")