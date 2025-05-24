import pandas as pd
import os
from datetime import datetime
from services.database_services import normalize_barcode, clean_string
from services.logger_service import log_and_print
from core.db_manager import DatabaseManager

REQUIRED_COLUMNS = ["barcode", "product_name", "url"]

def read_excel_file(file_path: str) -> pd.DataFrame:
    """Reads and normalizes data from the Excel file."""
    if not os.path.exists(file_path):
        log_and_print(f"❌ File not found: {file_path}", level="error")
        return pd.DataFrame()

    df = pd.read_excel(file_path, dtype=str)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        log_and_print(f"❌ Missing required columns: {missing_cols}", level="error")
        return pd.DataFrame()

    df = df[REQUIRED_COLUMNS].copy()
    df.dropna(subset=REQUIRED_COLUMNS, inplace=True)
    df["barcode"] = df["barcode"].apply(normalize_barcode)
    return df

def process_and_save_files(file_paths: list[str], db_name: str = "data/products.db"):
    """Processes multiple Excel files and logs successful imports."""
    from services.database_services import insert_or_update_product

    for file_path in file_paths:
        log_and_print(f"📄 Processing file: {file_path}")
        df = read_excel_file(file_path)
        if df.empty:
            continue

        for _, row in df.iterrows():
            insert_or_update_product(
                barcode=row["barcode"],
                product_name=row["product_name"],
                url=row["url"],
                db_name=db_name
            )
        log_and_print(f"✅ Completed import: {file_path}")

def update_products_from_excel(excel_file_path: str, db_name: str = "data/products.db") -> str:
    df = read_excel_file(excel_file_path)
    if df.empty:
        return ""

    updated_records = []
    inserted_records = []

    with DatabaseManager(db_name) as db:
        for _, row in df.iterrows():
            barcode = normalize_barcode(row["barcode"])
            new_product_name = clean_string(row["product_name"])
            new_url = clean_string(row["url"])

            current_data = db.fetch_query("SELECT product_name, url FROM products WHERE barcode = ?", (barcode,))
            if current_data:
                current_name, current_url = current_data[0]
                if clean_string(current_name) != new_product_name or clean_string(current_url) != new_url:
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
                    updated_records.append(barcode)
                    log_and_print(f"✅ Updated Barcode: {barcode}")
                else:
                    log_and_print(f"✔️ No change for Barcode: {barcode}")
            else:
                db.insert_record(
                    table="products",
                    columns=["barcode", "product_name", "url", "last_control"],
                    values=[barcode, new_product_name, new_url, datetime.now().strftime('%Y-%m-%d')]
                )
                inserted_records.append(barcode)
                log_and_print(f"➕ Inserted new Barcode: {barcode}")

    if updated_records:
        report_df = pd.DataFrame({"Updated Barcodes": updated_records})
        report_path = f"results/update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        report_df.to_excel(report_path, index=False)
        log_and_print(f"📄 Report saved: {report_path}")
        return report_path

    log_and_print("📭 No updates needed.")
    return ""
