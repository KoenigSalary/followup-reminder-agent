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
EXCEL_FILE_PATH = DATA_DIR / "auto_reply_sent.xlsx"

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
    """
    Ensure required folders and files exist.
    Safe for:
    - Local runs
    - Fresh clone
    - Streamlit Cloud
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not EXCEL_FILE_PATH.exists():
        df = pd.DataFrame(
            columns=[
                "Subject",
                "Owner",
                "Due Date",
                "Remarks",
                "Status",
                "Created On",
                "Last Updated"
            ]
        )
        df.to_excel(EXCEL_FILE_PATH, index=False)
