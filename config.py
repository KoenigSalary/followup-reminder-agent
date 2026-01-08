import os
from pathlib import Path
import pandas as pd

# -------------------------------------------------
# App Settings
# -------------------------------------------------
APP_TITLE = "Follow-up & Reminder Agent"

# -------------------------------------------------
# Base Directory (works locally + on Streamlit Cloud)
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# Data / Excel Configuration
# -------------------------------------------------
DATA_DIR = BASE_DIR / "data"

# ✅ FIXED: Use tasks_registry.xlsx as the main file
EXCEL_FILE_PATH = DATA_DIR / "tasks_registry.xlsx"
TASK_FILE = DATA_DIR / "tasks_registry.xlsx"

# For email reply tracking (separate file)
EMAIL_REPLY_FILE = DATA_DIR / "auto_reply_sent.xlsx"

# -------------------------------------------------
# Email Configuration (STANDARDIZED)
# -------------------------------------------------
DEFAULT_EMAIL = "praveen.chaudhary@koenig-solutions.com"

EMAIL_SENDER = DEFAULT_EMAIL
EMAIL_RECEIVER = DEFAULT_EMAIL

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

SMTP_USERNAME = DEFAULT_EMAIL

# ❗ Password must come from environment / Streamlit secrets
EMAIL_PASSWORD_ENV_KEY = "CEO_AGENT_EMAIL_PASSWORD"

SENDER_NAME = "Praveen Chaudhary"

# -------------------------------------------------
# Validation (Cloud-safe)
# -------------------------------------------------
def validate_paths():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create tasks_registry.xlsx if missing
    if not TASK_FILE.exists():
        task_df = pd.DataFrame(
            columns=[
                "task_id",
                "meeting_id",
                "owner",
                "task_text",
                "status",
                "created_on",
                "last_reminder_on",
                "last_reminder",
                "last_reminder_date",
                "priority",
                "deadline",
                "completed_date",
                "days_taken",
                "performance_rating",
                "cc"
            ]
        )
        task_df.to_excel(TASK_FILE, index=False)
    
    # Create email reply tracking file if missing
    if not EMAIL_REPLY_FILE.exists():
        email_df = pd.DataFrame(
            columns=[
                "Auto Reply Sent",
                "Meaning",
                "Action",
                "Message ID",
                "Received Date"
            ]
        )
        email_df.to_excel(EMAIL_REPLY_FILE, index=False)
