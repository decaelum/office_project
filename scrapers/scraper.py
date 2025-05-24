import os
import time
import math
import re
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from services.logger_service import log_and_print
from services.database_services import get_all_products
from urllib.parse import urlparse


def extract_product_id(url):
    try:
        path = urlparse(url).path
        product_id = path.split("-p-")[-1].strip("/")
        return product_id
    except Exception as e:
        log_and_print(f"❌ Error extracting product id from URL: {url} | {e}", level="error")
        return None


def get_chrome_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)


def scrape_page(page):
    base_url = "https://www.trendyol.com/sr?q=%25Farmasi&qt=%25Farmasi&st=%25Farmasi&os=1&pi="
    url = f"{base_url}{page}"
    scraped = set()
    driver = get_chrome_driver()
    driver.set_page_load_timeout(20)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        if "captcha" in driver.page_source.lower():
            log_and_print(f"🛑 CAPTCHA tespit edildi sayfa {page}'de. Skipping.", level="error")
            return scraped

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.p-card-chldrn-cntnr.card-border")))
        product_elements = driver.find_elements(By.CSS_SELECTOR, "a.p-card-chldrn-cntnr.card-border")

        for element in product_elements:
            href = element.get_attribute("href")
            log_and_print(f"🔎 Found href: {repr(href)}")

            if href is None:
                log_and_print("⚠️ Skipping: href is None", level="warning")
            elif "-p-" not in href:
                log_and_print(f"⚠️ Skipping: '-p-' not in href → {href}", level="warning")
            elif href in scraped:
                log_and_print(f"♻️ Duplicate URL skipped: {href}", level="info")
            else:
                scraped.add(href)
                log_and_print(f"✅ Added: {href}")

        log_and_print(f"📄 Page {page}: {len(product_elements)} elements, {len(scraped)} unique URLs.")
    except Exception as e:
        os.makedirs("results", exist_ok=True)
        driver.save_screenshot(f"results/page_{page}_error.png")
        with open(f"results/page_{page}_dump.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        log_and_print(f"❌ Error on page {page}: {e}", level="error")
    finally:
        driver.quit()
    return scraped


def scrape_farmasi_product_links(max_workers=3):
    base_url = "https://www.trendyol.com/sr?q=%25Farmasi&qt=%25Farmasi&st=%25Farmasi&os=1&pi=1"
    driver = get_chrome_driver()
    driver.get(base_url)
    wait = WebDriverWait(driver, 10)

    total_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dscrptn"))).text
    total_matches = re.findall(r"\d+", total_text.replace('.', ''))
    total_products = int(total_matches[-1]) if total_matches else 0
    max_pages = math.ceil(total_products / 24)
    log_and_print(f"📦 Total products: {total_products} | Total pages: {max_pages}")
    driver.quit()

    all_scraped = set()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(scrape_page, range(1, max_pages + 1))
        for page_results in results:
            all_scraped.update(page_results)

    log_and_print(f"🎯 Scraping completed. Final unique URL count: {len(all_scraped)}")
    return list(all_scraped)


def compare_scraped_links_with_db(db_name="data/products.db"):
    log_and_print("🔍 Scraping Trendyol for %Farmasi product links...")
    scraped_links = scrape_farmasi_product_links()
    log_and_print(f"🔢 Total scraped links: {len(scraped_links)}")

    if not scraped_links:
        log_and_print("❌ No links were scraped. Exiting compare process.", level="error")
        return None, None

    scraped_dict = {extract_product_id(url): url for url in scraped_links if extract_product_id(url)}
    db_products = get_all_products(db_name)
    db_dict = {
        barcode: {"name": name, "url": url, "product_id": extract_product_id(url)}
        for barcode, name, url, _ in db_products if extract_product_id(url)
    }

    new_products = []
    updated_urls = []

    for product_id, scraped_url in scraped_dict.items():
        found = False
        for barcode, info in db_dict.items():
            if info["product_id"] == product_id:
                found = True
                if info["url"] != scraped_url:
                    updated_urls.append({"Barcode": barcode, "Product Name": info["name"], "Old URL": info["url"], "New URL": scraped_url})
                break
        if not found:
            new_products.append({"Scraped URL": scraped_url})

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)

    new_path = f"results/new_farmasi_products_{timestamp}.xlsx"
    updated_path = f"results/updated_farmasi_urls_{timestamp}.xlsx"

    if new_products:
        pd.DataFrame(new_products).to_excel(new_path, index=False)
        log_and_print(f"📄 New products saved: {new_path}")
    else:
        log_and_print("✅ No new products found.")

    if updated_urls:
        pd.DataFrame(updated_urls).to_excel(updated_path, index=False)
        log_and_print(f"📄 Updated products saved: {updated_path}")
    else:
        log_and_print("✅ No URL changes found.")

    return new_path, updated_path
