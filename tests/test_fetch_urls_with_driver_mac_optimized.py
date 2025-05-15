
import unittest
import os
from services.url_checker_with_selenium import fetch_urls_with_driver
from services.logger_service import log_and_print

class TestOptimizedFetchUrls(unittest.TestCase):
    def test_batch_of_50_urls(self):
        # 50 sahte ürün oluştur
        test_data = [(f"1234567890{i:02d}", f"https://httpstat.us/200?sleep={i*2}") for i in range(1, 51)]

        results = fetch_urls_with_driver(test_data, total_count=5000, start_index=1234)

        self.assertEqual(len(results), 50)

        for idx, (barcode, original_url, resolved_url) in enumerate(results, start=1235):
            print(f"🔍 [{idx}/5000] Barcode: {barcode}")
            print(f"➡️ URL: {original_url} → {resolved_url}")

if __name__ == "__main__":
    unittest.main()
