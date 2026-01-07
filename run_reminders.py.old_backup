import os
from pathlib import Path
import pandas as pd

# =================================================
# App Settings
# =================================================
APP_TITLE = "Follow-up & Reminder Agent"

# =================================================
# Base Directory (Local + Streamlit Cloud Safe)
# =================================================
BASE_DIR = Path(__file__).resolve().parent

# =================================================
# Data / Excel Configuration
# =================================================
DATA_DIR = BASE_DIR / "data"
EXCEL_FILE_PATH = DATA_DIR / "auto_reply_sent.xlsx"
TASK_REGISTRY_FILE = DATA_DIR / "tasks_registry.xlsx"
TEAM_DIRECTORY_FILE = DATA_DIR / "Team_Directory.xlsx"

# =================================================
# Email Configuration (STANDARDIZED)
# =================================================
DEFAULT_EMAIL = "praveen.chaudhary@koenig-solutions.com"

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USERNAME = DEFAULT_EMAIL

# ❗ Password MUST come from env / Streamlit secrets
EMAIL_PASSWORD_ENV_KEY = "CEO_AGENT_EMAIL_PASSWORD"

# Display name in emails
SENDER_NAME = "Task Followup Team"

# Signature (used everywhere)
EMAIL_SIGNATURE = "Task Followup Team"

# =================================================
# Feature Flags (Q4 Safe)
# =================================================
ENABLE_GRAPH_READ = os.getenv("ENABLE_GRAPH_READ", "false").lower() == "true"
ENABLE_GRAPH_REPLY = os.getenv("ENABLE_GRAPH_REPLY", "false").lower() == "true"

# =================================================
# Validation (Cloud + Local Safe)
# =================================================
def validate_paths():
    """
    Ensure required folders and files exist.
    Safe for:
    - Local execution
    - Fresh Git clone
    - Streamlit Cloud
    """

    # Ensure data folder exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Follow-up registry (used by Streamlit dashboard)
    if not EXCEL_FILE_PATH.exists():
        df = pd.DataFrame(
            columns=[
                "Subject",
                "Owner",
                "Due Date",
                "Remarks",
                "Status",
                "Priority",
                "Created On",
                "Last Updated",
                "Last Reminder Date"
            ]
        )
        df.to_excel(EXCEL_FILE_PATH, index=False)

    # Task registry (used by MOM + reminders)
    if not TASK_REGISTRY_FILE.exists():
        df = pd.DataFrame(
            columns=[
                "task_id",
                "task_text",
                "owner",
                "status",
                "meeting_id",
                "created_on",
                "last_reminder_date"
            ]
        )
        df.to_excel(TASK_REGISTRY_FILE, index=False)

    # Team directory placeholder (do NOT auto-create real data)
    if not TEAM_DIRECTORY_FILE.exists():
        df = pd.DataFrame(columns=["Name", "Email"])
        df.to_excel(TEAM_DIRECTORY_FILE, index=False)

