import os
import requests
import msal
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

MAILBOX = "praveen.chaudhary@koenig-solutions.com"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )
    token = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" not in token:
        raise Exception(token)
    return token["access_token"]

def get_recent_inbox_messages(headers, days=30):
    since_date = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = f"https://graph.microsoft.com/v1.0/users/{MAILBOX}/mailFolders/Inbox/messages"

    params = {
        "$filter": f"receivedDateTime ge {since_date}",
        "$select": "id,subject,from,conversationId,receivedDateTime,body",
        "$top": 100
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("value", [])

def read_threads():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    messages = get_recent_inbox_messages(headers)
    print(f"Fetched {len(messages)} inbox messages")

    threads = defaultdict(list)

    for msg in messages:
        cid = msg.get("conversationId")
        threads[cid].append(msg)

    # Sort each thread by time
    for cid in threads:
        threads[cid].sort(key=lambda m: m["receivedDateTime"])

    return threads

if __name__ == "__main__":
    threads = read_threads()
    print(f"Built {len(threads)} conversation threads\n")

    for cid, msgs in threads.items():
        print("=" * 80)
        print("Conversation ID:", cid)
        print("Subject:", msgs[0].get("subject"))
        print("-" * 80)

        for m in msgs:
            sender = m.get("from", {}).get("emailAddress", {}).get("address")
            date = m.get("receivedDateTime")
            body = m.get("body", {}).get("content", "")
            clean = body.replace("\n", " ").replace("\r", " ")
            print(f"[{date}] {sender}")
            print(clean[:300])
            print("-" * 40)
