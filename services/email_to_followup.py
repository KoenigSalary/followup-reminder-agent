import re
from datetime import datetime, timedelta
import pandas as pd
import requests

from graph_auth import get_access_token
from utils.excel_handler import ExcelHandler
from config import EXCEL_FILE_PATH


GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"

KEYWORDS = [
    "follow up", "please", "kindly", "ensure",
    "needful", "update", "action"
]


def is_actionable(subject, preview):
    text = f"{subject} {preview}".lower()
    return any(k in text for k in KEYWORDS)


def process_emails(limit=10):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "$top": limit,
        "$select": "id,subject,from,receivedDateTime,bodyPreview"
    }

    response = requests.get(GRAPH_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()

    messages = response.json().get("value", [])

    excel = ExcelHandler(EXCEL_FILE_PATH)
    df = excel.load_data()

    created = 0

    for msg in messages:
        msg_id = msg["id"]

        # Duplicate protection
        if (
            not df.empty
            and "Message ID" in df.columns
            and msg_id in df["Message ID"].astype(str).values
        ):
            continue

        subject = msg.get("subject", "")
        preview = msg.get("bodyPreview", "")

        if not is_actionable(subject, preview):
            continue

        new_row = {
            "Message ID": msg_id,
            "Received Date": msg.get("receivedDateTime"),
            "From Email": msg.get("from", {}).get("emailAddress", {}).get("address"),
            "Subject": subject,
            "Task Summary": preview[:200],
            "Owner": "Praveen",
            "Priority": "Medium",
            "Due Date": (datetime.today() + timedelta(days=2)).date(),
            "Status": "Pending",
            "Last Reminder Date": "",
            "Auto Reply Sent": "",
            "Source": "Email"
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        created += 1

    excel.save_data(df)
    return created


if __name__ == "__main__":
    count = process_emails()
    print(f"✅ {count} follow-up(s) created from inbox.")
