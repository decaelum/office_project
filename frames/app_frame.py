import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from frames.log_frame import LogFrame
from core.threads import baslat_tekli, baslat_toplu
from services.log_manager import set_log_directory
import pandas as pd

class MainAppFrame(tk.Frame):
    def __init__(self, parent, kullanici_adi):
        super().__init__(parent)
        self.kullanici_adi = kullanici_adi
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
        tk.Button(self.menu_frame, text="➕ Kullanıcı Ekle", command=self.kullanici_ekle).pack(pady=5)

    def user_menu(self):
        tk.Button(self.menu_frame, text="📁 Tekli Excel Seç", command=self.tekli_dosya_sec).pack(pady=5)
        tk.Button(self.menu_frame, text="📂 Çoklu Excel Seç", command=self.toplu_dosya_sec).pack(pady=5)

    def log_klasoru_belirle(self):
        path = filedialog.askdirectory(title="Log klasörünü seçin")
        if path:
            if set_log_directory(path):
                messagebox.showinfo("Başarılı", f"Log klasörü ayarlandı:\n{path}")
            else:
                messagebox.showerror("Hata", "Log klasörü ayarlanamadı!")

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
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel dosyaları", "*.xlsx")])
        if not dosya_yolu:
            return

        try:
            df = pd.read_excel(dosya_yolu)
        except Exception as e:
            messagebox.showerror("Hata", f"Excel dosyası okunamadı:\n{e}")
            return

        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için bir ad girin:")
        if not islem_adi:
            messagebox.showwarning("Uyarı", "İşlem adı girilmedi.")
            return

        baslat_toplu(df, self.progress_guncelle, islem_adi)

    def loglari_goruntule(self):
        if self.active_frame:
            self.active_frame.pack_forget()

        self.active_frame = LogFrame(self.container, self.kullanici_adi)
        self.active_frame.pack(fill="both", expand=True)

    def kullanici_ekle(self):
        from frames.admin_user_add_frame import UserAddFrame
        if self.active_frame:
            self.active_frame.pack_forget()
        self.active_frame = UserAddFrame(self.container)
        self.active_frame.pack(fill="both", expand=True)

    def progress_guncelle(self, current, total):
        print(f"İlerleme: {current}/{total}")