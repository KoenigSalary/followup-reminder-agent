import os

# -------------------------------------------------
# App Settings
# -------------------------------------------------
APP_TITLE = "Follow-up & Reminder Agent"

# -------------------------------------------------
# Base Directory
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------
# Data / Excel Configuration
# -------------------------------------------------
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_FILE_PATH = "/Users/praveenchaudhary/Downloads/Agent/CEO_Followup_Agent/data/auto_reply_sent.xlsx"

# -------------------------------------------------
# Email Configuration (STANDARDIZED)
# -------------------------------------------------
# As instructed: use ONLY this email everywhere
DEFAULT_EMAIL = "praveen.chaudhary@koenig-solutions.com"

EMAIL_SENDER = DEFAULT_EMAIL
EMAIL_RECEIVER = DEFAULT_EMAIL

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

SMTP_USERNAME = "praveen.chaudhary@koenig-solutions.com"
SMTP_PASSWORD = "SalaryRecoAgent"   # app password

SENDER_NAME = "Praveen Chaudhary"

# IMPORTANT:
# Do NOT hardcode password here.
# Set it as an environment variable:
# export CEO_AGENT_EMAIL_PASSWORD="your_app_password"
EMAIL_PASSWORD_ENV_KEY = "CEO_AGENT_EMAIL_PASSWORD"

# -------------------------------------------------
# Validation
# -------------------------------------------------
def validate_paths():
    """
    Ensure required folders and files exist.
    Create them if missing (safe for production).
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(EXCEL_FILE_PATH):
        # Create empty Excel file structure if missing
        import pandas as pd

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
