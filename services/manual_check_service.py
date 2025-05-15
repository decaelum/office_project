import pandas as pd
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.excel_services import read_excel_file
from services.logger_service import log_and_print


def extract_p_segment(url: str) -> str:
    """
    URL içindeki -p- segmentini (ürün ID'si gibi) çıkartır.
    Örnek: https://site.com/urun-adı-p-12345678 → 12345678
    """
    if "-p-" in url:
        return url.split("-p-")[-1].split("/")[0].split("?")[0]
    return ""


def fetch_current_url_safe(url: str) -> str:
    """
    Verilen URL'yi güvenli şekilde getirir. Redirect varsa final URL döner.
    Hata durumunda orijinal URL döner.
    """
    try:
        response = requests.get(url, timeout=5)
        return response.url
    except Exception as e:
        log_and_print(f"⚠️ Error fetching URL: {url} | {e}", level="error")
        return url


def check_url_change(old_url: str, new_url: str) -> tuple:
    """
    İki URL arasındaki farkı kontrol eder. Hem -p- öncesi (prefix) hem de içerik ID'si açısından.
    """
    if old_url == new_url:
        return False, False

    old_prefix = old_url.split("-p-")[0] if "-p-" in old_url else old_url
    new_prefix = new_url.split("-p-")[0] if "-p-" in new_url else new_url
    prefix_changed = old_prefix.strip("/") != new_prefix.strip("/")

    old_id = extract_p_segment(old_url)
    new_id = extract_p_segment(new_url)
    content_id_changed = old_id != new_id

    return prefix_changed, content_id_changed


def manual_check_logic(file_path, progress_callback=None):
    """
    Manuel URL kontrolü. Aynı anda 3 thread ile çalışır. Her ürün için eski ve yeni URL karşılaştırması yapar.

    Args:
        file_path (str): Excel dosyasının tam yolu
        progress_callback (function, optional): ProgressBar güncellemesi için callback

    Returns:
        List[Dict]: Değişiklik içeren ürünlerin listesi
    """
    df = read_excel_file(file_path)
    products = df.to_dict(orient="records")  # ✅ HER ürün dict formatında
    total = len(products)
    completed = 0
    results = []

    def process_product(product):
        barcode = product["Barcode"]
        old_url = product["URL"]
        current_url = fetch_current_url_safe(old_url)

        prefix_changed, content_id_changed = check_url_change(old_url, current_url)

        log_and_print(
            f"🔎 Checked: {barcode} | Prefix changed: {prefix_changed} | "
            f"ID changed: {content_id_changed} | Thread: {threading.current_thread().name}"
        )

        return {
            "Barcode": barcode,
            "Old URL": old_url,
            "New URL": current_url,
            "Prefix Changed": prefix_changed,
            "Content ID Changed": content_id_changed
        }

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_product = {
            executor.submit(process_product, product): product for product in products
        }

        for future in as_completed(future_to_product):
            result = future.result()
            if result["Prefix Changed"] or result["Content ID Changed"]:
                results.append(result)

            completed += 1
            percent = int((completed / total) * 100)
            if progress_callback:
                progress_callback(percent)

    return results