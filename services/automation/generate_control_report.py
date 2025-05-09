import pandas as pd
import sqlite3
from datetime import datetime
from services.product_db import DB_PATH
from core.core import kontrol_ve_kaydet  # URL kontrol fonksiyonun bu ise
from services.automation.mail_service import send_mail_with_attachment

def generate_control_report():
    """
    Veritabanındaki ürünlerin kontrolünü yapar ve sonuç raporu oluşturur.
    Rapor başarıyla oluşturulursa e-posta ile gönderir.

    Returns:
        str: Rapor dosya yolu veya None.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            data = cursor.fetchall()

        if not data:
            print("📭 Veritabanında kontrol edilecek ürün yok.")
            return None

        # Ürün verilerini DataFrame'e aktar
        df = pd.DataFrame(data, columns=["Barcode", "Product_Name", "URL", "Last_Control"])

        # ✅ Ürünleri kontrol edip raporu DataFrame'e yazalım
        kontrol_sonuclari = kontrol_ve_kaydet(df=df, islem_adi="Otomasyon_Raporu", return_df=True)

        # 📄 Rapor adını belirle ve kaydet
        rapor_adi = f"otomasyon_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        kontrol_sonuclari.to_excel(rapor_adi, index=False)
        print(f"✅ Otomasyon raporu oluşturuldu: {rapor_adi}")

        # 📧 E-Posta Gönder
        if send_mail_with_attachment(rapor_adi):
            print("📧 Rapor e-posta ile gönderildi.")
        else:
            print("❌ Rapor e-posta ile gönderilemedi.")

        return rapor_adi

    except Exception as e:
        print(f"❌ Otomasyon raporu oluşturulamadı: {e}")
        return None