import requests
import json
import os
from datetime import datetime, timedelta

HANDLE = "kathiravanm65"

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")

DB_FILE = "solved_problems.json"


def send_whatsapp_message(message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": WHATSAPP_TO,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.text)


def get_solved_problems():
    url = f"https://codeforces.com/api/user.status?handle={HANDLE}"

    response = requests.get(url)
    data = response.json()

    solved = {}

    for submission in data["result"]:
        if submission.get("verdict") == "OK":
            problem = submission["problem"]

            contest_id = problem.get("contestId")
            index = problem.get("index")
            name = problem.get("name", "Unknown")
            rating = problem.get("rating", "N/A")

            if contest_id and index:
                key = f"{contest_id}{index}"

                creation_time = submission["creationTimeSeconds"]
                solve_date = datetime.utcfromtimestamp(creation_time)

                if key not in solved:
                    solved[key] = {
                        "name": name,
                        "rating": rating,
                        "date": solve_date.strftime("%Y-%m-%d")
                    }

    return solved


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def check_revision():
    old_data = load_db()
    new_data = get_solved_problems()

    today = datetime.utcnow().date()

    for key, value in new_data.items():

        if key not in old_data:
            old_data[key] = value

        solve_date = datetime.strptime(
            old_data[key]["date"],
            "%Y-%m-%d"
        ).date()

        days = (today - solve_date).days

        if days == 2:
            msg = (
                f"🔥 Codeforces Revision Reminder\n\n"
                f"Problem: {key} - {value['name']}\n"
                f"Rating: {value['rating']}\n"
                f"Solved 2 days ago.\n\n"
                f"Try solving again without seeing your old code 💪"
            )

            send_whatsapp_message(msg)

    save_db(old_data)


if __name__ == "__main__":
    check_revision()
