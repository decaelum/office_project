import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from frames.log_frame import LogFrame
from frames.login_frame import LoginFrame
from frames.user_add_frame import UserAddFrame
from frames.admin_user_list_frame import UserListFrame
from frames.product_upload_frame import ProductUploadFrame
from frames.product_list_frame import ProductListFrame
from core.threads import baslat_tekli, baslat_toplu
from services.log_manager import set_log_directory
import pandas as pd

class MainAppFrame(tk.Frame):
    def __init__(self, parent, kullanici_adi, on_exit):
        super().__init__(parent)
        self.kullanici_adi = kullanici_adi
        self.on_exit = on_exit
        self.active_frame = None

        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.container = tk.Frame(self)
        self.container.pack(side="right", fill="both", expand=True)

        if self.kullanici_adi == "admin":
            self.admin_menu()
        else:
            self.user_menu()

    def admin_menu(self):
        tk.Button(self.menu_frame, text="📁 Tekli Excel Seç", command=self.tekli_dosya_sec).pack(pady=5)
        tk.Button(self.menu_frame, text="📂 Çoklu Excel Seç", command=self.toplu_dosya_sec).pack(pady=5)
        tk.Button(self.menu_frame, text="🛠 Log Klasörü Belirle", command=self.log_klasoru_belirle).pack(pady=5)
        tk.Button(self.menu_frame, text="📄 Logları Görüntüle", command=self.loglari_goruntule).pack(pady=5)
        tk.Button(self.menu_frame, text="👥 Kullanıcıları Gör", command=self.kullanicilari_gor).pack(pady=5)
        tk.Button(self.menu_frame, text="➕ Kullanıcı Ekle", command=self.kullanici_ekle).pack(pady=5)
        tk.Button(self.menu_frame, text="📦 Ürün Yükle", command=self.urun_yukle).pack(pady=5)
        tk.Button(self.menu_frame, text="🚪 Çıkış Yap", command=self.exit_app).pack(pady=10)
        tk.Button(self.menu_frame, text="📋 Ürünleri Listele", command=self.urunleri_listele).pack(pady=5)

    def user_menu(self):
        tk.Button(self.menu_frame, text="📁 Tekli Excel Seç", command=self.tekli_dosya_sec).pack(pady=5)
        tk.Button(self.menu_frame, text="📂 Çoklu Excel Seç", command=self.toplu_dosya_sec).pack(pady=5)
        tk.Button(self.menu_frame, text="📦 Ürün Yükle", command=self.urun_yukle).pack(pady=5)
        tk.Button(self.menu_frame, text="🚪 Çıkış Yap", command=self.exit_app).pack(pady=10)

    def tekli_dosya_sec(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel dosyaları", "*.xlsx")])
        if not dosya_yolu:
            return

        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için bir ad girin:")
        if not islem_adi:
            messagebox.showwarning("Uyarı", "İşlem adı girilmedi.")
            return

        baslat_tekli(dosya_yolu, self.progress_guncelle, islem_adi)

    def toplu_dosya_sec(self):
        dosya_yollari = filedialog.askopenfilenames(filetypes=[("Excel dosyaları", "*.xlsx")])
        if not dosya_yollari:
            return

        try:
            dataframes = [pd.read_excel(dosya) for dosya in dosya_yollari]
            df = pd.concat(dataframes, ignore_index=True)
        except Exception as e:
            messagebox.showerror("Hata", f"Excel dosyaları okunamadı:\n{e}")
            return

        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için bir ad girin:")
        if not islem_adi:
            messagebox.showwarning("Uyarı", "İşlem adı girilmedi.")
            return

        baslat_toplu(df, self.progress_guncelle, islem_adi)

    def log_klasoru_belirle(self):
        path = filedialog.askdirectory(title="Log klasörünü seçin")
        if path:
            if set_log_directory(path):
                messagebox.showinfo("Başarılı", f"Log klasörü ayarlandı:\n{path}")
            else:
                messagebox.showerror("Hata", "Log klasörü ayarlanamadı!")

    def loglari_goruntule(self):
        self._show_frame(LogFrame)

    def kullanici_ekle(self):
        self._show_frame(UserAddFrame)

    def kullanicilari_gor(self):
        self._show_frame(UserListFrame)

    def urun_yukle(self):
        self._show_frame(ProductUploadFrame)

    def progress_guncelle(self, current, total):
        print(f"İlerleme: {current}/{total}")

    def exit_app(self):
        onay = messagebox.askyesno("Çıkış Yap", "Oturumdan çıkmak istiyor musunuz?")
        if onay:
            self.pack_forget()
            self.on_exit(lambda parent: LoginFrame(parent, lambda kullanici_adi: self.on_exit(lambda p: MainAppFrame(p, kullanici_adi, self.on_exit))))

    def _show_frame(self, FrameClass):
        if self.active_frame:
            self.active_frame.pack_forget()
        self.active_frame = FrameClass(self.container)
        self.active_frame.pack(fill="both", expand=True)
    
    def urunleri_listele(self):
        if self.active_frame:
            self.active_frame.pack_forget()
        self.active_frame = ProductListFrame(self.container)
        self.active_frame.pack(fill="both", expand=True)