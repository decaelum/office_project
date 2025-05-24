import unittest
import os
from services.logger_service import log_and_print
from services.farmasi_checker import scrape_farmasi_product_links

class TestFarmasiScraper(unittest.TestCase):

    def test_scraper_links_format_and_count(self):
        """
        Scraper'dan dönen linklerin boş olmadığını ve 'trendyol.com' içerdiğini kontrol eder
        """
        links = scrape_farmasi_product_links(max_pages=1)
        self.assertTrue(len(links) > 0, "❌ Hiç ürün linki bulunamadı.")
        for url in links:
            self.assertIn("trendyol.com", url, f"❌ Geçersiz URL formatı: {url}")

    def test_screenshot_created(self):
        """
        İlk sayfa için ekran görüntüsünün alınıp results klasörüne kaydedildiğini kontrol eder
        """
        scrape_farmasi_product_links(max_pages=1)
        screenshot_path = "results/page_1_screenshot.png"
        self.assertTrue(os.path.exists(screenshot_path), "❌ Screenshot alınamadı.")

        # Temizlik (tercihe bağlı)
        os.remove(screenshot_path)

if __name__ == "__main__":
    log_and_print("🔪 Unit test for Farmasi Scraper is running...")
    unittest.main()