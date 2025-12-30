import requests
from graph_auth import get_access_token


GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"


def read_inbox(limit=5):
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

    if response.status_code != 200:
        raise Exception(f"❌ Graph error: {response.text}")

    messages = response.json().get("value", [])

    for msg in messages:
        print("=" * 60)
        print("📧 Subject :", msg.get("subject"))
        print("👤 From    :", msg.get("from", {}).get("emailAddress", {}).get("address"))
        print("🕒 Received:", msg.get("receivedDateTime"))
        print("📝 Preview :", msg.get("bodyPreview"))


if __name__ == "__main__":
    read_inbox()
