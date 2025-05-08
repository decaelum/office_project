import tkinter as tk
from tkinter import filedialog, messagebox
from services.log_manager import logu_coz

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
        dosya_yolu = filedialog.askopenfilename(
            title="Şifreli Log Dosyasını Seç",
            filetypes=[("Şifreli Loglar", "*.enc")]
        )

        if not dosya_yolu:
            return

        try:
            self.cozulmus_metin = logu_coz(dosya_yolu)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, self.cozulmus_metin)
            self.save_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Hata", f"Log dosyası okunamadı:\n{e}")
            self.text_area.delete("1.0", tk.END)
            self.save_button.config(state="disabled")

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