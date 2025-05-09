import schedule
import threading
import time
from datetime import datetime
import pandas as pd
import os

from services.product_db import urunleri_getir_sayfali, urun_sayisini_getir
from services.automation.mail_service import send_mail_with_attachment
from core.core import kontrol_ve_kaydet
from services.log_manager import log_yaz, logu_olustur

def otomatik_kontrol_dbden(islem_adi=None, progress_callback=None):
    if not islem_adi:
        islem_adi = f"Otomasyon_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    
    log_dosya = logu_olustur(islem_adi)
    log_yaz(log_dosya, "⏰ Otomatik kontrol başlatıldı.")

    try:
        toplam_kayit = urun_sayisini_getir()
        if toplam_kayit == 0:
            log_yaz(log_dosya, "📭 Veritabanında kontrol edilecek ürün yok.")
            return

        sayfa_boyutu = 1000
        sayfa_no = 1
        all_data = []
        current_progress = 0

        while True:
            products = urunleri_getir_sayfali(sayfa_no, sayfa_boyutu)
            if not products:
                break

            all_data.extend(products)
            current_progress += len(products)

            # ✅ Progress Bar Güncelle
            if progress_callback:
                progress_callback(current_progress, toplam_kayit)

            print(f"🔄 Sayfa {sayfa_no} işlendi. Toplam işlenen: {current_progress}/{toplam_kayit}")
            sayfa_no += 1

        if not all_data:
            return

        df = pd.DataFrame(all_data, columns=["Barcode", "Product_Name", "URL", "Last_Control"])
        rapor_adi = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_NewURL.xlsx"

        # ✅ kontrol_ve_kaydet'e de progress_callback gönderiyoruz.
        sonuc_dosya = kontrol_ve_kaydet(df=df, islem_adi=islem_adi, rapor_adi=rapor_adi, progress_callback=progress_callback)

        if sonuc_dosya and os.path.exists(sonuc_dosya):
            send_mail_with_attachment(sonuc_dosya)

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        if progress_callback:
            # ✅ Progress Bar'ı tam dolu göster ve sıfırla
            progress_callback(1, 1)
        print("✅ Otomasyon tamamlandı.\n")

def otomasyonu_baslat_db(kontrol_saatleri):
    for saat in kontrol_saatleri:
        schedule.every().day.at(saat).do(otomatik_kontrol_dbden)
    print(f"🚀 Otomasyon aktif! Kontrol saatleri: {', '.join(kontrol_saatleri)}")

    while True:
        schedule.run_pending()
        time.sleep(60)

def start_automation(mail_receiver, interval_minutes):
    def job():
        while True:
            otomatik_kontrol_dbden()
            time.sleep(interval_minutes * 60)

    thread = threading.Thread(target=job, daemon=True)
    thread.start()