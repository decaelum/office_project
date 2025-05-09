import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import threading
import pandas as pd

from frames.log_frame import LogFrame
from frames.login_frame import LoginFrame
from frames.user_add_frame import UserAddFrame
from frames.admin_user_list_frame import UserListFrame
from frames.product_upload_frame import ProductUploadFrame
from frames.product_list_frame import ProductListFrame

from core.threads import baslat_tekli, baslat_toplu
from services.log_manager import set_log_directory
from services.automation.automation_controller import configure_and_start_automation, manual_start_automation
from services.automation.automation import otomatik_kontrol_dbden


class MainAppFrame(tk.Frame):
    def __init__(self, parent, kullanici_adi, on_exit):
        super().__init__(parent)
        self.kullanici_adi = kullanici_adi
        self.on_exit = on_exit
        self.active_frame = None
        self.progress_bar = None

        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.container = tk.Frame(self)
        self.container.pack(side="right", fill="both", expand=True)

        if self.kullanici_adi == "admin":
            self.admin_menu()
        else:
            self.user_menu()

    def admin_menu(self):
        buttons = [
            ("📁 Tekli Excel Seç", self.tekli_dosya_sec),
            ("📂 Çoklu Excel Seç", self.toplu_dosya_sec),
            ("🛠 Log Klasörü Belirle", self.log_klasoru_belirle),
            ("📄 Logları Görüntüle", self.loglari_goruntule),
            ("👥 Kullanıcıları Gör", self.kullanicilari_gor),
            ("➕ Kullanıcı Ekle", self.kullanici_ekle),
            ("📦 Ürün Yükle", self.urun_yukle),
            ("📅 Otomasyon Ayarları", self.otomasyon_ayarlarini_ac),
            ("🤖 Otomasyonu Başlat", self.otomasyonu_baslat),
            ("📋 Ürünleri Listele", self.urunleri_listele),
            ("🚪 Çıkış Yap", self.exit_app)
        ]
        for text, cmd in buttons:
            tk.Button(self.menu_frame, text=text, command=cmd).pack(pady=5)

    def user_menu(self):
        tk.Button(self.menu_frame, text="📋 Ürünleri Listele", command=self.urunleri_listele).pack(pady=5)
        tk.Button(self.menu_frame, text="🚪 Çıkış Yap", command=self.exit_app).pack(pady=5)

    def otomasyonu_baslat(self):
        if messagebox.askyesno("🤖 Otomasyon", "Otomasyonu başlatmak istiyor musunuz?"):
            self.show_progress_bar()
            threading.Thread(target=self.run_automation_with_progress, daemon=True).start()

    def run_automation_with_progress(self):
        otomatik_kontrol_dbden(progress_callback=self.update_progress)
        self.hide_progress_bar()

    def show_progress_bar(self):
        if not self.progress_bar:
            self.progress_bar = ttk.Progressbar(self.container, orient="horizontal", length=400, mode="determinate")
            self.progress_bar.pack(pady=20)
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = 100
        self.progress_bar.update()

    def hide_progress_bar(self):
        if self.progress_bar:
            self.progress_bar.pack_forget()
            self.progress_bar = None

    def update_progress(self, current, total):
        if self.progress_bar:
            percentage = (current / total) * 100
            self.progress_bar["value"] = percentage
            self.progress_bar.update()

    def otomasyon_ayarlarini_ac(self):
        try:
            configure_and_start_automation()
        except Exception as e:
            messagebox.showerror("Hata", f"Otomasyon Ayarları Açılırken Hata: {e}")

    def tekli_dosya_sec(self):
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel dosyaları", "*.xlsx")])
        if not dosya_yolu:
            return
        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için bir ad girin:")
        if not islem_adi:
            messagebox.showwarning("Uyarı", "İşlem adı girilmedi.")
            return
        baslat_tekli(dosya_yolu, self.update_progress, islem_adi)

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
        baslat_toplu(df, self.update_progress, islem_adi)

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

    def urunleri_listele(self):
        self._show_frame(ProductListFrame)

    def exit_app(self):
        if messagebox.askyesno("Çıkış", "Çıkmak istiyor musunuz?"):
            self.pack_forget()
            self.on_exit(lambda parent: LoginFrame(parent, lambda k_adi: self.on_exit(lambda p: MainAppFrame(p, k_adi, self.on_exit))))

    def _show_frame(self, FrameClass):
        if self.active_frame:
            self.active_frame.pack_forget()

        if FrameClass == LogFrame:
            self.active_frame = LogFrame(self.container, self.kullanici_adi)
        else:
            self.active_frame = FrameClass(self.container)

        self.active_frame.pack(fill="both", expand=True)
    def loglari_goruntule(self):
        self._show_frame(LogFrame)