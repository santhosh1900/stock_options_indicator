import json
import os
from pathlib import Path
from datetime import datetime

DB_FILE = Path("app/db/auth.json")
TRADES_FILE = Path("app/db/trades.json")
DB_PATH = "app/db"


def save_auth(data):
    auth_data = {
        "access_token": data["access_token"],
        "user_id": data["user_id"],
        "user_name": data["user_name"],
        "login_time": datetime.now().isoformat(),
    }

    with open(DB_FILE, "w") as f:
        json.dump(auth_data, f, indent=4)


def get_auth():
    if not DB_FILE.exists():
        return {}

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_trade(trade):

    with open(TRADES_FILE, "r") as f:

        trades:list = json.load(f)

    trades.append(trade)

    with open(TRADES_FILE, "w") as f:

        json.dump(trades, f, indent=4)

def save_data_file_name(json_data, file_name):
    with open(f'{DB_PATH}/{file_name}.json', "w") as f:
        json.dump(json_data, f, indent=4)

    print(f"Saved historical data to {file_name}")

def get_data_by_file_name(file_name):
    file_path = f"{DB_PATH}/{file_name}.json"

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return json.load(f) or None
