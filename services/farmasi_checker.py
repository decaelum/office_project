import os
import pandas as pd
from datetime import datetime
from scrapers.scraper import scrape_farmasi_product_links
from services.logger_service import log_and_print
from services.database_services import get_all_products
from scrapers.scraper import scrape_farmasi_product_links
from urllib.parse import urlparse


def extract_product_id(url):
    try:
        path = urlparse(url).path
        return path.split("-p-")[-1].strip("/")
    except Exception as e:
        log_and_print(f"❌ Error extracting product id from URL: {url} | {e}", level="error")
        return None


def check_farmasi_products(db_name="data/products.db"):
    log_and_print("🔍 Scraping %Farmasi product links from Trendyol...")
    trendyol_links = scrape_farmasi_product_links()
    log_and_print(f"🔢 Found {len(trendyol_links)} product links from Trendyol.")

    db_products = get_all_products(db_name)
    db_dict = {barcode: url for barcode, _, url, _ in db_products}

    new_entries = []
    updated_entries = []

    for barcode, trendyol_url in trendyol_links:
        trendyol_pid = extract_product_id(trendyol_url)
        if barcode in db_dict:
            db_pid = extract_product_id(db_dict[barcode])
            if trendyol_pid != db_pid:
                updated_entries.append({
                    "Barcode": barcode,
                    "Old URL": db_dict[barcode],
                    "New URL": trendyol_url,
                    "Product ID Changed": True
                })
        else:
            new_entries.append({
                "Barcode": barcode,
                "New URL": trendyol_url
            })

    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("results", exist_ok=True)

    new_file = f"results/farmasi_new_products_{timestamp}.xlsx"
    update_file = f"results/farmasi_updated_urls_{timestamp}.xlsx"

    if new_entries:
        pd.DataFrame(new_entries).to_excel(new_file, index=False)
        log_and_print(f"🆕 New products report saved: {new_file}")

    if updated_entries:
        pd.DataFrame(updated_entries).to_excel(update_file, index=False)
        log_and_print(f"♻️ Updated URLs report saved: {update_file}")

    return new_file if new_entries else None, update_file if updated_entries else None

def compare_scraped_links_with_db(db_name="data/products.db"):
    try:
        log_and_print("🔍 Scraping Trendyol for %Farmasi product links...")
        scraped_links = scrape_farmasi_product_links()

        if not scraped_links:
            log_and_print("❌ No links were scraped. Exiting compare process.", level="error")
            return "", ""

        scraped_dict = {extract_product_id(url): url for url in scraped_links if extract_product_id(url)}

        log_and_print("📦 Fetching products from database...")
        db_products = get_all_products(db_name)
        db_dict = {
            barcode: {
                "name": name,
                "url": url,
                "product_id": extract_product_id(url)
            }
            for barcode, name, url, _ in db_products if extract_product_id(url)
        }

        new_products = []
        updated_urls = []

        for product_id, url in scraped_dict.items():
            found = False
            for barcode, info in db_dict.items():
                if info["product_id"] == product_id:
                    found = True
                    if info["url"] != url:
                        updated_urls.append({
                            "Barcode": barcode,
                            "Product Name": info["name"],
                            "Old URL": info["url"],
                            "New URL": url
                        })
                    break
            if not found:
                new_products.append({"Scraped URL": url})

        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs("results", exist_ok=True)

        new_report_path = f"results/new_farmasi_products_{timestamp}.xlsx"
        updated_report_path = f"results/updated_farmasi_urls_{timestamp}.xlsx"

        if new_products:
            pd.DataFrame(new_products).to_excel(new_report_path, index=False)
            log_and_print(f"📄 New products report saved: {new_report_path}")
        else:
            new_report_path = ""
            log_and_print("✅ No new products found.")

        if updated_urls:
            pd.DataFrame(updated_urls).to_excel(updated_report_path, index=False)
            log_and_print(f"📄 Updated URL report saved: {updated_report_path}")
        else:
            updated_report_path = ""
            log_and_print("✅ No URL changes found.")

        return new_report_path, updated_report_path

    except Exception as e:
        log_and_print(f"❌ Farmasi kontrol hatası: {e}", level="error")
        return "", ""