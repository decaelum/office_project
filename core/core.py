import pandas as pd
import requests
import time
import os
from tkinter import messagebox, filedialog
from datetime import datetime
from services.log_manager import logu_olustur, log_yaz, logu_sifrele
from core.utils import extract_netloc_and_path_from_trendyol

def kontrol_ve_kaydet(dosya_yolu=None, progress_callback=None, df=None, islem_adi=None):
    if not islem_adi:
        print("❌ İşlem adı girilmedi.")
        return

    log_dosya = logu_olustur(islem_adi)
    if not log_dosya:
        messagebox.showwarning("Log Ayarı", "Log klasörü tanımlı değil veya erişilemez. Lütfen admin'e danışın.")
        return

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
        
    # 🔸 Filtreleme sorusu
    filtrele = messagebox.askyesno(
        "Filtreleme Seçeneği",
        "Yalnızca hatalı (404) ve satışta olan (Max Price ≠ 0) ürünleri kontrol etmek ister misiniz?\n\n"
        "• 404 = URL geçersiz veya silinmiş ürün\n"
        "• Max Price ≠ 0 = Satışta olan ürünler"
    )

    if filtrele:
        df["Max Price"] = pd.to_numeric(df["Max Price"], errors="coerce")
        df["Update Status"] = pd.to_numeric(df["Update Status"], errors="coerce")
        df = df[(df["Max Price"] != 0) & (df["Update Status"] == 404)]

    if df.empty:
        messagebox.showwarning("Uyarı", "İşlenecek satır bulunamadı.")
        return

    degisenler = []
    hatali_baglantilar = []
    start_time = time.time()

    for i, (_, row) in enumerate(df.iterrows()):
        barkod = row["Barcode"]
        orijinal_url = row["URL"]

        try:
            response = requests.get(orijinal_url, allow_redirects=True, timeout=25)
            yeni_url = response.url
        except Exception as e:
            hatali_baglantilar.append({
                "Barcode": barkod,
                "URL": orijinal_url,
                "Hata": str(e)
            })
            log_yaz(log_dosya, f"❌ {barkod} barkodu için bağlantı hatası: {e}")
            if progress_callback:
                progress_callback(i + 1, len(df))
            continue

        # 🔄 URL karşılaştırması
        eski_kisim = extract_netloc_and_path_from_trendyol(orijinal_url)
        yeni_kisim = extract_netloc_and_path_from_trendyol(yeni_url)

        if eski_kisim != yeni_kisim:
            degisenler.append({
                "Barcode": barkod,
                "Yeni URL": yeni_url
            })
            log_yaz(log_dosya, f"🔁 URL değişti - {barkod}: {orijinal_url} → {yeni_url}")
        else:
            log_yaz(log_dosya, f"✅ Değişiklik yok - {barkod}")

        if progress_callback:
            progress_callback(i + 1, len(df))

    # 🔴 Hatalı bağlantılar
    if hatali_baglantilar:
        hatali_df = pd.DataFrame(hatali_baglantilar)
        hatali_path = filedialog.asksaveasfilename(
            title="Bağlantı Hatalarını Kaydet",
            defaultextension=".xlsx",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        if hatali_path:
            hatali_df.to_excel(hatali_path, index=False)
            log_yaz(log_dosya, f"❌ {len(hatali_baglantilar)} hatalı bağlantı kaydedildi.")

    # ✅ Değişen URL'ler
    if degisenler:
        sonuc_df = pd.DataFrame(degisenler)
        save_path = filedialog.asksaveasfilename(
            title="Sonuç dosyasını kaydet",
            defaultextension=".xlsx",
            filetypes=[("Excel dosyaları", "*.xlsx")]
        )
        if save_path:
            sonuc_df.to_excel(save_path, index=False)
            log_yaz(log_dosya, f"🎯 {len(degisenler)} değişiklik kaydedildi: {save_path}")
            messagebox.showinfo("Tamamlandı", f"✅ {len(degisenler)} değişiklik bulundu.\nSüre: {time.time() - start_time:.2f} sn")
    else:
        log_yaz(log_dosya, f"🔍 Hiçbir URL değişmedi.")
        messagebox.showinfo("Tamamlandı", f"🔍 Değişiklik bulunamadı.\nSüre: {time.time() - start_time:.2f} sn")

    # 🔐 Şifrele ve kaydet
    logu_sifrele(log_dosya)