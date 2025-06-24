import os
import time
import math
import pandas as pd
import unicodedata
import re
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from services.logger_service import log_and_print
from services.database_services import (
    ensure_products_table_exists,
    get_all_products,
    update_url_if_changed,
    update_product_name
)
from services.url_checker_with_selenium import fetch_urls_with_driver


def normalize_name(name):
    if not name:
        return ""
    name = name.lower()
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


class AutomationThread(QThread):
    progress_updated = Signal(int)
    automation_finished = Signal(str, float)

    def __init__(self, db_name="data/products.db", chunk_size=500, max_workers=3, start_index=0, end_index=None):
        super().__init__()
        self.db_name = db_name
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self._stop_flag = False
        self.start_index = start_index
        self.end_index = end_index

    def stop(self):
        log_and_print("⛔ Stop signal received. Automation will terminate safely...", level="warning")
        self._stop_flag = True

    def run(self):
        log_and_print("🚀 Automation process started with Selenium...")
        start_time = time.time()

        ensure_products_table_exists(self.db_name)
        products = get_all_products(self.db_name)
        total_all = len(products)

        star = max(self.start_index, 0)
        end = self.end_index if self.end_index is not None else total_all
        products = products[star:end]
        total = len(products)

        if total == 0:
            log_and_print("⚠️ No products found in database.", level="warning")
            self.automation_finished.emit("", 0)
            return

        db_name_map = {
            barcode: normalize_name(name) for (barcode, name, _, _) in products
        }

        chunks = [products[i:i + self.chunk_size] for i in range(0, total, self.chunk_size)]
        completed = 0
        all_results = []

        for chunk_index, chunk in enumerate(chunks):
            if self._stop_flag:
                log_and_print("🛑 Automation manually stopped before processing this chunk.")
                break

            filtered_chunk = [(barcode, url) for (barcode, _, url, _) in chunk]
            batch_results = fetch_urls_with_driver(
                filtered_chunk, total_count=total, start_index=completed, max_workers=self.max_workers
            )

            all_results.extend(batch_results)

            for (barcode, original_url, resolved_url, product_id, scraped_name) in batch_results:
                if self._stop_flag:
                    log_and_print("🛑 Automation manually stopped during barcode iteration.")
                    break

                if resolved_url and resolved_url != original_url:
                    update_url_if_changed(barcode, resolved_url, self.db_name)
                    log_and_print(f"✅ Updated Barcode: {barcode} | New URL: {resolved_url}")
                else:
                    log_and_print(f"✔️ No change for Barcode: {barcode}")

                completed += 1
                self.progress_updated.emit(int((completed / total) * 100))

        if self._stop_flag:
            log_and_print("🧹 Automation stopped before completion. Saving partial results...", level="warning")
        else:
            log_and_print("🎉 Automation completed successfully.")

        result_path = ""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            result_path = f"results/automation_result_{timestamp}.xlsx"
            os.makedirs("results", exist_ok=True)

            result_df = pd.DataFrame([
                {
                    "Barcode": barcode,
                    "Original URL": original_url,
                    "Resolved URL": resolved_url,
                    "Product ID": product_id,
                    "Scraped Name": scraped_name,
                    "isNameChanged": (
                        normalize_name(scraped_name) != db_name_map.get(barcode, "")
                        if scraped_name else None
                    ),
                    "New Name": scraped_name if scraped_name and normalize_name(scraped_name) != db_name_map.get(barcode, "") else "",
                    "Changed": resolved_url != original_url
                }
                for (barcode, original_url, resolved_url, product_id, scraped_name) in all_results
            ])
            result_df.to_excel(result_path, index=False)
            log_and_print(f"📄 Results saved to: {result_path}")

            # Güncelleme işlemi
            for (barcode, _, _, _, scraped_name) in all_results:
                if scraped_name and normalize_name(scraped_name) != db_name_map.get(barcode, ""):
                    update_product_name(barcode, scraped_name, self.db_name)
                    log_and_print(f"✏️ Updated product name for {barcode} to: {scraped_name}")

        except Exception as e:
            log_and_print(f"❌ Failed to save result report: {e}", level="error")

        duration = time.time() - start_time
        log_and_print(f"🕒 Total automation time: {duration:.2f} seconds")
        self.automation_finished.emit(result_path, duration)
