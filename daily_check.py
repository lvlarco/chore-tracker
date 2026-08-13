import json
import os
import requests
from datetime import datetime, timedelta


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "chores_config.json")


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def send_ntfy(topic, message, title=None, priority=None, tags=None):
    headers = {}
    if title:
        headers["Title"] = title
    if priority:
        headers["Priority"] = priority
    if tags:
        headers["Tags"] = tags

    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers=headers if headers else None,
            timeout=5,
        )
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}")


def process_daily_chores():
    if not os.path.exists(CONFIG_FILE):
        return

    config = load_config()
    chores = config.get("chores", {})
    users = config.get("users", [])

    if not users:
        return

    logical_date = (datetime.now() - timedelta(hours=4)).date()
    today_str = str(logical_date)

    for chore_id, chore in chores.items():
        current_user_index = chore["assigned_user_index"]
        last_done = chore.get("last_completed_date", "")

        if last_done != today_str:
            current_user = users[current_user_index]
            msg = (
                f"Reminder {current_user['name']}, you didn't {chore['title'].lower()}! "
                f"It is still your turn."
            )
            send_ntfy(
                current_user["ntfy_topic_personal"],
                msg,
                priority="high",
                tags="warning,rotating_light",
            )

    save_config(config)


if __name__ == "__main__":
    process_daily_chores()
