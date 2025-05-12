import requests
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.db_manager import DatabaseManager
from services.excel_services import save_results_to_excel
from services.mail_service import send_mail_with_attachment, check_for_confirmation
from services.logger_service import log_and_print

def fetch_current_url(url: str, max_retries: int = 3, wait_seconds: int = 5) -> str:
    """Fetches the current URL after redirects, with retry logic on failure."""
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(url, timeout=5)
            return response.url
        except requests.RequestException as e:
            attempt += 1
            log_and_print(f"⚠️ Attempt {attempt} failed for URL: {url} | Error: {e}", level="warning")
            if attempt < max_retries:
                log_and_print(f"⏳ Waiting {wait_seconds} seconds before retrying...", level="info")
                time.sleep(wait_seconds)
            else:
                log_and_print(f"❌ Max retries exceeded for URL: {url}. Moving to next.", level="error")
                return url  # Hatalı URL ile devam et

def check_url_change(old_url: str, current_url: str) -> tuple[bool, bool]:
    """Compares old and current URLs for prefix and content ID changes."""
    if "-p-" in old_url and "-p-" in current_url:
        old_prefix, old_suffix = old_url.split("-p-", 1)
        current_prefix, current_suffix = current_url.split("-p-", 1)

        prefix_changed = old_prefix != current_prefix
        try:
            old_content_id = old_suffix.split("/")[0]
            current_content_id = current_suffix.split("/")[0]
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

        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = [executor.submit(fetch_current_url_safe, (barcode, old_url)) for barcode, old_url in products]

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
                    progress = int((idx / total_products) * 100)
                    progress_callback(progress)
                time.sleep(10)

    if results:
        log_and_print("📄 Changes detected. Generating report...")
        save_results_to_excel(results, operation_name)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_file = f"results/{timestamp}-{operation_name}.xlsx"

        if os.path.exists(report_file):
            log_and_print(f"📤 Sending email with report: {report_file}")
            send_mail_with_attachment(
                receiver_email="recipient@example.com",  # Bunu GUI'den dinamik yapıyoruz.
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