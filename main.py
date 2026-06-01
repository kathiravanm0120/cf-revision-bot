import requests
import json
import os
from datetime import datetime

HANDLE = "kathiravanm65"

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")

DB_FILE = "/tmp/solved_problems.json"


def send_whatsapp_message(message):
    url = (
        f"https://graph.facebook.com/v22.0/"
        f"{PHONE_NUMBER_ID}/messages"
    )

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

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.text)


def get_solved_problems():
    url = (
        f"https://codeforces.com/api/"
        f"user.status?handle={HANDLE}"
    )

    response = requests.get(url)
    data = response.json()

    solved = {}

    for submission in data["result"]:

        if submission.get("verdict") != "OK":
            continue

        problem = submission["problem"]

        contest_id = problem.get("contestId")
        index = problem.get("index")

        if not contest_id or not index:
            continue

        key = f"{contest_id}{index}"

        if key in solved:
            continue

        solved[key] = {
            "name": problem.get(
                "name",
                "Unknown"
            ),
            "rating": problem.get(
                "rating",
                "N/A"
            ),
            "date":
            datetime.utcfromtimestamp(
                submission[
                    "creationTimeSeconds"
                ]
            ).strftime("%Y-%m-%d")
        }

    return solved


def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=4
        )


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

        days = (
            today - solve_date
        ).days

        if days == 2:

            message = (
                "🔥 Codeforces Revision Reminder\n\n"
                f"Problem: {key}\n"
                f"Name: {value['name']}\n"
                f"Rating: {value['rating']}\n\n"
                "Solved 2 days ago.\n"
                "Try solving again without "
                "seeing your old code 💪"
            )

            send_whatsapp_message(
                message
            )

    save_db(old_data)


if __name__ == "__main__":
    check_revision()
