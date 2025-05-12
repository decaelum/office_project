import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.log_manager import log_message  

def check_single_url(url):
    try:
        response = requests.get(url, timeout=5)
        log_message(f"{url} -> {response.status_code}")
        return url, response.status_code
    except requests.RequestException as e:
        log_message(f"{url} -> FAILED ({str(e)})")
        return url, None

def check_urls_parallel(url_list, max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_single_url, url): url for url in url_list}
        for future in as_completed(future_to_url):
            url, status = future.result()
            results.append((url, status))
    return results