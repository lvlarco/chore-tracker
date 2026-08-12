import json
import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "chores_config.json")


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def send_ntfy(topic, message):
    try:
        requests.post(
            f"https://ntfy.sh/{topic}", data=message.encode("utf-8"), timeout=5
        )
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}")


def process_daily_chores():
    if not os.path.exists(CONFIG_FILE):
        return

    config = load_config()
    chores = config.get("chores", {})
    users = config.get("users", [])
    topic = config.get("ntfy_topic")

    if not users or not topic:
        return

    for chore_id, chore in chores.items():
        current_user_index = chore["assigned_user_index"]

        if chore["completed_today"]:
            # Rotate user
            next_user_index = (current_user_index + 1) % len(users)
            chore["assigned_user_index"] = next_user_index
            chore["completed_today"] = False

            # GET THE NEXT USER'S PERSONAL TOPIC
            next_user = users[next_user_index]
            msg = f"{next_user['name']}, it's your turn for {chore['title']} today."
            send_ntfy(next_user["ntfy_topic_personal"], msg)

        else:
            current_user = users[current_user_index]
            msg = f"Reminder {current_user['name']}, you didn't do {chore['title']} yesterday. " \
                  f"It is still your turn today!"

            # You can add ntfy headers to make nagging notifications high priority!
            requests.post(
                f"https://ntfy.sh/{current_user['ntfy_topic_personal']}",
                data=msg.encode("utf-8"),
                headers={"Priority": "high", "Tags": "warning,rotating_light"},
            )

    save_config(config)


if __name__ == "__main__":
    process_daily_chores()
