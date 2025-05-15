import logging
import os

# Log dosyasının konumu ve ismi
LOG_DIR = "logs"
LOG_FILE = "automation.log"

# Log dizini yoksa oluştur
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logging ayarları
logging.basicConfig(
    filename=os.path.join(LOG_DIR, LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def log_and_print(message: str, level="info"):
    print(message, flush=True)  # Force print to immediately flush to stdout
    logger = logging.getLogger("app")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
    getattr(logger, level)(message)