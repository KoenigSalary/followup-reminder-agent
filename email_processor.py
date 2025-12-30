import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from config import (
    EMAIL_SENDER,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_PASSWORD_ENV_KEY
)

load_dotenv()  # harmless locally, ignored in cloud

SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")

if not SMTP_PASSWORD:
    raise EnvironmentError("Environment variable 'CEO_AGENT_EMAIL_PASSWORD' not set")

class EmailProcessor:
    def __init__(self):
        self.password = os.getenv(EMAIL_PASSWORD_ENV_KEY)

        if not self.password:
            raise EnvironmentError(
                f"Environment variable '{EMAIL_PASSWORD_ENV_KEY}' not set"
            )

    # -------------------------------------------------
    # Send generic email
    # -------------------------------------------------
    def send_email(self, subject, body, to_email=None):
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email or EMAIL_SENDER
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, self.password)
            server.send_message(msg)

    # -------------------------------------------------
    # SAFE AUTO-REPLY (Q4-safe)
    # -------------------------------------------------
    def send_auto_reply(self, to_email, subject):
        reply_subject = f"Re: {subject}"
        body = (
            "Noted.\n\n"
            "This task is being tracked and reminder notifications are active until completion.\n\n"
            "Regards,\n"
            "CEO Follow-up Agent"
        )

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = reply_subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, self.password)
            server.send_message(msg)

    # -------------------------------------------------
    # Process emails & update Excel (Q4 placeholder)
    # -------------------------------------------------
    def process_and_update(self, excel_handler):
        """
        Q4-safe placeholder:
        Sends ONE auto-reply acknowledgment
        and marks Excel to prevent duplicates.
        """

        df = excel_handler.load_data()
        sent_count = 0

        for idx, row in df.iterrows():
            auto_reply = str(row.get("Auto Reply Sent", "")).strip().lower()

            if auto_reply != "yes":
                subject = row.get("Subject", "CEO Follow-up Task")

                self.send_auto_reply(
                    to_email=EMAIL_SENDER,
                    subject=subject
                )

                df.at[idx, "Auto Reply Sent"] = "Yes"
                sent_count += 1
                break  # ONLY one auto-reply per run

        excel_handler.save_data(df)
        return sent_count
