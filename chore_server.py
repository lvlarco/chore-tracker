import json
import os
import requests
from datetime import datetime, timedelta
from flask import (
    Flask,
    request,
    make_response,
    redirect,
    url_for,
    render_template_string,
)

app = Flask(__name__)

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


@app.route("/setup", methods=["GET", "POST"])
def setup():
    config = load_config()
    users = config.get("users", [])

    if request.method == "POST":
        selected_index = request.form.get("user_index")
        resp = make_response(
            "<h1>Phone registered! You can close this and scan tags normally now.</h1>"
        )
        resp.set_cookie("user_index", selected_index, max_age=60 * 60 * 24 * 365 * 10)
        return resp

    html = """
    <div style="font-family: sans-serif; padding: 20px;">
        <h2>One-Time Setup</h2>
        <p>Who does this phone belong to?</p>
        <form method="POST">
            <select name="user_index" style="font-size: 18px; padding: 10px;">
                {% for i in range(users|length) %}
                    <option value="{{ i }}">{{ users[i].name }}</option>
                {% endfor %}
            </select><br><br>
            <button type="submit" style="font-size: 18px; padding: 10px 20px;">Save My Phone</button>
        </form>
    </div>
    
    
    """
    return render_template_string(html, users=users)


@app.route("/done/<chore_id>")
def mark_done(chore_id):
    if not os.path.exists(CONFIG_FILE):
        return "<h1>Configuration file missing.</h1>", 500

    # 1. Read the cookie
    user_cookie = request.cookies.get("user_index")
    if user_cookie is None:
        return redirect(url_for("setup"))

    config = load_config()
    chores = config.get("chores", {})
    users = config.get("users", [])

    if chore_id not in chores:
        return f"<h1>Chore '{chore_id}' not found.</h1>", 404

    chore = chores[chore_id]
    logical_date = (datetime.now() - timedelta(hours=4)).date()
    today_str = str(logical_date)

    # 2. Identify who is scanning vs. who is assigned
    actual_user_index = int(user_cookie)
    actual_user_name = users[actual_user_index]["name"]

    assigned_user_index = chore["assigned_user_index"]
    assigned_user_name = users[assigned_user_index]["name"]

    # 3. STRICT CHECK: Prevent the wrong person from logging it
    if actual_user_index != assigned_user_index:
        return (
            f"<h1>It isn't your turn {actual_user_name}! "
            f"It is {assigned_user_name}'s turn to {chore['title'].lower()}.</h1>",
            403,
        )

    # 4. Check if completed today
    if chore.get("last_completed_date") == today_str:
        return "<h1>Chore already logged today!</h1>", 200

    # 5. Log completion & rotate assignment to the next person
    chore["last_completed_date"] = today_str
    chore["assigned_user_index"] = (assigned_user_index + 1) % len(users)
    save_config(config)

    # 6. Send the success notification
    topic = config.get("ntfy_topic_global", "fallback_topic")
    msg = f"{actual_user_name} completed {chore['title'].lower()}! 🎉"
    send_ntfy(topic, msg, title="Chore Complete!", tags="white_check_mark,tada")

    return f"<h1>Thanks {actual_user_name}! Chore logged successfully.</h1>", 200


if __name__ == "__main__":
    is_windows = (os.name == "nt")
    local = "127.0.0.1"
    network = "0.0.0.0"
    app.run(debug=is_windows, host=network, port=5000)
