import json
import os

def load_mail_config(config_path='config/mail_config.json'):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Mail config file not found at: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)