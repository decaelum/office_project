import tkinter as tk
import os 
from tkinter import filedialog, messagebox
from services.log_manager import logu_coz , get_log_directory_from_config

class LogFrame(tk.Frame):
    def __init__(self, parent, kullanici_adi):
        super().__init__(parent)
        self.parent = parent
        self.kullanici_adi = kullanici_adi
        self.config(padx=10, pady=10)

        if self.kullanici_adi != "admin":
            tk.Label(self, text="❌ Bu bölüme yalnızca admin erişebilir.").pack(pady=20)
            return

        tk.Label(self, text="🔐 Şifreli log dosyasını seçin:", font=("Arial", 12, "bold")).pack(pady=5)

        tk.Button(self, text="Dosya Seç", command=self.log_dosyasini_sec).pack(pady=5)

        self.text_area = tk.Text(self, height=20, width=80)
        self.text_area.pack(pady=5)

        self.save_button = tk.Button(self, text="TXT olarak kaydet", command=self.txt_kaydet, state="disabled")
        self.save_button.pack(pady=5)

        self.cozulmus_metin = ""

    def log_dosyasini_sec(self):
        log_root = get_log_directory_from_config()

        if not log_root or not os.path.isdir(log_root):
            messagebox.showerror("Hata", "Log klasörü ayarlı değil veya mevcut değil.")
            return

        dosyalar = [f for f in os.listdir(log_root) if f.endswith(".log.enc")]

        if not dosyalar:
            messagebox.showinfo("Bilgi", "Hiçbir şifreli log dosyası bulunamadı.")
            return

        secim_penceresi = tk.Toplevel(self)
        secim_penceresi.title("Log Dosyası Seç")

        tk.Label(secim_penceresi, text="Bir log dosyası seçin:").pack(pady=5)

        listbox = tk.Listbox(secim_penceresi, width=60, height=10)
        for f in dosyalar:
            listbox.insert(tk.END, f)
        listbox.pack(padx=10, pady=5)

        def logu_yukle():
            secilen_index = listbox.curselection()
            if not secilen_index:
                return

            dosya_adi = dosyalar[secilen_index[0]]
            tam_yol = os.path.join(log_root, dosya_adi)

            try:
                cozulmus = logu_coz(tam_yol)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, cozulmus)
                self.save_button.config(state="normal")
                secim_penceresi.destroy()
            except Exception as e:
                messagebox.showerror("Hata", f"Log çözülemedi:\n{e}")
                self.text_area.delete("1.0", tk.END)
                self.save_button.config(state="disabled")

        tk.Button(secim_penceresi, text="Göster", command=logu_yukle).pack(pady=10)

    def txt_kaydet(self):
        dosya_yolu = filedialog.asksaveasfilename(
            title="Log'u TXT olarak kaydet",
            defaultextension=".txt",
            filetypes=[("Metin Dosyası", "*.txt")]
        )

        if not dosya_yolu:
            return

        try:
            logu_txt_olarak_kaydet(self.cozulmus_metin, dosya_yolu)
            messagebox.showinfo("Başarılı", "Log başarıyla TXT olarak kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt başarısız:\n{e}")