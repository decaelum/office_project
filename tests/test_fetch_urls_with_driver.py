
import unittest
import random
import string
from datetime import datetime
from services.url_checker_with_selenium import fetch_urls_with_driver

def generate_fake_urls(n=100):
    base_url = "https://example.com/product/"
    return [
        (
            ''.join(random.choices(string.digits, k=13)),  # fake barcode
            f"{base_url}{i}"
        )
        for i in range(n)
    ]

class TestFetchUrlsWithDriver(unittest.TestCase):
    def test_batch_of_100_urls(self):
        test_data = generate_fake_urls(100)
        results = fetch_urls_with_driver(test_data, total_count=100, start_index=0, max_workers=3)

        self.assertEqual(len(results), 100)

        for barcode, original_url, resolved_url in results:
            self.assertTrue(barcode.isdigit())
            self.assertTrue(original_url.startswith("https://example.com/product/"))
            self.assertTrue(isinstance(resolved_url, str))
            self.assertNotEqual(resolved_url, "")

        print("\n✅ Test completed successfully for 100 URLs.")
        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    unittest.main()
