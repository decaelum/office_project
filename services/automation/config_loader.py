import os
import json

def load_mail_config():
    """
    E-posta ayarlarını JSON dosyasından yükler.
    """
    # 📢 Kök dizine git
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(base_dir, "config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"⚠️ Config dosyası bulunamadı: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)