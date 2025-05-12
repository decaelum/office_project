import pandas as pd
import os
from typing import List
from core.db_manager import DatabaseManager
from core.log_manager import log_message
from datetime import datetime

REQUIRED_COLUMNS = ["barcode", "product_name", "url", "last_control"]

def read_excel_file(file_path: str) -> pd.DataFrame:
    """
    Reads an Excel file and filters required columns.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        pd.DataFrame: Filtered DataFrame with required columns.
    """
    if not os.path.exists(file_path):
        log_message(f"File not found: {file_path}", level="error")
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path)
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

        if missing_columns:
            log_message(f"Missing columns in {file_path}: {missing_columns}", level="warning")
            return pd.DataFrame()

        filtered_df = df[REQUIRED_COLUMNS].dropna()
        return filtered_df

    except Exception as e:
        log_message(f"Error reading Excel file {file_path}: {e}", level="error")
        return pd.DataFrame()


def process_and_save_files(file_paths: List[str], db_name: str = "products.db"):
    """
    Processes multiple Excel files and saves valid data to the database.

    Args:
        file_paths (List[str]): List of Excel file paths.
        db_name (str): Name of the database file.
    """
    combined_df = pd.DataFrame()

    for path in file_paths:
        df = read_excel_file(path)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    if combined_df.empty:
        log_message("No valid data found to save.", level="warning")
        return

    with DatabaseManager(db_name) as db:
        for _, row in combined_df.iterrows():
            try:
                db.insert_record(
                    table="products",
                    columns=REQUIRED_COLUMNS,
                    values=[row["barcode"], row["product_name"], row["url"], row["last_control"]]
                )
            except Exception as e:
                log_message(f"Failed to insert record for barcode {row['barcode']}: {e}", level="error")

    log_message(f"Processed and saved data from {len(file_paths)} files successfully.")


def save_results_to_excel(results: List[dict], operation_name: str, output_dir: str = "results/"):
    """
    Saves the results of URL comparison into an Excel file.

    Args:
        results (List[dict]): List of results with keys: 'barcode', 'new_url', 'prefix_changed', 'content_id_changed'.
        operation_name (str): Name of the operation provided by the user.
        output_dir (str): Directory to save the result file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{timestamp}-{operation_name}.xlsx"
    file_path = os.path.join(output_dir, file_name)

    df = pd.DataFrame(results)
    df.to_excel(file_path, index=False)

    log_message(f"Results saved to: {file_path}")
    print(f"✅ Results saved to: {file_path}")