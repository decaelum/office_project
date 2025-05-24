from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
from services.logger_service import log_and_print

def scrape_farmasi_product_links(max_pages=50):
    options = Options()
    options.add_argument("--headless=new")  # Daha stabil headless
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    base_url = "https://www.trendyol.com/sr?q=%25Farmasi&qt=%25Farmasi&st=%25Farmasi&os=1&pi="
    scraped_urls = set()

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}{page}"
            try:
                driver.get(url)
                time.sleep(2)

                # 📸 Sayfanın ekran görüntüsünü al
                os.makedirs("results", exist_ok=True)
                screenshot_path = f"results/page_{page}_screenshot.png"
                driver.save_screenshot(screenshot_path)
                log_and_print(f"📸 Screenshot saved: {screenshot_path}")

                product_elements = driver.find_elements(By.CSS_SELECTOR, "a.p-card-chldrn-cntnr.card-border")
                if not product_elements:
                    log_and_print(f"⛔ No products found on page {page}. Ending scrape.")
                    break

                for element in product_elements:
                    href = element.get_attribute("href")
                    if href and "/p-" in href:
                        scraped_urls.add(href)

                log_and_print(f"✅ Page {page}: {len(product_elements)} product links found.")

            except Exception as e:
                log_and_print(f"❌ Error on page {page}: {e}", level="error")

    except Exception as e:
        log_and_print(f"❌ Scraper crashed: {e}", level="error")

    finally:
        driver.quit()

    log_and_print(f"🧹 Scraping completed. Total unique URLs: {len(scraped_urls)}")
    return list(scraped_urls)