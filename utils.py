import re
import os 
from cryptography.fernet import Fernet
from urllib.parse import urlparse




def anahtar_olustur(kayit_yolu="log_key.key"):
    if not os.path.exists(kayit_yolu):
        key = Fernet.generate_key()
        with open(kayit_yolu, "wb") as f:
            f.write(key)

def extract_netloc_and_path_from_trendyol(url):
    """
    Verilen Trendyol URL'sinden sadece domain sonrası path'i (örnek: /product/abc-def-p-12345) döner.
    'https://www.trendyol.com' kısmı çıkarılır, kalan yol karşılaştırılır.
    """
    parsed = urlparse(url)
    if "trendyol.com" in parsed.netloc:
        return parsed.path
    else:
        return None

def logu_sifrele(veri: str, key_path="log_key.key", log_dosya_adi="log.enc"):
    with open(key_path, "rb") as f:
        key = f.read()
    cipher = Fernet(key)
    sifreli = cipher.encrypt(veri.encode("utf-8"))
    
    with open(log_dosya_adi, "wb") as f:
        f.write(sifreli)

def logu_coz(key_path="log_key.key", log_dosya_adi="log.enc") -> str:
    with open(key_path, "rb") as f:
        key = f.read()
    cipher = Fernet(key)

    with open(log_dosya_adi, "rb") as f:
        sifreli_veri = f.read()

    try:
        return cipher.decrypt(sifreli_veri).decode("utf-8")
    except Exception as e:
        return f"⚠️ Deşifre edilemedi: {e}"
    
