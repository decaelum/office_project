from tkinter import messagebox, simpledialog
from services.automation.automation import start_automation, otomatik_kontrol_dbden

def configure_and_start_automation():
    mail_alici = simpledialog.askstring("E-posta Alıcısı", "📧 Rapor gönderilecek e-posta adresini girin:")
    if not mail_alici:
        return False

    try:
        sure_dakika = int(simpledialog.askstring("Süre", "⏱ Kontrol tekrarı için dakika cinsinden süre girin (Örn: 60):"))
    except (TypeError, ValueError):
        messagebox.showwarning("Uyarı", "Geçerli bir sayı girilmedi.")
        return False

    start_automation(mail_alici, sure_dakika)
    messagebox.showinfo("Otomasyon Başlatıldı", f"📅 Her {sure_dakika} dakikada bir kontrol yapılıp rapor gönderilecek.")
    return True

def manual_start_automation():
    result = messagebox.askyesno("🤖 Otomasyon", "Otomasyonu hemen başlatmak istiyor musunuz?")
    if result:
        otomatik_kontrol_dbden(islem_adi="Manual_Otomasyon")
        messagebox.showinfo("Otomasyon", "✅ Otomasyon süreci başlatıldı.")
        return True
    return False