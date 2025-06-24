import unittest
import shutil
import subprocess
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


class TestChromeDriverAvailability(unittest.TestCase):

    def test_chromedriver_exists_in_path(self):
        """Test if chromedriver exists in system PATH"""
        driver_path = shutil.which("chromedriver")
        self.assertIsNotNone(driver_path, msg="❌ 'chromedriver' not found in PATH. Download from https://chromedriver.chromium.org/downloads")

    def test_chrome_version_matches_driver(self):
        """Test if Chrome browser is installed and its version is accessible"""
        try:
            result = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                capture_output=True,
                text=True
            )
            chrome_version = result.stdout.strip()
            self.assertIn("Google Chrome", chrome_version, msg="❌ Google Chrome is not installed or path is invalid.")
        except FileNotFoundError:
            self.fail("❌ Google Chrome not found at default location. Check your installation.")

    def test_driver_starts_headless(self):
        """Test if selenium can start Chrome in headless mode"""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")

        try:
            driver = webdriver.Chrome(options=options)
            driver.quit()
        except WebDriverException as e:
            self.fail(f"❌ Selenium failed to start ChromeDriver:\n{str(e)}\n\n"
                      f"➤ Check if your ChromeDriver matches your browser version.\n"
                      f"➤ Or use `webdriver-manager` as fallback.")