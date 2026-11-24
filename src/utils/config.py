import os
import json

CONFIG_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_DATA_DIR = os.path.join(CONFIG_DIR, "data")

DEFAULT_CONFIG = {
    "db_type": "mysql",  # "mysql" or "sqlite"
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "inventory_db"
    },
    "sqlite": {
        "file_path": os.path.join(DEFAULT_DATA_DIR, "inventory.db")
    },
    "currency_symbol": "₹",
    "default_low_stock_threshold": 5,
    "company_name": "School Store / Inventory Central",
    "theme": "modern"
}


def load_config() -> dict:
    """Load configuration from config.json or create default if not present."""
    if not os.path.exists(DEFAULT_DATA_DIR):
        try:
            os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)
        except OSError:
            pass

    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with default config to ensure all keys exist
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            if "mysql" in data:
                merged["mysql"] = {**DEFAULT_CONFIG["mysql"], **data["mysql"]}
            if "sqlite" in data:
                merged["sqlite"] = {**DEFAULT_CONFIG["sqlite"], **data["sqlite"]}
            return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config_dict: dict) -> bool:
    """Save configuration to config.json."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
