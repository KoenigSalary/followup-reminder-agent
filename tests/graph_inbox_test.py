import os
import requests
import msal
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

token = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" not in token:
    raise Exception(token)

headers = {
    "Authorization": f"Bearer {token['access_token']}"
}

url = (
    "https://graph.microsoft.com/v1.0/users/"
    "praveen.chaudhary@koenig-solutions.com"
    "/mailFolders/Inbox/messages"
    "?$top=5&$select=subject,from,conversationId,receivedDateTime"
)

response = requests.get(url, headers=headers, timeout=30)

if response.status_code == 504:
    print("Graph timeout, retrying...")
    response = requests.get(url, headers=headers, timeout=30)

response.raise_for_status()

for msg in response.json().get("value", []):
    print("Subject:", msg.get("subject"))
    print("From:", msg.get("from", {}).get("emailAddress", {}).get("address"))
    print("Conversation ID:", msg.get("conversationId"))
    print("-" * 40)
