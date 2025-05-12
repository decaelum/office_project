import unittest
import requests
import time
import random

MOCK_URL = "http://127.0.0.1:5050/product"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Mobile/15A5341f Safari/604.1"
]

class TestMockServer(unittest.TestCase):
    def test_stealth_headers_pass(self):
        """Doğru header ve bekleme süresi ile istek atılırsa yakalanmamalı."""
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9"
        }
        time.sleep(2)
        response = requests.get(MOCK_URL, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("product", response.json())
        

    def test_bot_user_agent_blocked(self):
        """Bot User-Agent ile istek atılırsa bloklanmalı."""
        headers = {"User-Agent": "python-requests/2.28.1"}
        response = requests.get(MOCK_URL, headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_rate_limit_blocked(self):
        """Çok hızlı iki istek atılırsa bloklanmalı."""
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9"
        }
        requests.get(MOCK_URL, headers=headers)  # İlk istek (geçmeli)
        response = requests.get(MOCK_URL, headers=headers)  # Hemen 2. istek
        self.assertEqual(response.status_code, 429)

    def test_missing_accept_language_blocked(self):
        """Accept-Language header eksikse bloklanmalı."""
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(MOCK_URL, headers=headers)
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()