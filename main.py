import tkinter as tk
from frames.login_frame import LoginFrame
from frames.app_frame import MainAppFrame

class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ofis Uygulaması")
        self.geometry("800x600")
        self.current_frame = None

        self.ekrani_degistir(lambda parent: LoginFrame(parent, self.giris_basarili))

    def ekrani_degistir(self, frame_sinifi):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_sinifi(self)
        self.current_frame.pack(fill="both", expand=True)

    def giris_basarili(self, kullanici_adi):
        print(f"🎉 Giriş başarılı: {kullanici_adi}")
        self.ekrani_degistir(lambda parent: MainAppFrame(parent, kullanici_adi, self.ekrani_degistir))


if __name__ == "__main__":
    app = Uygulama()
    app.mainloop()