import tkinter as tk
from tkinter import messagebox
from services.users import tum_kullanicilari_getir, kullanici_sil

class UserManageFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.kullanicilar_listesi = tk.Listbox(self, width=40)
        self.kullanicilar_listesi.pack(pady=10)

        tk.Button(self, text="Yenile", command=self.listele).pack(pady=5)
        tk.Button(self, text="Seçili Kullanıcıyı Sil", command=self.kullanici_sil).pack(pady=5)

        self.listele()

    def listele(self):
        self.kullanicilar_listesi.delete(0, tk.END)
        for kullanici in tum_kullanicilari_getir():
            self.kullanicilar_listesi.insert(tk.END, f"{kullanici[0]}")

    def kullanici_sil(self):
        secili = self.kullanicilar_listesi.curselection()
        if not secili:
            return
        kullanici = self.kullanicilar_listesi.get(secili[0])
        if messagebox.askyesno("Sil", f"{kullanici} silinsin mi?"):
            kullanici_sil(kullanici)
            self.listele()