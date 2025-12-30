import requests
from graph_auth import get_access_token
from utils.excel_handler import ExcelHandler
from config import EXCEL_FILE_PATH

GRAPH_REPLY_ENDPOINT = "https://graph.microsoft.com/v1.0/me/sendMail"

# 👇 ADD THIS FUNCTION HERE (TOP OF FILE)
def choose_reply_template(subject, summary):
    text = f"{subject} {summary}".lower()

    if any(k in text for k in [
        "status", "progress", "any update", "current status", "update on"
    ]):
        return (
            "Noted.\n\n"
            "I’ll check the current status and get back to you.\n\n"
            "Regards,\n"
            "Follow-up Agent"
        )

    if any(k in text for k in [
        "entity", "formation", "registration",
        "return filing", "return",
        "tds", "tds return", "tds deposit",
        "vat", "vat return", "vat deposit",
        "gst", "gst return", "gst deposit",
        "tax", "computation",
        "audit", "statutory", "compliance",
        "e-invoicing", "einvoicing",
        "financial", "closure",
        "purchase invoice", "invoice algo", "algo",
        "property", "coworking",
        "rent", "rental", "rentals",
        "maintenance", "maintainance"
    ]):
        return (
            "Noted.\n\n"
            "This is a detailed task and I’m tracking it. "
            "I’ll update you as it progresses.\n\n"
            "Regards,\n"
            "Follow-up Agent"
        )

    return (
        "Noted.\n\n"
        "This has been taken up and I’ll follow up on it until closure.\n\n"
        "Regards,\n"
        "Follow-up Agent"
    )

def send_auto_replies():
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    excel = ExcelHandler(EXCEL_FILE_PATH)
    df = excel.load_data()

    if df.empty:
        print("No follow-ups found.")
        return 0

    sent_count = 0

    for idx, row in df.iterrows():

        auto_reply = str(row.get("Auto Reply Sent", "")).strip().lower()
        if auto_reply == "yes":
            continue

        status = str(row.get("Status", "")).strip().lower()
        if status != "pending":
            continue

        to_email = row.get("From Email")
        subject = row.get("Subject")

        if not to_email or not subject:
            continue

        body_text = (
            "Noted.\n\n"
            "This follow-up is being tracked and reminder notifications are active "
            "until the task is completed.\n\n"
            "Regards,\n"
            "Follow-up Agent"
        )

        payload = {
            "message": {
                "subject": f"Re: {subject}",
                "body": {
                    "contentType": "Text",
                    "content": body_text
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ]
            }
        }

        response = requests.post(
            GRAPH_REPLY_ENDPOINT,
            headers=headers,
            json=payload
        )

        if response.status_code in (200, 202):
            df.at[idx, "Auto Reply Sent"] = "Yes"
            sent_count += 1

    excel.save_data(df)
    return sent_count

if __name__ == "__main__":
    count = send_auto_replies()
    print(f"✅ {count} auto-reply email(s) sent.")
