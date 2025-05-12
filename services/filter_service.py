import pandas as pd
from typing import Optional, List

def filter_by_barcode(df: pd.DataFrame, barcode: str) -> pd.DataFrame:
    """Filters DataFrame by exact barcode match."""
    return df[df["barcode"] == barcode]

def filter_by_product_name(df: pd.DataFrame, keyword: str, match_type: str = "contains") -> pd.DataFrame:
    """
    Filters DataFrame by product name.

    Args:
        match_type (str): Options are 'contains', 'startswith', 'endswith'.
    """
    if match_type == "contains":
        return df[df["product_name"].str.contains(keyword, case=False, na=False)]
    elif match_type == "startswith":
        return df[df["product_name"].str.startswith(keyword, na=False)]
    elif match_type == "endswith":
        return df[df["product_name"].str.endswith(keyword, na=False)]
    return df

def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """Filters DataFrame by last_control date range. Dates must be 'YYYY-MM-DD' format."""
    df["last_control"] = pd.to_datetime(df["last_control"], errors='coerce')
    return df[(df["last_control"] >= start_date) & (df["last_control"] <= end_date)]

def filter_by_url_change(df: pd.DataFrame, check_p_section: bool = True) -> pd.DataFrame:
    """
    Filters rows based on URL changes before or after '-p-'.

    Args:
        check_p_section (bool): 
            - True: Check if content ID after '-p-' has changed.
            - False: Check if prefix before '-p-' has changed.
    """
    def check_change(row):
        old_url = row.get("url", "")
        new_url = row.get("new_url", "")
        if "-p-" in old_url and "-p-" in new_url:
            old_prefix, old_suffix = old_url.split("-p-", 1)
            new_prefix, new_suffix = new_url.split("-p-", 1)

            if check_p_section:
                try:
                    old_content_id = old_suffix.split("/")[0]
                    new_content_id = new_suffix.split("/")[0]
                    return old_content_id != new_content_id
                except IndexError:
                    return False
            else:
                return old_prefix != new_prefix
        return False

    return df[df.apply(check_change, axis=1)]

def drop_missing_data(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Drops rows with missing values in specified columns."""
    return df.dropna(subset=columns) if columns else df.dropna()

def apply_multiple_filters(df: pd.DataFrame, filters: List[dict]) -> pd.DataFrame:
    """
    Applies multiple filters to the DataFrame.

    Args:
        filters (List[dict]): List of filters. Each filter dict should have:
            - 'type': filter function name as string
            - 'params': dictionary of parameters for that function

    Example:
        filters = [
            {"type": "filter_by_barcode", "params": {"barcode": "123456789"}},
            {"type": "filter_by_product_name", "params": {"keyword": "Coffee", "match_type": "contains"}},
        ]
    """
    for filter_def in filters:
        filter_func = globals().get(filter_def["type"])
        if callable(filter_func):
            df = filter_func(df, **filter_def.get("params", {}))
    return df