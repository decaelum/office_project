import pandas as pd
import requests
import logging
import os
import time
from datetime import datetime
from tkinter import filedialog, messagebox
from utils import extract_p_segment, anahtar_olustur, logu_sifrele, extract_p_segment

def kontrol_ve_kaydet(dosya_yolu=None, log_path=None, progress_callback=None, df=None, islem_adi=None):
    hatali_baglantilar = []
    if not islem_adi:
        return  # İşlem adı girilmediyse işlem iptal edilir

    tarih_saat = datetime.now().strftime("%d-%m-%Y-%H.%M")
    log_adi = f"{tarih_saat}-{islem_adi}.log"
    log_file = os.path.join(log_path, log_adi)

    anahtar_olustur()  # İlk kez çağrıldığında anahtar oluşturur
    loglar = []         # 🔸 logları biriktireceğimiz liste

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
            logging.warning(f"{barkod} barkodu için bağlantı hatası: {e}")
            hatali_baglantilar.append({
                "Barcode": barkod,
                "URL": orijinal_url,
                "Hata": str(e)
            })
            if progress_callback:
                progress_callback(i + 1, len(df))
            continue
        if hatali_baglantilar:
            hatali_df = pd.DataFrame(hatali_baglantilar)
            hatali_path = filedialog.askopenfilename(
                title="Baglanti Hatalarini Kaydet",
                defaultextension=".xlsx",
                filetypes= [("Excel dosyalari","*.xlsx")]

            )
            if hatali_path:
                hatali_df.to.to_excel(hatali_path, index=False)
                loglar.append(f"✅ URL değişmedi - {barkod}")
                print(f"🔴 {len(hatali_baglantilar)} hatalı bağlantı bulundu.")

        eski_p = extract_p_segment(orijinal_url)
        yeni_p = extract_p_segment(yeni_url)

        if eski_p != yeni_p:
            degisenler.append({"Barcode": barkod, "Yeni URL": yeni_url})
            loglar.append(f"🔁 Değişti - {barkod}: {eski_p} → {yeni_p}")
        else:
            loglar.append(f"⚠️ Bağlantı hatası - {barkod}: {e}")

        if progress_callback:
            progress_callback(i + 1, len(df))

    sure = time.time() - start_time

    if degisenler:
        sonuc_df = pd.DataFrame(degisenler)
        save_path = filedialog.asksaveasfilename(
            title="Sonuç dosyasını kaydet",
            defaultextension=".xlsx",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        if save_path:
            sonuc_df.to_excel(save_path, index=False)
            logging.info(f"✅ {len(degisenler)} değişiklik kaydedildi: {save_path}")
            os.system(f'say "İşlem tamamlandı. {len(degisenler)} değişiklik bulundu."')
            messagebox.showinfo("Tamamlandı", f"✅ {len(degisenler)} değişiklik bulundu.\nSüre: {sure:.2f} sn")
    else:
        logging.info("🔍 Hiçbir URL değişmedi.")
        os.system('say "İşlem tamamlandı. Değişiklik yok."')
        messagebox.showinfo("Tamamlandı", f"🔍 Değişiklik bulunamadı.\nSüre: {sure:.2f} sn")

    log_adi = f"{isim}_log.enc"
    log_metin = "\n".join(loglar)
    logu_sifrele(log_metin, log_dosya_adi=os.path.join(log_path, log_adi))