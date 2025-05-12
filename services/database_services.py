import pandas as pd
from core.db_manager import DatabaseManager
from datetime import datetime
from services.logger_service import log_and_print

def get_all_products(db_name: str = "products.db"):
    """
    Fetches all products from the database.

    Returns:
        list of tuples: Each tuple contains (barcode, product_name, url, last_control)
    """
    with DatabaseManager(db_name) as db:

        return db.fetch_query("SELECT barcode, product_name, url, last_control FROM products")
def update_products_from_excel(excel_file_path: str, db_name: str = "data/products.db") -> str:
    df = pd.read_excel(excel_file_path)
    required_columns = ["Barcode", "Product Name", "URL"]

    # Gerekli kolonlar kontrolü
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Excel dosyasında gerekli kolonlar eksik. Gereken: Barcode, Product Name, URL")

    updated_records = []

    with DatabaseManager(db_name) as db:
        for _, row in df.iterrows():
            barcode = str(row["Barcode"]).strip()
            new_product_name = str(row["Product Name"]).strip()
            new_url = str(row["URL"]).strip()

            current_data = db.fetch_query(
                "SELECT product_name, url FROM products WHERE barcode = ?", (barcode,)
            )

            if current_data:
                current_name, current_url = current_data[0]
                if current_name != new_product_name or current_url != new_url:
                    # Güncelleme yapılıyor
                    db.update_record(
                        table="products",
                        update_fields={
                            "product_name": new_product_name,
                            "url": new_url,
                            "last_control": datetime.now().strftime('%Y-%m-%d')
                        },
                        condition="barcode = ?",
                        condition_values=(barcode,)
                    )
                    updated_records.append({
                        "Barcode": barcode,
                        "Old Product Name": current_name,
                        "New Product Name": new_product_name,
                        "Old URL": current_url,
                        "New URL": new_url,
                        "Update Date": datetime.now().strftime('%Y-%m-%d')
                    })
                    log_and_print(f"✅ Updated Barcode: {barcode}")
            else:
                log_and_print(f"⚠️ Barcode not found in DB: {barcode}")

    # Güncellenen kayıtlar raporlanıyor
    if updated_records:
        report_df = pd.DataFrame(updated_records)
        report_path = f"results/update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        report_df.to_excel(report_path, index=False)
        log_and_print(f"📄 Update report generated: {report_path}")
        return report_path

    log_and_print("📭 No records updated.")
    return ""