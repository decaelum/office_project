import tkinter as tk
from tkinter import messagebox
from users import db_olustur, dogrula

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Veritabanını oluştur (ilk çalıştırmada)
        db_olustur()

        tk.Label(self, text="Kullanıcı Girişi", font=("Arial", 14)).pack(pady=20)

        tk.Label(self, text="Kullanıcı Adı").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Şifre").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Giriş Yap", command=self.giris_yap).pack(pady=15)

    def giris_yap(self):
        kullanici = self.username_entry.get()
        sifre = self.password_entry.get()

        if not kullanici or not sifre:
            messagebox.showwarning("Eksik Bilgi", "Lütfen kullanıcı adı ve şifre girin.")
            return

        if dogrula(kullanici, sifre):
            messagebox.showinfo("Giriş Başarılı", f"Hoş geldin, {kullanici}")
            self.master.giris_basarili(kullanici)  # main.py içindeki fonksiyonu tetikler
        else:
            messagebox.showerror("Giriş Hatası", "Kullanıcı adı veya şifre hatalı.")