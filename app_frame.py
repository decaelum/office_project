import tkinter as tk
import pandas as pd
import json
import os
from users import is_admin_kullanici, tum_kullanicilari_getir, kullanici_sil
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
from threads import baslat_tekli, baslat_toplu
from utils import logu_coz


class MainAppFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.log_path = None
        self.birlesik_df = None

        # log klasörü ayarını oku
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                    path = config.get("log_path")
                    if path and os.path.isdir(path):
                        self.log_path = path
            except Exception as e:
                print(f"⚠️ config.json okunamadı: {e}")

        # Arayüz bileşenleri
        tk.Label(self, text="URL Kontrol Paneli", font=("Arial", 14)).pack(pady=10)

        self.kullanici_adi = self.master.current_user  # Şu anki oturum açan kullanıcı
        admin_mi = is_admin_kullanici(self.kullanici_adi)

        if admin_mi:
             # Admin'e özel butonlar
            tk.Button(self, text="📁 Logları Göster", command=self.loglari_goster).pack(pady=5)
            tk.Button(self, text="👤 Yeni Kullanıcı Ekle", command=self.kullanici_ekle_popup).pack(pady=5)
            tk.Button(self, text="👥 Kullanıcıları Yönet", command=self.kullanicilari_yonet).pack(pady=5)

        tk.Button(self, text="Log Klasörü Seç", command=self.log_klasoru_sec).pack(pady=5)
        tk.Button(self, text="Tek Dosya Seç ve Başlat", command=self.tekli_islem).pack(pady=5)
        tk.Button(self, text="Çoklu Dosya Seç ve Başlat", command=self.toplu_islem).pack(pady=5)

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=300, mode="determinate")
        self.progress.pack(pady=20)

    def log_klasoru_sec(self):
        klasor = filedialog.askdirectory(title="Log klasörünü seçin")
        if klasor and os.path.isdir(klasor):
            self.log_path = klasor
            with open("config.json", "w") as f:
                json.dump({"log_path": klasor}, f)

    def tekli_islem(self):
        if not self.log_path:
            messagebox.showwarning("Uyarı", "Lütfen önce log klasörünü seçin.")
            return

        dosya_yolu = filedialog.askopenfilename(title="Excel dosyasını seçin", filetypes=[("Excel", "*.xlsx")])
        if not dosya_yolu:
            return

        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için log dosyasının adı ne olsun?")
        if not islem_adi:
            return

        baslat_tekli(dosya_yolu, self.log_path, self.guncelle_progress, islem_adi)

    def toplu_islem(self):
        if not self.log_path:
            messagebox.showwarning("Uyarı", "Lütfen önce log klasörünü seçin.")
            return

        adet = simpledialog.askinteger("Dosya Sayısı", "Kaç Excel dosyası birleştirilecek?")
        if not adet:
            return

        yollar = []
        for i in range(adet):
            yol = filedialog.askopenfilename(title=f"{i+1}. dosyayı seç", filetypes=[("Excel", "*.xlsx")])
            if not yol:
                return
            yollar.append(yol)

        try:
            df = pd.concat([pd.read_excel(yol, dtype={"Barcode": str}) for yol in yollar], ignore_index=True)
        except Exception as e:
            messagebox.showerror("Birleştirme Hatası", str(e))
            return

        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için log dosyasının adı ne olsun?")
        if not islem_adi:
            return

        baslat_toplu(df, self.log_path, self.guncelle_progress, islem_adi)

    def guncelle_progress(self, mevcut, toplam):
        self.progress["maximum"] = toplam
        self.progress["value"] = mevcut
        self.update_idletasks()
    
    def loglari_goster(self):
        klasor = filedialog.askdirectory(title="Log klasörünü seçin")
        if klasor:
            os.system(f'open "{klasor}"')  # Mac için, Windows'ta "start" kullanılır

    def kullanici_ekle_popup(self):
        pencere = tk.Toplevel(self)
        pencere.title("Yeni Kullanıcı Ekle")
        pencere.geometry("300x200")

        tk.Label(pencere, text="Kullanıcı Adı").pack()
        username_entry = tk.Entry(pencere)
        username_entry.pack()

        tk.Label(pencere, text="Şifre").pack()
        password_entry = tk.Entry(pencere, show="*")
        password_entry.pack()

        tk.Label(pencere, text="Admin yap?").pack()
        admin_var = tk.IntVar()
        admin_check = tk.Checkbutton(pencere, text="Evet", variable=admin_var)
        admin_check.pack()

        def kaydet():
            username = username_entry.get()
            password = password_entry.get()
            is_admin = admin_var.get()

            if not username or not password:
                messagebox.showwarning("Uyarı", "Tüm alanları doldurun.")
                return
            
            from users import  kullanici_ekle
            basarili = kullanici_ekle(username, password, is_admin)
            
            if basarili:
                    messagebox.showinfo("Başarılı", "Kullanıcı eklendi.")
                    pencere.destroy()
            else:
                messagebox.showerror("Hata", "Bu kullanıcı zaten kayıtlı.")

        tk.Button(pencere, text="Kaydet", command=kaydet).pack(pady=10)

  

    def loglari_goster(self):
        log_dosya = filedialog.askopenfilename(
            title="Şifreli Log Dosyasını Seç",
            filetypes=[("Şifreli Loglar", "*.enc")]
        )
        if not log_dosya:
            return

        icerik = logu_coz(log_dosya_adi=log_dosya)

        pencere = tk.Toplevel(self)
        pencere.title("Log Görüntüleyici")
        pencere.geometry("600x400")

        metin_alani = scrolledtext.ScrolledText(pencere, wrap=tk.WORD)
        metin_alani.insert(tk.END, icerik)
        metin_alani.pack(fill=tk.BOTH, expand=True)
        metin_alani.config(state=tk.DISABLED)

    def kullanicilari_yonet(self):
        pencere = tk.Toplevel(self)
        pencere.title("Kullanıcı Yönetimi")
        pencere.geometry("300x300")

        tk.Label(pencere, text="Kayıtlı Kullanıcılar").pack()

        liste = tk.Listbox(pencere)
        liste.pack(fill=tk.BOTH, expand=True)

        for kullanici in tum_kullanicilari_getir():
            liste.insert(tk.END, kullanici)

        def sil():
            secim = liste.curselection()
            if not secim:
                messagebox.showwarning("Uyarı", "Lütfen silinecek bir kullanıcı seçin.")
                return
            secilen = liste.get(secim)
            if kullanici_sil(secilen):
                messagebox.showinfo("Başarılı", f"{secilen} silindi.")
                liste.delete(secim)
            else:
                messagebox.showerror("Hata", "Admin silinemez veya kullanıcı bulunamadı.")

        tk.Button(pencere, text="🗑️ Seçili Kullanıcıyı Sil", command=sil).pack(pady=10)