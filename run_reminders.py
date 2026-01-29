# -*- coding: utf-8 -*-
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date

import pandas as pd

# IMPORTANT: keep your key name CEO_AGENT_EMAIL_PASSWORD
from dotenv import load_dotenv
load_dotenv()

# Your Excel handler (adjust import path if different)
from utils.excel_handler import ExcelHandler


# -----------------------------
# Settings / Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

REGISTRY_FILE = os.path.join(DATA_DIR, "tasks_registry.xlsx")
TEAM_FILE = os.path.join(DATA_DIR, "Team_Directory.xlsx")  # optional


REMINDER_FREQUENCY_DAYS = {
    "URGENT": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 7,
}


# -----------------------------
# Secrets / Env helper
# -----------------------------
def _get_setting(key: str, default=None):
    """Read from OS env first, then Streamlit secrets (Cloud)."""
    val = os.getenv(key)
    if val is not None and str(val).strip() != "":
        return val

    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


def _require_setting(key: str):
    val = _get_setting(key)
    if val is None or str(val).strip() == "":
        raise ValueError(
            f"Missing required setting: {key}. "
            f"Set it in Streamlit Secrets (Cloud) or .env (local)."
        )
    return val


# -----------------------------
# Email / SMTP
# -----------------------------
def _smtp_config():
    smtp_server = _get_setting("SMTP_SERVER", "smtp.office365.com")
    smtp_port = int(_get_setting("SMTP_PORT", 587))
    smtp_username = _require_setting("SMTP_USERNAME")
    smtp_password = _require_setting("CEO_AGENT_EMAIL_PASSWORD")

    sender_name = _get_setting("AGENT_SENDER_NAME", "Follow-up Reminder Agent")
    sender_email = _get_setting("AGENT_SENDER_EMAIL", smtp_username)

    return {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "smtp_username": smtp_username,
        "smtp_password": smtp_password,
        "sender_name": sender_name,
        "sender_email": sender_email,
    }


def send_email(to_email: str, subject: str, html_body: str):
    cfg = _smtp_config()

    msg = MIMEMultipart("alternative")
    msg["From"] = f'{cfg["sender_name"]} <{cfg["sender_email"]}>'
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
        server.ehlo()
        server.starttls()
        server.login(cfg["smtp_username"], cfg["smtp_password"])
        server.sendmail(cfg["sender_email"], [to_email], msg.as_string())


# -----------------------------
# Team Directory (Owner -> Email)
# -----------------------------
def load_team_directory():
    """
    Loads Team_Directory.xlsx if present.
    Expected columns (flexible): Name, Email (case-insensitive)
    """
    if not os.path.exists(TEAM_FILE):
        return {}

    try:
        df = pd.read_excel(TEAM_FILE, engine="openpyxl")
    except Exception:
        # if openpyxl engine not needed or fails, pandas will try default
        df = pd.read_excel(TEAM_FILE)

    cols = {c.lower().strip(): c for c in df.columns}
    name_col = cols.get("name") or cols.get("owner") or cols.get("full name")
    email_col = cols.get("email") or cols.get("email id") or cols.get("mail")

    if not name_col or not email_col:
        return {}

    mapping = {}
    for _, r in df.iterrows():
        name = str(r.get(name_col, "")).strip()
        email = str(r.get(email_col, "")).strip()
        if name and email and "@" in email:
            mapping[name.lower()] = email

    return mapping


# Optional: hardcoded fallback mapping (if you don't have Team_Directory.xlsx yet)
HARDCODED_EMAILS = {
    # "sunil": "sunil@yourdomain.com",
    # "praveen": "praveen.chaudhary@koenig-solutions.com",
    # add more if needed
}


def resolve_owner_email(owner: str, team_map: dict) -> str | None:
    """
    Resolve owner name to email via:
    1) Team Directory mapping
    2) Hardcoded mapping
    """
    o = (owner or "").strip().lower()
    if not o:
        return None

    if o in team_map:
        return team_map[o]

    if o in HARDCODED_EMAILS:
        return HARDCODED_EMAILS[o]

    return None


# -----------------------------
# Reminder decision
# -----------------------------
def _parse_date(x):
    if x is None:
        return None
    try:
        if isinstance(x, float) and pd.isna(x):
            return None
    except Exception:
        pass

    try:
        return pd.to_datetime(x).date()
    except Exception:
        return None


def should_send_reminder(task: dict, force_first: bool = False) -> tuple[bool, str]:
    """
    Returns (should_send, reason).
    Reasons used for debugging/summary.
    """
    status = str(task.get("Status", "")).strip().upper()
    if status not in ["OPEN", "PENDING", "IN PROGRESS"]:
        return False, "status"

    owner = str(task.get("Owner", "")).strip()
    if not owner or owner.upper() == "UNASSIGNED":
        return False, "unassigned_owner"

    priority = str(task.get("Priority", "MEDIUM")).strip().upper()
    freq = REMINDER_FREQUENCY_DAYS.get(priority, REMINDER_FREQUENCY_DAYS["MEDIUM"])

    last_reminder = task.get("Last Reminder Date") or task.get("Last Reminder On")
    last_date = _parse_date(last_reminder)

    today = date.today()

    # ✅ first reminder immediately
    if last_date is None:
        return True, "first_reminder"

    # If explicitly forced, still allow sending even if last reminder exists
    if force_first:
        return True, "force_first"

    days_since = (today - last_date).days
    if days_since >= freq:
        return True, "frequency_ok"

    return False, "frequency_not_due"


# -----------------------------
# Email body
# -----------------------------
def build_email_html(task: dict) -> tuple[str, str]:
    owner = task.get("Owner", "Owner")
    subject_line = str(task.get("Subject", "Task Reminder")).strip()
    meeting_id = str(task.get("meeting_id", "") or task.get("Meeting ID", "") or "")
    due_date = str(task.get("Due Date", "")).strip()
    priority = str(task.get("Priority", "MEDIUM")).strip()
    status = str(task.get("Status", "")).strip()
    remarks = str(task.get("Remarks", "")).strip()

    mail_subject = f"Task Reminder: {subject_line}"

    html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.5;">
      <h3>Task Reminder</h3>
      <p>Hi <b>{owner}</b>,</p>
      <p>This is a reminder for the following task:</p>

      <table cellpadding="8" cellspacing="0" border="1" style="border-collapse: collapse;">
        <tr><td><b>Subject</b></td><td>{subject_line}</td></tr>
        <tr><td><b>MOM / Meeting ID</b></td><td>{meeting_id}</td></tr>
        <tr><td><b>Due Date</b></td><td>{due_date}</td></tr>
        <tr><td><b>Priority</b></td><td>{priority}</td></tr>
        <tr><td><b>Status</b></td><td>{status}</td></tr>
        <tr><td><b>Remarks</b></td><td>{remarks}</td></tr>
      </table>

      <p>Please take the necessary action and share an update.</p>
      <p>Thanks,<br/>Follow-up & Reminder Agent</p>
    </div>
    """
    return mail_subject, html


# -----------------------------
# Main API called by Streamlit
# -----------------------------
def send_reminders(force_first: bool = False) -> str:
    """
    Sends reminders for OPEN/PENDING/IN PROGRESS tasks.
    - First reminder is sent immediately when Last Reminder is empty.
    - Follow-ups are sent based on REMINDER_FREQUENCY_DAYS (priority).
    - Returns summary with skip reasons.
    """
    # Load registry
    if not os.path.exists(REGISTRY_FILE):
        return f"Registry not found: {REGISTRY_FILE}"

    excel_handler = ExcelHandler(REGISTRY_FILE)
    df = excel_handler.load_data()

    if df is None or df.empty:
        return "No tasks found."

    team_map = load_team_directory()

    sent = 0
    skipped = 0

    reason_counts = {
        "status": 0,
        "unassigned_owner": 0,
        "no_email": 0,
        "frequency_not_due": 0,
        "error": 0,
        "first_reminder": 0,
        "force_first": 0,
        "frequency_ok": 0,
    }

    now_str = datetime.now().strftime("%Y-%m-%d")

    for idx, row in df.iterrows():
        task = row.to_dict()

        should_send, reason = should_send_reminder(task, force_first=force_first)

        if not should_send:
            skipped += 1
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            continue

        owner = str(task.get("Owner", "")).strip()
        to_email = resolve_owner_email(owner, team_map)
        if not to_email:
            skipped += 1
            reason_counts["no_email"] += 1
            continue

        try:
            mail_subject, html = build_email_html(task)
            send_email(to_email=to_email, subject=mail_subject, html_body=html)

            sent += 1
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

            # Update reminder fields
            df.at[idx, "Last Reminder Date"] = now_str
            df.at[idx, "Last Reminder On"] = now_str
            df.at[idx, "Last Updated"] = now_str

        except Exception:
            skipped += 1
            reason_counts["error"] += 1
            continue

    # Save updates
    excel_handler.save_data(df)

    # Summary
    return (
        f"Sent {sent} reminders, skipped {skipped} tasks | "
        f"reasons: no_email={reason_counts['no_email']}, "
        f"status={reason_counts['status']}, "
        f"unassigned_owner={reason_counts['unassigned_owner']}, "
        f"frequency_not_due={reason_counts['frequency_not_due']}, "
        f"error={reason_counts['error']} | "
        f"sent_breakdown: first={reason_counts['first_reminder']}, "
        f"forced={reason_counts['force_first']}, "
        f"scheduled={reason_counts['frequency_ok']}"
    )
