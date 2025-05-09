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
    Verilen Trendyol URL'sinden domain ve path bilgilerini döner.
    
    Args:
        url (str): Kontrol edilecek Trendyol URL'si.

    Returns:
        tuple: (path, content_id)
            - path (str): URL'nin domain sonrası path bilgisi.
            - content_id (str or None): '-p-' ifadesinden sonraki içerik ID'si. Yoksa None döner.

    Örnek:
        Input: 'https://www.trendyol.com/product/abc-def-p-12345'
        Output: ('/product/abc-def-p-12345', '12345')
    """
    parsed = urlparse(url)
    if "trendyol.com" in parsed.netloc:
        path = parsed.path
        # Content ID'yi bulalım
        if "-p-" in path:
            try:
                content_id = path.split("-p-")[1].split("/")[0]
            except IndexError:
                content_id = None
        else:
            content_id = None
        return path, content_id
    return None, None

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
    
def logu_txt_olarak_kaydet(encrypted_log_file: str, save_path: str):
    """
    Şifreli log dosyasını çözerek .txt olarak belirtilen yere kaydeder.
    """
    key = anahtar_yukle()
    fernet = Fernet(key)

    with open(encrypted_log_file, "rb") as f:
        encrypted_data = f.read()

    decrypted = fernet.decrypt(encrypted_data)

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(decrypted.decode("utf-8"))
