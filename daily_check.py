import json
import os
import requests
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "chores_config.json")


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


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

    for chore_id, chore in chores.items():
        current_user_index = chore["assigned_user_index"]
        last_done_str = chore.get("last_completed_date", "")

        reminder_config = chore.get("reminder_days", 1)

        if isinstance(reminder_config, list):
            reminder_days = reminder_config[current_user_index]
        else:
            reminder_days = reminder_config

        needs_reminder = False

        if not last_done_str:
            # If it has never been done, it immediately needs a reminder
            needs_reminder = True
        else:
            last_done_date = datetime.strptime(last_done_str, "%Y-%m-%d").date()
            days_since = (logical_date - last_done_date).days

            if days_since >= reminder_days:
                needs_reminder = True

        if needs_reminder:
            current_user = users[current_user_index]
            chore_tag = chore.get("emoji_tag", "tada")
            tags = f"rotating_light,{chore_tag}"
            msg = f"You still need to {chore['title'].lower()}!"
            send_ntfy(
                current_user["ntfy_topic_personal"],
                msg,
                title=f"Reminder {current_user['name']}",
                priority="high",
                tags=tags,
            )


if __name__ == "__main__":
    process_daily_chores()
