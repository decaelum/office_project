import math
import os
import time
import pandas as pd
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from services.logger_service import log_and_print
from services.database_services import (
    ensure_products_table_exists,
    get_all_products,
    update_url_if_changed
)
from services.url_checker_with_selenium import fetch_urls_with_driver


class AutomationThread(QThread):
    progress_updated = Signal(int)
    automation_finished = Signal(str, float)  # result path, duration

    def __init__(self, db_name="data/products.db", chunk_size=500, max_workers=3):
        super().__init__()
        self.db_name = db_name
        self.chunk_size = chunk_size
        self.max_workers = max_workers

    def run(self):
        log_and_print("🚀 Automation process started with Selenium...")
        start_time = time.time()

        ensure_products_table_exists(self.db_name)
        products = get_all_products(self.db_name)
        total = len(products)

        if total == 0:
            log_and_print("⚠️ No products found in database.", level="warning")
            self.automation_finished.emit("", 0)
            return

        chunks = [products[i:i+self.chunk_size] for i in range(0, total, self.chunk_size)]
        completed = 0
        all_results = []  # 🔍 tüm batch sonuçlarını tut

        for chunk_index, chunk in enumerate(chunks):
            filtered_chunk = [(barcode, url) for (barcode, _, url, _) in chunk]
            batch_results = fetch_urls_with_driver(filtered_chunk, total_count=total, start_index=completed)

            all_results.extend(batch_results)  # 🔗 tüm sonuçlara ekle

            for (barcode, original_url, resolved_url) in batch_results:
                if resolved_url and resolved_url != original_url:
                    update_url_if_changed(barcode, resolved_url, self.db_name)
                    log_and_print(f"✅ Updated Barcode: {barcode} | New URL: {resolved_url}")
                else:
                    log_and_print(f"✔️ No change for Barcode: {barcode}")

                completed += 1
                self.progress_updated.emit(int((completed / total) * 100))

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
                    "Changed": resolved_url != original_url
                }
                for (barcode, original_url, resolved_url) in all_results
            ])
            result_df.to_excel(result_path, index=False)
            log_and_print(f"📄 Results saved to: {result_path}")
        except Exception as e:
            log_and_print(f"❌ Failed to save result report: {e}", level="error")

        duration = time.time() - start_time
        log_and_print(f"🕒 Total automation time: {duration:.2f} seconds")
        self.automation_finished.emit(result_path, duration)
