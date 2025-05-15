# services/url_checker_with_selenium.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import psutil
import os 
from services.logger_service import log_and_print


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--enable-features=UseSkiaRenderer")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    options.page_load_strategy = "eager"
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def fetch_urls_with_driver(url_data_batch, total_count=0, start_index=0):
    log_and_print(f"🧪 Starting driver for batch of {len(url_data_batch)} URLs.")

    driver = create_driver()
    driver.set_page_load_timeout(15)

    results = []
    process = psutil.Process(os.getpid())

    for idx, (barcode, url) in enumerate(url_data_batch, start=start_index + 1):
        try:
            current_mem = process.memory_info().rss / (1024 * 1024)
            current_cpu = process.cpu_percent(interval=0.1)
            resolved_url = driver.current_url or url
            log_and_print(f"🔍 [{idx}/{total_count}] Checking barcode {barcode} - {url}")
            log_and_print(f"🧠 Memory: {current_mem:.2f} MB | CPU: {current_cpu:.1f}%")

            driver.get(url)
            time.sleep(0.15)
            resolved_url = driver.current_url
        except TimeoutException:
            log_and_print(f"⚠️ Timeout fetching URL for {barcode}: {url}", level="warning")
            resolved_url = url
        except Exception as e:
            log_and_print(f"❌ Error fetching URL for {barcode}: {e}", level="error")
            resolved_url = url
        results.append((barcode, url, resolved_url))

    driver.quit()
    log_and_print("🧹 Driver closed for this batch.")
    return results
