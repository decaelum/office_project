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

def log_and_print(message, level="info"):
    """
    Logs the message to the log file and prints it to the terminal.

    Args:
        message (str): The message to log and print.
        level (str): Log level (info, warning, error, debug).
    """
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
    else:
        logging.info(message)  # Default olarak info kullan