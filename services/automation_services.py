import requests
import os
import random
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.db_manager import DatabaseManager
from services.excel_services import save_results_to_excel
from services.mail_service import send_mail_with_attachment, check_for_confirmation
from services.logger_service import log_and_print

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Mobile/15A5341f Safari/604.1"
]

def get_stealth_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

session = requests.Session()
session.headers.update(get_stealth_headers())

def smart_wait(min_wait=2, max_wait=5):
    """Random wait to simulate human behavior."""
    delay = random.uniform(min_wait, max_wait)
    log_and_print(f"🕒 Waiting for {delay:.2f} seconds before next request...")
    time.sleep(delay)

def fetch_current_url(barcode: str, old_url: str, max_retries: int = 3) -> tuple:
    attempt = 0
    while attempt < max_retries:
        try:
            session.headers.update(get_stealth_headers())
            response = session.get(old_url, timeout=7)
            return barcode, old_url, response.url  # 3 değer döndürüyoruz
        except requests.RequestException as e:
            attempt += 1
            log_and_print(f"⚠️ Attempt {attempt} failed for URL: {old_url} | Error: {e}", level="warning")
            smart_wait(3, 7)
    log_and_print(f"❌ Max retries exceeded for URL: {old_url}. Moving to next.", level="error")
    return barcode, old_url, old_url  # Hatalı durumda eski URL'yi döndür

def check_url_change(old_url: str, current_url: str) -> tuple[bool, bool]:
    """Compares old and current URLs for prefix and content ID changes, ignoring query parameters."""
    if "-p-" in old_url and "-p-" in current_url:
        old_prefix, old_suffix = old_url.split("-p-", 1)
        current_prefix, current_suffix = current_url.split("-p-", 1)

        prefix_changed = old_prefix != current_prefix

        try:
            old_content_id = old_suffix.split("/")[0].split("?")[0]
            current_content_id = current_suffix.split("/")[0].split("?")[0]
            content_id_changed = old_content_id != current_content_id
        except IndexError:
            content_id_changed = False

        return prefix_changed, content_id_changed

    return False, False

def run_full_automation(db_name: str = "products.db", operation_name: str = "URL_Check", progress_callback=None):
    results = []
    log_and_print("🚀 Connecting to database...")
    with DatabaseManager(db_name) as db:
        products = db.fetch_query("SELECT barcode, url FROM products")
        total_products = len(products)
        log_and_print(f"📦 Total products to check: {total_products}")

        futures = []
        processed_urls = set()

        with ThreadPoolExecutor(max_workers=6) as executor:
            for barcode, old_url in products:
                if old_url not in processed_urls:
                    futures.append(executor.submit(fetch_current_url, barcode, old_url))
                    processed_urls.add(old_url)

            for idx, future in enumerate(as_completed(futures), start=1):
                barcode, old_url, current_url = future.result()
                prefix_changed, content_id_changed = check_url_change(old_url, current_url)

                if prefix_changed or content_id_changed:
                    results.append({
                        "barcode": barcode,
                        "new_url": current_url,
                        "prefix_changed": prefix_changed,
                        "content_id_changed": content_id_changed
                    })
                    log_and_print(f"✅ Change detected for Barcode: {barcode} | New URL: {current_url}")

                if progress_callback:
                    progress = int((idx / len(futures)) * 100)
                    progress_callback(progress)

                time.sleep(1)  # Yavaşlatma süresi (isteğe göre ayarlanabilir)

    if results:
        log_and_print("📄 Changes detected. Generating report...")
        save_results_to_excel(results, operation_name)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_file = f"results/{timestamp}-{operation_name}.xlsx"

        if os.path.exists(report_file):
            log_and_print(f"📤 Sending email with report: {report_file}")
            send_mail_with_attachment(
                receiver_email="recipient@example.com",
                subject=f"Automation Report - {operation_name}",
                body="Please review the attached report.",
                attachment_path=report_file
            )

            log_and_print("📧 Waiting for confirmation email...")
            if check_for_confirmation():
                log_and_print("📧 Confirmation received. Updating database...")
                with DatabaseManager(db_name) as db:
                    for row in results:
                        db.update_record(
                            table="products",
                            update_fields={"url": row["new_url"]},
                            condition="barcode = ?",
                            condition_values=(row["barcode"],)
                        )
                log_and_print("✅ Database updated after email confirmation.")
            else:
                log_and_print("⚠️ No email confirmation received. Database update skipped.")
    else:
        log_and_print("📭 No URL changes detected during automation.")