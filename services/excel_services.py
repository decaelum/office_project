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


def save_results_to_excel(data, operation_name):
    from pandas import DataFrame
    from datetime import datetime

    if not os.path.exists("results"):
        os.makedirs("results")

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"results/{timestamp}-{operation_name}.xlsx"
    df = DataFrame(data)
    df.to_excel(filename, index=False)

    return filename  # önemli: geri döndür!