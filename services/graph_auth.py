import os
import msal
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = [
    "Mail.Read",
    "Mail.Send",
    "User.Read"
]

TOKEN_CACHE_FILE = "graph_token_cache.bin"


def get_access_token():
    cache = msal.SerializableTokenCache()

    if os.path.exists(TOKEN_CACHE_FILE):
        cache.deserialize(open(TOKEN_CACHE_FILE, "r").read())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        result = None

    if not result:
        print("🔐 Starting device login flow...")

        flow = app.initiate_device_flow(scopes=SCOPES)

        if "user_code" not in flow:
            raise Exception("❌ Failed to start device flow")

        print(flow["message"])  # <-- THIS IS WHAT YOU WILL SEE

        result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())

        print("✅ Access token acquired successfully")
        return result["access_token"]

    else:
        raise Exception(f"❌ Token error: {result}")

if __name__ == "__main__":
    get_access_token()

