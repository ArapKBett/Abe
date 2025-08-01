import json
import logging
import os

def load_config():
    with open("config/config.json", "r") as f:
        return json.load(f)

def load_accounts():
    if os.path.exists("config/accounts.json"):
        with open("config/accounts.json", "r") as f:
            return json.load(f)
    return []

def save_accounts(accounts):
    with open("config/accounts.json", "w") as f:
        json.dump(accounts, f, indent=4)

def setup_logging(log_file, log_level):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
