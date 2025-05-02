import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pandas as pd
import os
import json
from threads import baslat_tekli, baslat_toplu

class URLKontrolArayuz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("URL Kontrol Arayüzü")
        self.root.geometry("450x300")
        self.root.protocol("WM_DELETE_WINDOW", self.pencereyi_kapat)

        self.log_path = None

        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                    path = config.get("log_path")
                    if path and os.path.isdir(path):
                        self.log_path = path
            except Exception as e:
                print(f"⚠️ config.json okunamadı: {e}")

        self.label = tk.Label(self.root, text="Excel dosyasını seçin:", font=("Arial", 12))
        self.label.pack(pady=10)

        self.log_button = tk.Button(self.root, text="Log Klasörü Seç", command=self.log_klasoru_sec)
        self.log_button.pack(pady=5)

        self.single_button = tk.Button(self.root, text="Tek Dosya Seç ve Başlat", command=self.dosya_sec_ve_kontrol_et)
        self.single_button.pack(pady=5)

        self.multi_button = tk.Button(self.root, text="Toplu Dosya Seç ve Başlat", command=self.toplu_dosya_sec_ve_birlestir)
        self.multi_button.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.root.mainloop()

    def log_klasoru_sec(self):
        klasor = filedialog.askdirectory(title="Log klasörünü seçin")
        if klasor and os.path.isdir(klasor):
            self.log_path = klasor
            with open("config.json", "w") as f:
                json.dump({"log_path": klasor}, f)

    def dosya_sec_ve_kontrol_et(self):
        if not self.log_path:
            messagebox.showwarning("Uyarı", "Önce log klasörü seçin.")
            return

        dosya_yolu = filedialog.askopenfilename(title="Excel dosyası seç", filetypes=[("Excel", "*.xlsx")])
        if not dosya_yolu:
            return

        islem_adi = simpledialog.askstring("İşlem Adı", "Bu işlem için log dosyasının adı ne olsun?")
        if not islem_adi:
            return

        baslat_tekli(dosya_yolu, self.log_path, self.guncelle_progress, islem_adi)

    def toplu_dosya_sec_ve_birlestir(self):
        if not self.log_path:
            messagebox.showwarning("Uyarı", "Önce log klasörü seçin.")
            return

        adet = simpledialog.askinteger("Excel Sayısı", "Kaç Excel dosyası birleştirilecek?")
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
        self.root.update_idletasks()

    def pencereyi_kapat(self):
        self.root.destroy()
        exit(0)

if __name__ == "__main__":
    URLKontrolArayuz()