import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from threads import baslat_tekli, baslat_toplu
import pandas as pd
import json
import os

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