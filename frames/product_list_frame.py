import tkinter as tk
from tkinter import messagebox, simpledialog
from services.product_db import tum_urunleri_getir, urun_guncelle, urun_sil

class ProductListFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="📦 Ürün Listesi", font=("Arial", 14, "bold")).pack(pady=10)

        products = tum_urunleri_getir()
        for barcode, name, url, last_control in products:
            frame = tk.Frame(self)
            frame.pack(pady=2, fill="x", padx=20)

            info = f"📌 {barcode} | {name} | {url} | {last_control}"
            tk.Label(frame, text=info, anchor="w").pack(side="left", fill="x", expand=True)

            tk.Button(frame, text="🔄 Güncelle", command=lambda b=barcode: self.urun_guncelle_popup(b)).pack(side="right", padx=5)
            tk.Button(frame, text="❌ Sil", command=lambda b=barcode: self.urun_sil(b)).pack(side="right", padx=5)

    def urun_guncelle_popup(self, barcode):
        yeni_ad = simpledialog.askstring("Yeni Ürün Adı", "Yeni ürün adını girin (boş bırakabilirsiniz):")
        yeni_url = simpledialog.askstring("Yeni URL", "Yeni URL'yi girin (boş bırakabilirsiniz):")
        yeni_tarih = simpledialog.askstring("Yeni Tarih", "Yeni tarih (YYYY-MM-DD, boş bırakabilirsiniz):")

        if not any([yeni_ad, yeni_url, yeni_tarih]):
            messagebox.showwarning("Uyarı", "En az bir alan doldurulmalıdır.")
            return

        basarili = urun_guncelle(barcode, product_name=yeni_ad, url=yeni_url, last_control=yeni_tarih)
        if basarili:
            messagebox.showinfo("Başarılı", f"✅ '{barcode}' ürün bilgileri güncellendi.")
            self.refresh()
        else:
            messagebox.showerror("Hata", "❌ Güncelleme başarısız.")

    def urun_sil(self, barcode):
        onay = messagebox.askyesno("Silme Onayı", f"'{barcode}' barkodlu ürünü silmek istiyor musunuz?")
        if not onay:
            return

        basarili = urun_sil(barcode)
        if basarili:
            messagebox.showinfo("Başarılı", f"✅ '{barcode}' ürünü silindi.")
            self.refresh()
        else:
            messagebox.showerror("Hata", "❌ Silme işlemi başarısız.")

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()