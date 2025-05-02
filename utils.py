import re

def extract_p_segment(url):
    """
    URL'den -p- ile başlayan numarayı çeker. Örn: /product-p-12345
    """
    match = re.search(r'-p-\d+', str(url))
    return match.group() if match else None