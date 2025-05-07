import pandas as pd
import requests
import logging
import os
import time
from datetime import datetime
from tkinter import filedialog, messagebox
from utils import extract_netloc_and_path_from_trendyol, anahtar_olustur, logu_sifrele


def kontrol_ve_kaydet(dosya_yolu=None, log_path=None, progress_callback=None, df=None, islem_adi=None):
    hatali_baglantilar = []

    if not islem_adi:
        messagebox.showerror("Hata", "İşlem adı belirtilmedi.")
        return

    # 🔧 Log dosyasının ismi ve konumu
    tarih_saat = datetime.now().strftime("%d-%m-%Y-%H.%M")
    log_adi = f"{tarih_saat}-{islem_adi}.log"
    log_file = os.path.join(log_path, log_adi)

    # 🔐 Şifreleme için anahtar üret
    anahtar_olustur()
    loglar = []

    # 🔧 Logging ayarları
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding='utf-8',
        force=True
    )

    logging.info(f"📁 Loglama başlatıldı: {log_file}")

    # 🔄 DataFrame yükleme
    if df is None:
        if not dosya_yolu:
            messagebox.showerror("Hata", "Dosya yolu belirtilmedi.")
            return
        try:
            df = pd.read_excel(dosya_yolu, dtype={"Barcode": str})
            df.columns = df.columns.str.strip()
        except Exception as e:
            messagebox.showerror("Excel Hatası", str(e))
            return

    # 🔍 Filtreleme
    df["Max Price"] = pd.to_numeric(df["Max Price"], errors="coerce")
    df["Update Status"] = pd.to_numeric(df["Update Status"], errors="coerce")
    df = df[(df["Max Price"] != 0) & (df["Update Status"] == 404)]

    if df.empty:
        messagebox.showwarning("Uyarı", "İşlenecek satır bulunamadı.")
        return

    degisenler = []
    start_time = time.time()

    for i, (_, row) in enumerate(df.iterrows()):
        barkod = row["Barcode"]
        orijinal_url = row["URL"]

        try:
            response = requests.get(orijinal_url, allow_redirects=True, timeout=25)
            yeni_url = response.url
        except Exception as e:
            hata = f"❌ {barkod} bağlantı hatası: {e}"
            logging.warning(hata)
            loglar.append(hata)
            hatali_baglantilar.append({
                "Barcode": barkod,
                "URL": orijinal_url,
                "Hata": str(e)
            })
            if progress_callback:
                progress_callback(i + 1, len(df))
            continue

        eski_netloc = extract_netloc_and_path_from_trendyol(orijinal_url)
        yeni_netloc = extract_netloc_and_path_from_trendyol(yeni_url)

        if eski_netloc != yeni_netloc:
            degisenler.append({
                "Barcode": barkod,
                "Yeni URL": yeni_url
            })
            mesaj = f"🔁 URL değişti - {barkod}"
        else:
            mesaj = f"✅ Değişiklik yok - {barkod}"

        logging.info(mesaj)
        loglar.append(mesaj)

        if progress_callback:
            progress_callback(i + 1, len(df))

    sure = time.time() - start_time

    # ✅ Sonuçları kaydet
    if degisenler:
        sonuc_df = pd.DataFrame(degisenler)
        save_path = filedialog.asksaveasfilename(
            title="Sonuç dosyasını kaydet",
            defaultextension=".xlsx",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        if save_path:
            sonuc_df.to_excel(save_path, index=False)
            logging.info(f"🎯 {len(degisenler)} değişiklik kaydedildi: {save_path}")
            os.system(f'say "İşlem tamamlandı. {len(degisenler)} değişiklik bulundu."')
            messagebox.showinfo("Tamamlandı", f"✅ {len(degisenler)} değişiklik bulundu.\nSüre: {sure:.2f} sn")
        else:
            logging.warning("🛑 Kullanıcı sonuç dosyasını kaydetmedi.")
            messagebox.showinfo("İptal", "Kayıt işlemi iptal edildi.")
    else:
        logging.info("🔍 Hiçbir URL değişmedi.")
        os.system('say "İşlem tamamlandı. Değişiklik yok."')
        messagebox.showinfo("Tamamlandı", f"🔍 Değişiklik bulunamadı.\nSüre: {sure:.2f} sn")

    # 🧨 Hatalı bağlantılar varsa kullanıcıya kaydetme seçeneği sun
    if hatali_baglantilar:
        hatali_df = pd.DataFrame(hatali_baglantilar)
        hatali_path = filedialog.asksaveasfilename(
            title="Bağlantı Hatalarını Kaydet",
            defaultextension=".xlsx",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        if hatali_path:
            hatali_df.to_excel(hatali_path, index=False)
            logging.info(f"⚠️ {len(hatali_baglantilar)} hatalı bağlantı kaydedildi: {hatali_path}")
            messagebox.showinfo("Uyarı", f"{len(hatali_baglantilar)} hatalı bağlantı kaydedildi.")

    # 🔐 Logları şifrele
    logu_sifrele("\n".join(loglar), log_dosya_adi=os.path.join(log_path, f"{tarih_saat}-{islem_adi}_log.enc"))