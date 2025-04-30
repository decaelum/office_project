import pandas as pd
import requests
import re
import logging
import os

# LOG AYARLARI
logging.basicConfig(
    filename='islem_logu.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def extract_p_segment(url):
    """URL içinden -p- ile başlayan ürün kodunu çeker"""
    match = re.search(r'-p-\d+', str(url))
    return match.group() if match else None

def kontrol_ve_kaydet(dosya_yolu):
    logging.info(f"İşlem başlatıldı. Dosya: {dosya_yolu}")
    
    try:
        df = pd.read_excel(dosya_yolu)
    except Exception as e:
        logging.error(f"Excel dosyası okunamadı: {e}")
        print(f"❌ Excel dosyası okunamadı: {e}")
        return

    # 🔍 FİLTRELEME: Max Price ≠ 0 ve Update Status = 404 olanlar
    df_filtered = df[(df["Max Price"] != 0) & (df["Update Status"] == 404)]
    print(f"Kontrol edilecek ürün sayısı: {len(df_filtered)}")
    logging.info(f"Kontrol edilecek satır sayısı: {len(df_filtered)}")

    degisenler = []

    for index, row in df_filtered.iterrows():
        barkod = row["Barcode"]
        orijinal_url = row["URL"]

        try:
            response = requests.get(orijinal_url, allow_redirects=True, timeout=10)
            yeni_url = response.url
        except Exception as e:
            logging.warning(f"{barkod} barkodu için bağlantı hatası: {e}")
            continue

        eski_p = extract_p_segment(orijinal_url)
        yeni_p = extract_p_segment(yeni_url)

        if eski_p != yeni_p:
            degisenler.append({
                "Barcode": barkod,
                "Yeni URL": yeni_url
            })
            logging.info(f"🔁 URL değişti - Barkod: {barkod} | {eski_p} → {yeni_p}")
        else:
            logging.info(f"✅ Değişiklik yok - Barkod: {barkod}")

    if degisenler:
        sonuc_df = pd.DataFrame(degisenler)
        sonuc_df.to_excel("degisenler.xlsx", index=False)
        logging.info(f"🎯 {len(degisenler)} adet değişiklik bulundu ve 'degisenler.xlsx' dosyasına kaydedildi.")
        print(f"✅ İşlem tamamlandı! {len(degisenler)} değişen URL bulundu. 'degisenler.xlsx' oluşturuldu.")
        os.system('say "İşlem tamamlandı. Değişen ürünler bulundu."')
    else:
        logging.info("🔍 Hiçbir URL değişmedi.")
        print("🔍 Hiçbir değişiklik bulunamadı.")
        os.system('say "İşlem tamamlandı. Değişen ürün yok."')

    logging.info("İşlem tamamen sona erdi.\n")

# 🟢 ÇALIŞTIRMA YERİ
if __name__ == "__main__":
    # 📂 BURAYA Excel dosyanın tam yolunu yaz
    kontrol_ve_kaydet("deneme.xlsx")