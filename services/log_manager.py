import os
import json
from datetime import datetime
from cryptography.fernet import Fernet

CONFIG_PATH = "log_config.json"
KEY_PATH = "key.key"

def get_log_directory_from_config():
    """Log klasörünü config dosyasından alır."""
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"log_root": ""}, f)
        return None

    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config.get("log_root")
    except Exception as e:
        print(f"⚠️ config okunamadı: {e}")
        return None

def set_log_directory(path: str):
    """Admin log klasörü seçtiğinde kaydeder."""
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"log_root": path}, f)
        print(f"📁 Log klasörü ayarlandı: {path}")
        return True
    except Exception as e:
        print(f"⚠️ Log klasörü ayarlanamadı: {e}")
        return False

def anahtar_olustur():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)

def anahtar_yukle():
    with open(KEY_PATH, "rb") as f:
        return f.read()

def logu_olustur(islem_adi: str) -> str:
    """
    Log klasöründe işlem adı ve tarih ile dosya oluşturur.
    """
    log_root = get_log_directory_from_config()

    if not log_root or not os.path.isdir(log_root):
        print("❌ Log klasörü bulunamadı. Lütfen admin'e danışın.")
        return None

    tarih_saat = datetime.now().strftime("%d-%m-%Y-%H.%M")
    dosya_adi = f"{tarih_saat}-{islem_adi}.log"
    log_yolu = os.path.join(log_root, dosya_adi)

    try:
        with open(log_yolu, "w", encoding="utf-8") as f:
            f.write(f"🔹 Log oluşturuldu: {tarih_saat}\n")
        return log_yolu
    except Exception as e:
        print(f"❌ Log dosyası oluşturulamadı: {e}")
        return None

def log_yaz(log_dosya: str, mesaj: str):
    try:
        with open(log_dosya, "a", encoding="utf-8") as f:
            f.write(mesaj + "\n")
    except Exception as e:
        print(f"❌ Log yazma hatası: {e}")

def logu_sifrele(log_dosya: str):
    try:
        anahtar_olustur()
        key = anahtar_yukle()
        fernet = Fernet(key)

        with open(log_dosya, "rb") as f:
            veri = f.read()

        sifreli = fernet.encrypt(veri)
        sifreli_yol = log_dosya + ".enc"

        with open(sifreli_yol, "wb") as f:
            f.write(sifreli)

        os.remove(log_dosya)
    except Exception as e:
        print(f"❌ Log şifreleme hatası: {e}")

def logu_coz(log_dosya: str) -> str:
    try:
        key = anahtar_yukle()
        fernet = Fernet(key)

        with open(log_dosya, "rb") as f:
            sifreli = f.read()

        cozulmus = fernet.decrypt(sifreli)
        return cozulmus.decode("utf-8")
    except Exception as e:
        return f"❌ Log çözülemedi: {e}"