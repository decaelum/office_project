
import tkinter as tk
from tkinter import messagebox
from services.users import dogrula

class LoginFrame(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        self.create_widgets()

    def create_widgets(self):
        self.label_user = tk.Label(self, text="Kullanıcı Adı:")
        self.label_user.pack(pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        self.label_pass = tk.Label(self, text="Şifre:")
        self.label_pass.pack(pady=5)
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        self.button_login = tk.Button(self, text="Giriş Yap", command=self.login)
        self.button_login.pack(pady=10)

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        if dogrula(username, password):
            self.on_login_success(username)
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış.")