# -*- coding: utf-8 -*-
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date, timedelta

import pandas as pd
import numpy as np

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
    "URGENT": 1,    # Every day
    "HIGH": 2,      # Every 2 days
    "MEDIUM": 3,    # Every 3 days
    "LOW": 7,       # Every week
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

    try:
        with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()  # Some servers require ehlo after starttls
            server.login(cfg["smtp_username"], cfg["smtp_password"])
            server.sendmail(cfg["sender_email"], [to_email], msg.as_string())
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


# -----------------------------
# Team Directory (Owner -> Email) - FIXED VERSION
# -----------------------------
def load_team_directory():
    """
    Loads Team_Directory.xlsx if present.
    FIXED: More robust column name detection and data handling
    """
    if not os.path.exists(TEAM_FILE):
        print(f"⚠️ Team directory file not found: {TEAM_FILE}")
        return {}

    try:
        # Try reading with openpyxl first
        df = pd.read_excel(TEAM_FILE, engine="openpyxl")
    except Exception as e:
        print(f"⚠️ Error reading with openpyxl: {e}, trying default engine")
        try:
            df = pd.read_excel(TEAM_FILE)
        except Exception as e2:
            print(f"❌ Failed to read team directory: {e2}")
            return {}

    # Debug: Show what columns we found
    print(f"📊 Team Directory columns: {list(df.columns)}")
    
    # Clean column names: lowercase, strip spaces
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Common column name variations
    name_variations = ["name", "full name", "fullname", "employee name", "owner", "person", "contact"]
    email_variations = ["email", "email address", "email id", "mail", "e-mail", "emailid"]
    
    # Find name column
    name_col = None
    for variation in name_variations:
        if variation in df.columns:
            name_col = variation
            break
    
    # Find email column
    email_col = None
    for variation in email_variations:
        if variation in df.columns:
            email_col = variation
            break
    
    if not name_col or not email_col:
        print(f"❌ Could not find name/email columns. Name col: {name_col}, Email col: {email_col}")
        print(f"   Available columns: {list(df.columns)}")
        return {}
    
    print(f"✅ Found columns: Name='{name_col}', Email='{email_col}'")
    
    mapping = {}
    skipped_rows = 0
    
    for idx, row in df.iterrows():
        try:
            name = str(row.get(name_col, "")).strip()
            email = str(row.get(email_col, "")).strip()
            
            # Validate
            if not name or pd.isna(name):
                skipped_rows += 1
                continue
                
            if not email or pd.isna(email) or "@" not in email:
                skipped_rows += 1
                continue
            
            # Clean email
            email = email.lower().strip()
            
            # Add mappings
            # 1. Full name (lowercase)
            mapping[name.lower()] = email
            
            # 2. First name only
            first_name = name.split()[0].lower() if " " in name else name.lower()
            if first_name and first_name not in mapping:
                mapping[first_name] = email
            
            # 3. First name with first letter capitalized (common format)
            first_name_cap = first_name.capitalize()
            if first_name_cap and first_name_cap not in mapping:
                mapping[first_name_cap.lower()] = email
                
        except Exception as e:
            print(f"⚠️ Error processing row {idx}: {e}")
            skipped_rows += 1
            continue
    
    print(f"✅ Loaded {len(mapping)} email mappings from team directory")
    if skipped_rows > 0:
        print(f"⚠️ Skipped {skipped_rows} invalid rows")
    
    # Show sample of mappings
    if mapping:
        print("📋 Sample mappings:")
        for i, (name, email) in enumerate(list(mapping.items())[:5]):
            print(f"   {name} -> {email}")
    
    return mapping


# Hardcoded fallback mapping
HARDCODED_EMAILS = {
    "sunil": "sunil@koenig-solutions.com",
    "praveen": "praveen.chaudhary@koenig-solutions.com",
    "rajesh": "rajesh@koenig-solutions.com",
    "amit": "amit@koenig-solutions.com",
    # Add more common names
    "john": "john@koenig-solutions.com",
    "mike": "mike@koenig-solutions.com",
    "david": "david@koenig-solutions.com",
    "sarah": "sarah@koenig-solutions.com",
    "emma": "emma@koenig-solutions.com",
}


def resolve_owner_email(owner: str, team_map: dict) -> str | None:
    """
    Resolve owner name to email.
    """
    if not owner or pd.isna(owner):
        return None
    
    owner_str = str(owner).strip()
    if not owner_str:
        return None
    
    # Try different variations
    variations = [
        owner_str.lower(),  # lowercase
        owner_str,  # original case
        owner_str.split()[0].lower() if " " in owner_str else owner_str.lower(),  # first name lowercase
        owner_str.split()[0] if " " in owner_str else owner_str,  # first name original case
    ]
    
    for variation in variations:
        if variation in team_map:
            return team_map[variation]
    
    # Try hardcoded emails
    for variation in variations:
        if variation.lower() in HARDCODED_EMAILS:
            return HARDCODED_EMAILS[variation.lower()]
    
    print(f"⚠️ No email found for owner: '{owner_str}'")
    return None


# -----------------------------
# Reminder decision - FIXED VERSION (handles NaT)
# -----------------------------
def _parse_date(x):
    """Parse date from various formats, safely handle NaT."""
    if x is None or pd.isna(x):
        return None
    
    try:
        # If it's already a date/datetime object
        if isinstance(x, (date, datetime)):
            return x.date() if isinstance(x, datetime) else x
        
        # If it's a pandas NaT
        if hasattr(x, '__class__') and x.__class__.__name__ == 'NaTType':
            return None
        
        # If it's a string
        if isinstance(x, str):
            x = x.strip()
            if not x or x.lower() in ['nat', 'nan', 'null', '']:
                return None
            # Try multiple date formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(x, fmt).date()
                except:
                    continue
        
        # Try pandas parsing as last resort
        result = pd.to_datetime(x, errors='coerce')
        if pd.isna(result):
            return None
        return result.date()
    except Exception as e:
        print(f"⚠️ Could not parse date '{x}': {e}")
        return None


def should_send_reminder(task: dict, force_first: bool = False) -> tuple[bool, str]:
    """
    Returns (should_send, reason).
    FIXED: Handles NaT dates safely.
    """
    # Check status
    status = str(task.get("Status", "")).strip().upper()
    valid_statuses = ["OPEN", "PENDING", "IN PROGRESS", "IN_PROGRESS"]
    if status not in valid_statuses:
        return False, f"status_not_active ({status})"

    # Check owner
    owner = str(task.get("Owner", "")).strip()
    if not owner or owner.upper() == "UNASSIGNED":
        return False, "unassigned_owner"

    # Get priority
    priority = str(task.get("Priority", "MEDIUM")).strip().upper()
    freq = REMINDER_FREQUENCY_DAYS.get(priority, REMINDER_FREQUENCY_DAYS["MEDIUM"])

    # Get dates - FIXED: Safely handle NaT
    last_reminder = task.get("Last Reminder Date") or task.get("Last Reminder On")
    created_date = task.get("Created On")
    
    last_date = _parse_date(last_reminder)
    created_on_date = _parse_date(created_date)
    
    today = date.today()

    # 🚨 FIX: First reminder logic
    # If task has never been reminded (last_date is None/NaT)
    if last_date is None:
        # If created date is today or earlier, or if we don't have created date
        if created_on_date is None or created_on_date <= today:
            return True, "first_reminder"
        else:
            return False, "future_created_date"

    # If explicitly forced (for testing)
    if force_first:
        return True, "force_first"

    # Regular reminder based on frequency
    try:
        days_since = (today - last_date).days
        if days_since >= freq:
            return True, f"frequency_ok ({days_since}d >= {freq}d)"
        return False, f"frequency_not_due ({days_since}d < {freq}d)"
    except Exception as e:
        print(f"⚠️ Error calculating days since last reminder: {e}")
        return False, f"date_calculation_error"


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
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.5; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #1f77b4; color: white; padding: 15px; text-align: center; border-radius: 5px; }}
            .content {{ padding: 20px; background-color: #f9f9f9; border-radius: 5px; margin-top: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            .priority-urgent {{ color: #d63031; font-weight: bold; }}
            .priority-high {{ color: #e17055; font-weight: bold; }}
            .priority-medium {{ color: #fdcb6e; font-weight: bold; }}
            .priority-low {{ color: #00b894; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📧 Task Reminder</h2>
            </div>
            <div class="content">
                <p>Hi <strong>{owner}</strong>,</p>
                <p>This is a reminder for your pending task:</p>
                
                <table>
                    <tr><th>Subject</th><td>{subject_line}</td></tr>
                    <tr><th>Meeting ID</th><td>{meeting_id if meeting_id else 'N/A'}</td></tr>
                    <tr><th>Due Date</th><td>{due_date if due_date else 'Not specified'}</td></tr>
                    <tr><th>Priority</th><td><span class="priority-{priority.lower()}">{priority}</span></td></tr>
                    <tr><th>Status</th><td>{status}</td></tr>
                    <tr><th>Remarks</th><td>{remarks if remarks else 'No remarks'}</td></tr>
                </table>
                
                <p>Please take the necessary action and update the task status.</p>
                <p>You can view all your tasks in the Follow-up Dashboard.</p>
                
                <p>Best regards,<br>
                <strong>Follow-up & Reminder Agent</strong><br>
                Koenig Solutions</p>
            </div>
            <div class="footer">
                <p>This is an automated reminder. Please do not reply to this email.</p>
                <p>© {datetime.now().year} Koenig Solutions - Follow-up System</p>
            </div>
        </div>
    </body>
    </html>
    """
    return mail_subject, html


# -----------------------------
# Main API - Simplified version without test_mode parameter
# -----------------------------
def send_reminders(force_first: bool = False) -> str:
    """
    Sends reminders for OPEN/PENDING/IN PROGRESS tasks.
    Returns detailed summary.
    """
    # Load registry
    if not os.path.exists(REGISTRY_FILE):
        return f"❌ Registry not found: {REGISTRY_FILE}"

    excel_handler = ExcelHandler(REGISTRY_FILE)
    df = excel_handler.load_data()

    if df is None or df.empty:
        return "ℹ️ No tasks found in registry."

    team_map = load_team_directory()
    
    sent = 0
    skipped = 0
    errors = 0

    reason_counts = {
        "status_not_active": 0,
        "unassigned_owner": 0,
        "no_email": 0,
        "frequency_not_due": 0,
        "future_created_date": 0,
        "first_reminder": 0,
        "force_first": 0,
        "frequency_ok": 0,
        "date_calculation_error": 0,
        "error": 0,
    }

    now_str = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 Running reminder check on {now_str}")
    print(f"📊 Total tasks: {len(df)}")
    print(f"📧 Team mapping entries: {len(team_map)}")

    for idx, row in df.iterrows():
        task = row.to_dict()
        
        # Get task details for logging
        task_id = task.get('task_id', idx)
        subject = task.get('Subject', 'No Subject')
        owner = task.get('Owner', 'Unknown')
        
        should_send, reason = should_send_reminder(task, force_first=force_first)

        if not should_send:
            skipped += 1
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            print(f"  [{task_id}] Skipped: {reason}")
            continue

        to_email = resolve_owner_email(owner, team_map)
        
        if not to_email:
            skipped += 1
            reason_counts["no_email"] += 1
            print(f"  [{task_id}] ❌ No email for owner '{owner}'")
            continue

        try:
            mail_subject, html = build_email_html(task)
            
            # Send email
            success = send_email(to_email=to_email, subject=mail_subject, html_body=html)
            
            if success:
                sent += 1
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
                
                # Update reminder fields
                df.at[idx, "Last Reminder Date"] = now_str
                df.at[idx, "Last Reminder On"] = now_str
                df.at[idx, "Last Updated"] = now_str
                
                print(f"  [{task_id}] ✅ Sent to {to_email} (Owner: {owner})")
            else:
                errors += 1
                reason_counts["error"] += 1
                print(f"  [{task_id}] ❌ Failed to send to {to_email}")

        except Exception as e:
            errors += 1
            reason_counts["error"] += 1
            print(f"  [{task_id}] ❌ Error: {str(e)}")
            continue

    # Save updates
    if sent > 0:
        try:
            excel_handler.save_data(df)
            print(f"💾 Updated {sent} tasks in registry")
        except Exception as e:
            print(f"❌ Failed to save registry: {str(e)}")
            errors += 1

    # Build summary
    summary = [
        f"## 📊 Reminder Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Tasks Processed:** {len(df)}",
        f"**✅ Reminders Sent:** {sent}",
        f"**⏭️ Tasks Skipped:** {skipped}",
        f"**❌ Errors:** {errors}",
        "",
        "### 📈 Breakdown:",
    ]
    
    # Add reasons
    for reason, count in sorted(reason_counts.items()):
        if count > 0:
            summary.append(f"- {reason}: {count}")
    
    return "\n".join(summary)


# -----------------------------
# Debug Functions
# -----------------------------
def test_team_directory():
    """Test the team directory loading."""
    print("🧪 Testing team directory loading...")
    team_map = load_team_directory()
    
    print(f"\n📋 Team Directory Stats:")
    print(f"Total entries: {len(team_map)}")
    
    if team_map:
        print("\nSample entries:")
        for i, (name, email) in enumerate(list(team_map.items())[:10]):
            print(f"  {i+1}. {name} -> {email}")
    
    # Test some names
    test_names = ["Sunil", "Praveen", "John", "Test"]
    print("\n🔍 Email resolution test:")
    for name in test_names:
        email = resolve_owner_email(name, team_map)
        print(f"  '{name}' -> {email if email else '❌ Not found'}")
    
    return team_map


def check_registry_dates():
    """Check dates in registry for issues."""
    print("🧪 Checking registry dates...")
    
    if not os.path.exists(REGISTRY_FILE):
        print("❌ Registry file not found")
        return
    
    df = pd.read_excel(REGISTRY_FILE)
    print(f"Total tasks: {len(df)}")
    
    # Check for NaT dates
    date_columns = ["Last Reminder Date", "Created On", "Due Date", "Last Updated"]
    
    for col in date_columns:
        if col in df.columns:
            nat_count = df[col].isna().sum()
            print(f"{col}: {nat_count} NaT values out of {len(df)}")
            
            # Show sample of problematic rows
            if nat_count > 0:
                problematic = df[df[col].isna()].head(3)
                print(f"  Sample rows with NaT in {col}:")
                for idx, row in problematic.iterrows():
                    print(f"    Row {idx}: Owner='{row.get('Owner', '')}', Subject='{row.get('Subject', '')}'")


# Quick test if run directly
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Reminder System")
    print("=" * 60)
    
    # Test 1: Team Directory
    team_map = test_team_directory()
    
    print("\n" + "=" * 60)
    
    # Test 2: Registry dates
    check_registry_dates()
    
    print("\n" + "=" * 60)
    print("To send reminders, run in Streamlit app or call:")
    print("  result = send_reminders(force_first=False)")
    print("=" * 60)
