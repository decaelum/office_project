import logging
import os
from datetime import datetime
from cryptography.fernet import Fernet

# Constants
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app_logs.log")
ENCRYPTED_LOG_FILE = os.path.join(LOG_DIR, "log.enc")
KEY_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "keys", "log_key.key")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Logging configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_message(message: str, level: str = "info") -> None:
    """
    Logs a message to the log file with the specified level.

    :param message: Message to log.
    :param level: Logging level ('info', 'warning', 'error', 'debug').
    """
    level = level.lower()
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
    else:
        logging.info(message)  # Default to info if unknown level

def generate_encryption_key(key_path: str = KEY_FILE_PATH) -> None:
    """
    Generates and saves an encryption key if it does not already exist.

    :param key_path: Path to save the encryption key.
    """
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)

def encrypt_log_file(key_path: str = KEY_FILE_PATH, log_file: str = LOG_FILE, encrypted_file: str = ENCRYPTED_LOG_FILE) -> None:
    """
    Encrypts the plain text log file and saves it as an encrypted file.

    :param key_path: Path to the encryption key.
    :param log_file: Path to the plain text log file.
    :param encrypted_file: Path to save the encrypted log file.
    """
    with open(key_path, "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)

    with open(log_file, "rb") as log_f:
        plain_data = log_f.read()

    encrypted_data = cipher.encrypt(plain_data)

    with open(encrypted_file, "wb") as enc_file:
        enc_file.write(encrypted_data)

def decrypt_log_file(key_path: str = KEY_FILE_PATH, encrypted_file: str = ENCRYPTED_LOG_FILE) -> str:
    """
    Decrypts the encrypted log file and returns its content.

    :param key_path: Path to the encryption key.
    :param encrypted_file: Path to the encrypted log file.
    :return: Decrypted log content as a string.
    """
    with open(key_path, "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)

    with open(encrypted_file, "rb") as enc_file:
        encrypted_data = enc_file.read()

    try:
        return cipher.decrypt(encrypted_data).decode("utf-8")
    except Exception as e:
        return f"⚠️ Failed to decrypt log: {e}"

def save_decrypted_log_as_txt(output_path: str, key_path: str = KEY_FILE_PATH, encrypted_file: str = ENCRYPTED_LOG_FILE) -> None:
    """
    Decrypts the encrypted log file and saves it as a plain text file.

    :param output_path: Path to save the decrypted text file.
    :param key_path: Path to the encryption key.
    :param encrypted_file: Path to the encrypted log file.
    """
    decrypted_content = decrypt_log_file(key_path, encrypted_file)
    with open(output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(decrypted_content)