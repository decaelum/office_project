import pandas as pd
import time
import requests
from tkinter import messagebox, filedialog
from core.utils import extract_netloc_and_path_from_trendyol
from services.log_manager import log_yaz, logu_olustur, logu_sifrele

def kontrol_ve_kaydet(dosya_yolu=None, progress_callback=None, df=None, islem_adi=None, rapor_adi=None, filtrele=True):
    """
    Hem manuel hem otomasyon için esnek kontrol ve raporlama fonksiyonu.

    Args:
        dosya_yolu (str): Excel dosya yolu (manuel kullanımda).
        progress_callback (func): Progress bar güncelleme fonksiyonu.
        df (DataFrame): Otomasyonda kullanılacak DataFrame.
        islem_adi (str): Log ve rapor adı için işlem adı.
        rapor_adi (str): Rapor dosya adı (otomasyonda zorunlu).
        filtrele (bool): Manuel kullanımda filtre uygulama tercihi.
    """
    if not islem_adi:
        print("❌ İşlem adı belirtilmedi.")
        return

    log_dosya = logu_olustur(islem_adi)
    if not log_dosya:
        messagebox.showwarning("Log Ayarı", "Log klasörü ayarlı değil. Lütfen admin'e danışın.")
        return

    if df is None and dosya_yolu:
        try:
            df = pd.read_excel(dosya_yolu, dtype={"Barcode": str})
            df.columns = df.columns.str.strip()
        except Exception as e:
            messagebox.showerror("Excel Hatası", str(e))
            return

    if df is None or df.empty:
        messagebox.showwarning("Uyarı", "İşlenecek veri bulunamadı.")
        return

    # 📌 Filtreleme (Sadece manuelde uygulanır)
    if filtrele and "Max Price" in df.columns and "Update Status" in df.columns:
        df["Max Price"] = pd.to_numeric(df["Max Price"], errors="coerce")
        df["Update Status"] = pd.to_numeric(df["Update Status"], errors="coerce")
        df = df[(df["Max Price"] != 0) & (df["Update Status"] == 404)]

    if df.empty:
        messagebox.showwarning("Uyarı", "Filtre sonrası işlenecek satır kalmadı.")
        return

    degisenler = []
    hatali_baglantilar = []
    toplam_kayit = len(df)
    start_time = time.time()

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        barkod = row["Barcode"]
        orijinal_url = row["URL"]

        try:
            print(f"🔎 {barkod} için URL kontrol ediliyor...")
            response = requests.get(orijinal_url, allow_redirects=True, timeout=25)
            yeni_url = response.url
        except Exception as e:
            hatali_baglantilar.append({"Barcode": barkod, "URL": orijinal_url, "Hata": str(e)})
            log_yaz(log_dosya, f"❌ {barkod} bağlantı hatası: {e}")
            if progress_callback:
                progress_callback(i, toplam_kayit)
            continue

        eski_path, eski_content_id = extract_netloc_and_path_from_trendyol(orijinal_url)
        yeni_path, yeni_content_id = extract_netloc_and_path_from_trendyol(yeni_url)

        url_changed = eski_path != yeni_path
        content_id_changed = eski_content_id != yeni_content_id

        if url_changed or content_id_changed:
            degisenler.append({
                "Barcode": barkod,
                "New URL": yeni_url,
                "URL Changed": url_changed,
                "Content ID Changed": content_id_changed
            })
            log_yaz(log_dosya, f"🔁 {barkod} | URL Changed: {url_changed} | Content ID Changed: {content_id_changed} → {yeni_url}")
        else:
            log_yaz(log_dosya, f"✅ {barkod} değişiklik yok.")

        if progress_callback:
            progress_callback(i, toplam_kayit)

    # 📤 Sonuç Kaydetme
    if degisenler:
        sonuc_df = pd.DataFrame(degisenler)
        if not rapor_adi:
            save_path = filedialog.asksaveasfilename(
                title="Sonuç Dosyasını Kaydet", defaultextension=".xlsx",
                filetypes=[("Excel dosyaları", "*.xlsx")]
            )
        else:
            save_path = rapor_adi

        if save_path:
            sonuc_df.to_excel(save_path, index=False)
            log_yaz(log_dosya, f"🎯 {len(degisenler)} değişiklik kaydedildi: {save_path}")
            if not rapor_adi:  # Sadece manuel işlemde bilgi mesajı göster
                messagebox.showinfo("Tamamlandı", f"✅ {len(degisenler)} değişiklik bulundu.\nSüre: {time.time() - start_time:.2f} sn")
        else:
            save_path = None
    else:
        log_yaz(log_dosya, "🔍 Hiçbir değişiklik bulunamadı.")
        if not rapor_adi:
            messagebox.showinfo("Tamamlandı", f"🔍 Değişiklik bulunamadı.\nSüre: {time.time() - start_time:.2f} sn")
        save_path = None

    # ✅ Logu Şifrele
    logu_sifrele(log_dosya)
    return save_path