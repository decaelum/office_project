import tkinter as tk
from tkinter import messagebox
from services.users import kullanici_ekle

class UserAddFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="👤 Yeni Kullanıcı Ekle", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Kullanıcı Adı:").pack(pady=2)
        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=2)

        tk.Label(self, text="Şifre:").pack(pady=2)
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=2)

        self.is_admin_var = tk.IntVar()
        tk.Checkbutton(self, text="Admin yetkisi ver", variable=self.is_admin_var).pack(pady=5)

        tk.Button(self, text="Kaydet", command=self.kullanici_ekle).pack(pady=10)

    def kullanici_ekle(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        is_admin = bool(self.is_admin_var.get())

        if not username or not password:
            messagebox.showwarning("Eksik Bilgi", "Kullanıcı adı ve şifre gereklidir.")
            return

        if kullanici_ekle(username, password, is_admin):
            messagebox.showinfo("Başarılı", f"✅ '{username}' adlı kullanıcı eklendi.")
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            self.is_admin_var.set(0)
        else:
            messagebox.showerror("Hata", "❌ Kullanıcı zaten mevcut.")