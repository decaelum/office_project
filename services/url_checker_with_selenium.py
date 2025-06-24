import os
import time
import psutil
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from services.logger_service import log_and_print
from scrapers.scraper import extract_product_id  # 🔁 product_id için yardımcı fonksiyon

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.page_load_strategy = 'eager'
    return webdriver.Chrome(options=options)

def _resolve_url(barcode, url, idx, total):
    process = psutil.Process(os.getpid())
    driver = None
    try:
        driver = create_driver()
        driver.set_page_load_timeout(15)

        log_and_print(f"🔍 [{idx}/{total}] Checking barcode: {barcode} | URL: {url}")

        # Sistem kaynaklarını logla
        current_mem = process.memory_info().rss / (1024 * 1024)
        current_cpu = process.cpu_percent(interval=0.1)
        log_and_print(f"🧠 Memory: {current_mem:.2f} MB | CPU: {current_cpu:.1f}%")

        driver.get(url)
        time.sleep(0.2)
        resolved_url = driver.current_url or url

        # Ürün ismini çekmeye çalış
        try:
            wait = WebDriverWait(driver, 5)
            name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.pr-new-br")))
            product_name = name_element.text.strip()
        except Exception:
            product_name = None
            log_and_print(f"⚠️ Ürün ismi alınamadı: {resolved_url}", level="warning")

        product_id = extract_product_id(resolved_url)

        return (barcode, url, resolved_url, product_id, product_name)

    except TimeoutException:
        log_and_print(f"⚠️ Timeout fetching URL for barcode {barcode}: {url}", level="warning")
        return (barcode, url, url, None, None)
    except WebDriverException as e:
        log_and_print(f"❌ WebDriver error for barcode {barcode}: {e}", level="error")
        return (barcode, url, url, None, None)
    except Exception as e:
        log_and_print(f"❌ Unknown error for barcode {barcode}: {e}", level="error")
        return (barcode, url, url, None, None)
    finally:
        if driver:
            driver.quit()

def fetch_urls_with_driver(url_data_batch, total_count=0, start_index=0, max_workers=3):
    log_and_print(f"🧪 Starting parallel URL check for {len(url_data_batch)} items with {max_workers} workers...")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_resolve_url, barcode, url, idx, total_count)
            for idx, (barcode, url) in enumerate(url_data_batch, start=start_index + 1)
        ]
        for future in futures:
            results.append(future.result())

    log_and_print("🧹 All drivers finished. Batch complete.")
    return results