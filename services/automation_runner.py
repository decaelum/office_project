import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.logger_service import log_and_print
from services.url_checker_with_selenium import fetch_urls_with_driver
from services.excel_services import save_results_to_excel
from core.db_manager import DatabaseManager
from PySide6.QtCore import QThread, Signal

class AutomationThread(QThread):
    progress_updated = Signal(int)
    automation_finished = Signal()
    log_message = Signal(str)

    def run(self):
        print("🧪 [DEBUG] AutomationThread.run() started", flush=True)

        try:
            self.log_message.emit("🚀 Starting full automation process...")
            run_full_automation(
                db_name="data/products.db",
                operation_name="URL_Check",
                progress_callback=self.progress_updated.emit,
                log_callback=self.log_message.emit
            )
            self.log_message.emit("✅ Automation process completed successfully.")
            self.automation_finished.emit()
        except Exception as e:
            self.log_message.emit(f"❌ Automation process failed: {e}")
            print(f"[ERROR] run() exception: {e}", flush=True)
            self.automation_finished.emit()

def check_url_change(old_url: str, current_url: str) -> tuple[bool, bool]:
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

def run_full_automation(db_name: str = "data/products.db", operation_name: str = "URL_Check", progress_callback=None, log_callback=print):
    log_callback("🚀 Connecting to database...")
    results = []
    with DatabaseManager(db_name) as db:
        products = db.fetch_query("SELECT barcode, url FROM products")
        total_products = len(products)
        log_callback(f"📦 Total products to check: {total_products}")

        chunk_size = 500
        chunks = [products[i:i + chunk_size] for i in range(0, total_products, chunk_size)]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch_urls_with_driver, chunk) for chunk in chunks]

            completed = 0
            for future in as_completed(futures):
                log_and_print("🚀 A batch thread started processing...")

                batch_result = future.result()

                log_and_print("✅ A batch thread finished.")
                for barcode, old_url, current_url in batch_result:
                    prefix_changed, content_id_changed = check_url_change(old_url, current_url)

                    if prefix_changed or content_id_changed:
                        results.append({
                            "barcode": barcode,
                            "new_url": current_url,
                            "prefix_changed": prefix_changed,
                            "content_id_changed": content_id_changed
                        })
                        log_and_print(f"✅ Change detected for Barcode: {barcode} | New URL: {current_url}")

                    completed += 1
                    if progress_callback:
                        progress = int((completed / total_products) * 100)
                        progress_callback(progress)
                time.sleep(0.1)

    if results:
        log_and_print("📄 Changes detected. Generating report...")
        save_results_to_excel(results, operation_name)
        log_and_print("✅ Report saved successfully.")
    else:
        log_and_print("📭 No URL changes detected during automation.")
