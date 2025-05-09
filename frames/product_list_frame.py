import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from services.product_db import urunleri_getir_sayfali, urun_guncelle, urun_sil, urun_sayisini_getir

class ProductListFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.sayfa_no = 1
        self.sayfa_boyutu = 25
        self.arama_query = None  

        self.create_control_panel()
        self.create_scrollable_area()
        self.load_products()

    def create_control_panel(self):
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="🔍 Arama:").pack(side="left")
        self.search_entry = tk.Entry(control_frame)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(control_frame, text="Ara", command=self.search_products).pack(side="left", padx=5)
        tk.Button(control_frame, text="Tümünü Göster", command=self.reset_search).pack(side="left", padx=5)

        tk.Label(control_frame, text="Sayfa Başına:").pack(side="left", padx=5)
        self.page_size_var = tk.IntVar(value=self.sayfa_boyutu)
        page_size_options = ttk.Combobox(
            control_frame, 
            textvariable=self.page_size_var, 
            values=[25, 50, 100, 500, 1000],
            state="readonly", width=5
        )
        page_size_options.pack(side="left")
        page_size_options.bind("<<ComboboxSelected>>", lambda e: self.change_page_size())

        tk.Button(control_frame, text="⬅️ Önceki", command=self.prev_page).pack(side="left", padx=5)
        tk.Button(control_frame, text="➡️ Sonraki", command=self.next_page).pack(side="left", padx=5)

        self.page_info_label = tk.Label(control_frame, text="")
        self.page_info_label.pack(side="left", padx=10)

    def create_scrollable_area(self):
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_products(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        toplam_kayit = urun_sayisini_getir(self.arama_query)
        toplam_sayfa = max(1, (toplam_kayit + self.sayfa_boyutu - 1) // self.sayfa_boyutu)
        self.page_info_label.config(text=f"Sayfa: {self.sayfa_no}/{toplam_sayfa} | Toplam: {toplam_kayit}")

        if self.arama_query:
            products = urunleri_getir_sayfali(self.sayfa_no, self.sayfa_boyutu, self.arama_query)
        else:
            products = urunleri_getir_sayfali(self.sayfa_no, self.sayfa_boyutu)

        if not products:
            tk.Label(self.scrollable_frame, text="📭 Ürün bulunamadı.").pack(pady=20)
            return

        for barcode, name, url, last_control in products:
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(pady=2, fill="x", padx=20)

            info = f"📌 {barcode} | {name} | {url} | {last_control}"
            label = tk.Label(frame, anchor="w", justify="left")
            label.pack(side="left", fill="x", expand=True)

            # 🔥 Highlight tüm eşleşmeler için optimize edildi
            if self.arama_query:
                self.highlight_search_term(label, info, self.arama_query)
            else:
                label.config(text=info)

            tk.Button(frame, text="🔄 Güncelle", 
                       command=lambda b=barcode: self.urun_guncelle_popup(b)).pack(side="right", padx=5)
            tk.Button(frame, text="❌ Sil", 
                       command=lambda b=barcode: self.urun_sil(b)).pack(side="right", padx=5)

    def highlight_search_term(self, label, text, term):
        term_lower = term.lower()
        current_idx = 0
        frame = label.master  

        while True:
            start = text.lower().find(term_lower, current_idx)
            if start == -1:
                # Kalan kısmı ekle
                tk.Label(frame, text=text[current_idx:]).pack(side="left")
                break

            # Öncesi
            tk.Label(frame, text=text[current_idx:start]).pack(side="left")
            # Vurgulu kısım
            tk.Label(frame, text=text[start:start+len(term)], fg="black", bg="yellow").pack(side="left")

            current_idx = start + len(term)

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
            self.load_products()
        else:
            messagebox.showerror("Hata", "❌ Güncelleme başarısız.")

    def urun_sil(self, barcode):
        onay = messagebox.askyesno("Silme Onayı", f"'{barcode}' barkodlu ürünü silmek istiyor musunuz?")
        if onay:
            basarili = urun_sil(barcode)
            if basarili:
                messagebox.showinfo("Başarılı", f"✅ '{barcode}' ürünü silindi.")
                self.load_products()
            else:
                messagebox.showerror("Hata", "❌ Silme işlemi başarısız.")

    def next_page(self):
        toplam_kayit = urun_sayisini_getir(self.arama_query)
        toplam_sayfa = max(1, (toplam_kayit + self.sayfa_boyutu - 1) // self.sayfa_boyutu)
        if self.sayfa_no < toplam_sayfa:
            self.sayfa_no += 1
        self.load_products()

    def prev_page(self):
        if self.sayfa_no > 1:
            self.sayfa_no -= 1
        self.load_products()

    def search_products(self):
        query = self.search_entry.get().strip()
        if query:
            self.arama_query = query
            self.sayfa_no = 1
            self.load_products()

    def reset_search(self):
        self.arama_query = None
        self.sayfa_no = 1
        self.load_products()

    def change_page_size(self):
        self.sayfa_boyutu = self.page_size_var.get()
        self.sayfa_no = 1
        self.load_products()