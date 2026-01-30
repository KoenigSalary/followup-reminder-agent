# config.py
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
# HARDCODED EMAIL MAPPINGS
# -------------------------------------------------
# Add this new section for fallback email mappings
HARDCODED_EMAILS = {
    # From your Team Directory
    "admin": "admin@koenig-solutions.com",
    "sunil": "sunilkumar.kushwaha@koenig-solutions.com",
    "sunilkumar": "sunilkumar.kushwaha@koenig-solutions.com",
    "sarika": "sarika.gupta@koenig-solutions.com",
    "ritika": "ritika.bhalla@koenig-solutions.com",
    "tripti": "tripti@koenig-solutions.com",
    "jony": "jony.saini@koenig-solutions.com",
    "anurag": "anurag.chauhan@koenig-solutions.com",
    "ajay": "ajay.rawat@koenig-solutions.com",
    "aditya": "aditya.singh@koenig-solutions.com",
    "jatin": "jatin.khurana@koenig-solutions.com",
    "praveen": "praveen.chaudhary@koenig-solutions.com",
    "vipin": "vipin.nautiyal@koenig-solutions.com",
    "tamanna": "tamanna.alisha@koenig-solutions.com",
    "nishant": "nishant.yash@koenig-solutions.com",
    "shkelzen": "shkelzen.sadiku@koenig-solutions.com",
    "nupur": "nupur.munjal@koenig-solutions.com",
    "vardaan": "vardaan.aggarwal@koenig-solutions.com",
    "dimna": "dimna.k@koenig-solutions.com",  # UPDATE with actual email
     
    # Common variations
    "praveen kumar": "praveen.chaudhary@koenig-solutions.com",
    "anurag chauhan": "anurag.chauhan@koenig-solutions.com",
    "ajay rawat": "ajay.rawat@koenig-solutions.com",
}

# -------------------------------------------------
# Reminder Settings
# -------------------------------------------------
REMINDER_FREQUENCY_DAYS = {
    "URGENT": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 7,
}

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
