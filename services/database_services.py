
import pandas as pd
from core.db_manager import DatabaseManager
from datetime import datetime
from services.logger_service import log_and_print
import unicodedata

def ensure_products_table_exists(db_name="data/products.db"):
    create_table_query = (
        """
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            product_name TEXT,
            url TEXT,
            last_control TEXT
        );
        """
    )
    with DatabaseManager(db_name) as db:
        db.execute_query(create_table_query)

def get_all_products(db_name: str = "products.db"):
    with DatabaseManager(db_name) as db:
        return db.fetch_query("SELECT barcode, product_name, url, last_control FROM products")

def clean_string(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFKD", s)
    return s.strip().lower().replace("\n", "").replace("\r", "")

def normalize_barcode(barcode: str) -> str:
    try:
        cleaned = str(int(float(barcode)))
        return cleaned.strip()
    except Exception:
        return barcode.strip()

def insert_or_update_product(barcode, product_name, url, db_name="data/products.db"):
    barcode = normalize_barcode(barcode)
    product_name = clean_string(product_name)
    url = clean_string(url)

    with DatabaseManager(db_name) as db:
        existing = db.fetch_query("SELECT * FROM products WHERE barcode = ?", (barcode,))
        if existing:
            db.execute_query(
                "UPDATE products SET product_name = ?, url = ?, last_control = ? WHERE barcode = ?",
                (product_name, url, datetime.now().isoformat(), barcode)
            )
            log_and_print(f"Updated barcode: {barcode}")
        else:
            db.execute_query(
                "INSERT INTO products (barcode, product_name, url, last_control) VALUES (?, ?, ?, ?)",
                (barcode, product_name, url, datetime.now().isoformat())
            )
            log_and_print(f"Inserted new barcode: {barcode}")


def update_url_if_changed(barcode: str, new_url: str, db_name: str = "data/products.db"):
    """
    Ürünün URL'si değişmişse günceller ve last_control tarihini kaydeder.
    """
    with DatabaseManager(db_name) as db:
        result = db.fetch_query("SELECT url FROM products WHERE barcode = ?", (barcode,))
        if result:
            old_url = result[0][0]
            if old_url != new_url:
                db.update_record(
                    table="products",
                    update_fields={
                        "url": new_url,
                        "last_control": datetime.now().strftime('%Y-%m-%d')
                    },
                    condition="barcode = ?",
                    condition_values=(barcode,)
                )
                log_and_print(f"🔁 URL updated for barcode {barcode}")
        else:
            log_and_print(f"⚠️ Barcode not found while updating URL: {barcode}", level="warning")