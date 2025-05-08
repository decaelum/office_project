import tkinter as tk
from tkinter import messagebox
from services.users import kullanici_ekle

class UserAddFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Kullanıcı Adı:").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Şifre:").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Kaydet", command=self.kaydet).pack(pady=10)

    def kaydet(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre zorunludur.")
            return

        try:
            kullanici_ekle(username, password)
            messagebox.showinfo("Başarılı", "Kullanıcı eklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kullanıcı eklenemedi:\n{e}")