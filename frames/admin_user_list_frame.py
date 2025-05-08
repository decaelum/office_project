import tkinter as tk
from tkinter import messagebox, simpledialog
from services.users import get_all_users, kullanici_sil as sil_fonksiyonu, dogrula  

class UserListFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="📋 Kullanıcı Listesi", font=("Arial", 14, "bold")).pack(pady=10)

        users = get_all_users()
        for username, _, role in users:
            frame = tk.Frame(self)
            frame.pack(pady=2, fill="x", padx=20)

            tk.Label(frame, text=f"Kullanıcı: {username} | Yetki: {role}", anchor="w").pack(side="left", fill="x", expand=True)

            if username != "admin":
                tk.Button(frame, text="Sil", command=lambda u=username: self.kullanici_sil(u)).pack(side="right", padx=5)

    def kullanici_sil(self, username):
        onay = messagebox.askyesno("Silme Onayı", f"⚠️ '{username}' adlı kullanıcıyı silmek istiyor musunuz?")
        if not onay:
            return

        admin_sifre = simpledialog.askstring("Admin Şifresi", "🔐 Lütfen admin şifresini girin:", show="*")
        if not dogrula("admin", admin_sifre):
            messagebox.showerror("Hatalı Şifre", "❌ Geçersiz şifre. Silme işlemi iptal edildi.")
            return

        if sil_fonksiyonu(username):
            messagebox.showinfo("Başarılı", f"✅ '{username}' adlı kullanıcı silindi.")
            self.destroy()
            self.__init__(self.master)  # Yeniden yükle
        else:
            messagebox.showerror("Hata", "❌ Kullanıcı silinemedi.")