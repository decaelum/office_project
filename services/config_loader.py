import os
import json

def load_config(config_file: str = "config/config.json") -> dict:
    """
    Loads the full JSON configuration file.

    Args:
        config_file (str): Path to the JSON configuration file.

    Returns:
        dict: Configuration data as a dictionary.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found at: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_mail_config() -> dict:
    """
    Loads only the mail configuration section from the config file.

    Returns:
        dict: Mail configuration section.
    """
    config = load_config()
    if "mail" not in config:
        raise KeyError("Missing 'mail' section in config.json.")
    return config["mail"]