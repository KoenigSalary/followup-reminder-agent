# ================= ENV LOADING =================
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load env (local .env OR Streamlit Secrets)
load_dotenv(dotenv_path=ENV_PATH)

SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")
if not SMTP_PASSWORD:
    raise EnvironmentError(
        "Environment variable 'CEO_AGENT_EMAIL_PASSWORD' not set"
    )
# ==============================================

# ================= IMPORTS =====================
import smtplib
import pandas as pd
from email.message import EmailMessage
from datetime import datetime, timedelta
# ==============================================

# ================= CONFIG ======================
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")
SENDER_NAME = os.getenv("AGENT_SENDER_NAME", "Followup Agent")

TASK_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"
TEAM_FILE = BASE_DIR / "data" / "Team_Directory.xlsx"
# ==============================================


# ================= HELPERS =====================
def resolve_email(owner: str):
    """
    Resolve owner to email:
    - If owner is already an email → return directly
    - Else resolve using Team_Directory.xlsx
    """
    if "@" in owner:
        return owner

    df = pd.read_excel(TEAM_FILE)
    match = df[df["Name"].str.lower() == owner.lower()]
    if not match.empty:
        return match.iloc[0]["Email"]
    return None

def should_send_reminder(last_reminder):
    """
    Send reminder only if:
    - No reminder sent earlier, OR
    - Last reminder was sent 2 or more days ago
    """
    if pd.isna(last_reminder) or last_reminder == "":
        return True

    last_date = pd.to_datetime(last_reminder).date()
    return datetime.now().date() >= (last_date + timedelta(days=2))

def build_email(owner, owner_email, tasks_df):
    msg = EmailMessage()
    msg["From"] = f"{SENDER_NAME} <{SMTP_USERNAME}>"
    msg["To"] = owner_email
    msg["Subject"] = "⏰ Pending Action Items – Reminder"

    body = f"""Dear {owner},

This is a gentle reminder for the following pending action items:
"""

    for _, t in tasks_df.iterrows():
        body += f"""
• Task ID : {t['task_id']}
  Task    : {t['task_text']}
  Source  : {t['meeting_id']}
"""

    body += """

Kindly let me know once completed.

Regards,
Task Followup Team
"""
    msg.set_content(body)
    return msg
# ==============================================


# ================= MAIN LOGIC ==================
def send_reminders():
    df = pd.read_excel(TASK_FILE)

    # Only OPEN tasks
    df = df[df["status"] == "OPEN"]

    if df.empty:
        print("✅ No pending tasks. No reminders sent.")
        return

    # Ensure column exists
    if "last_reminder_date" not in df.columns:
        df["last_reminder_date"] = None

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)

    for owner, group in df.groupby("owner"):
        owner_email = resolve_email(owner)

        if not owner_email:
            print(f"⚠️ No email found for owner: {owner}. Skipping.")
            continue

        # Check alternate-day rule (use latest reminder for this owner)
        last_reminder = group["last_reminder_date"].max()

        if not should_send_reminder(last_reminder):
            print(f"⏭️ Skipping {owner} (last reminder too recent)")
            continue

        print(f"📧 Sending reminder to {owner} ({owner_email})")

        email = build_email(owner, owner_email, group)
        server.send_message(email)

        # Update last_reminder_date for all tasks of this owner
        df.loc[group.index, "last_reminder_date"] = datetime.now()

        print("✅ Reminder sent")

    server.quit()

    # Save updated reminder dates
    df.to_excel(TASK_FILE, index=False)
# ==============================================


# ================= ENTRY =======================
if __name__ == "__main__":
    send_reminders()
# ==============================================
