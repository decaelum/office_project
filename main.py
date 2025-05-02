import tkinter as tk
from login_frame import LoginFrame
from app_frame import MainAppFrame

class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("URL Kontrol Uygulaması")
        self.geometry("500x350")
        self.resizable(False, False)

        self.current_user = None
        self.current_frame = None

        self.ekrani_degistir(LoginFrame)

    def ekrani_degistir(self, frame_sinifi):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_sinifi(self)
        self.current_frame.pack(fill="both", expand=True)

    def giris_basarili(self, kullanici_adi):
        self.current_user = kullanici_adi
        self.ekrani_degistir(MainAppFrame)

if __name__ == "__main__":
    app = Uygulama()
    app.mainloop()