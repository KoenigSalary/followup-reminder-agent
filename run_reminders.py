# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Task Reminder System V3 - FIXED VERSION
Sends reminder emails for OPEN tasks based on priority
"""

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import sys
import os

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

def _get_secret(key: str, default=None):
    """Read from OS env first, then Streamlit secrets (Cloud)."""
    # Try Streamlit secrets first (better for cloud deployment)
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val is not None and str(val).strip() != '':
            return val
    except Exception:
        pass
    
    # Fallback to environment variable
    val = os.getenv(key)
    if val is not None and str(val).strip() != '':
        return val
    
    return default

# Email configuration
SMTP_SERVER = _get_secret('SMTP_SERVER', 'smtp.office365.com')
SMTP_PORT = int(_get_secret('SMTP_PORT', 587))
SMTP_USERNAME = _get_secret('SMTP_USERNAME')
SMTP_PASSWORD = _get_secret('CEO_AGENT_EMAIL_PASSWORD')
AGENT_SENDER_EMAIL = _get_secret('AGENT_SENDER_EMAIL', SMTP_USERNAME)

# File paths
REGISTRY_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"
TEAM_FILE = BASE_DIR / "data" / "Team_Directory.xlsx"

# Priority-based reminder frequency (days)
REMINDER_FREQUENCY = {
    'URGENT': 0,
    'HIGH': 0,
    'MEDIUM': 0,
    'LOW': 0
}

def load_team_directory():
    """Load team directory"""
    try:
        if TEAM_FILE.exists():
            df = pd.read_excel(TEAM_FILE)
            print(f"📂 Loaded team directory: {len(df)} rows")
            return df
    except Exception as e:
        print(f"⚠️  Could not load team directory: {e}")
    return None

def find_user_email(owner_name, team_df=None):
    """Find user email from team directory or construct default"""
    if team_df is not None and not team_df.empty:
        try:
            match = team_df[team_df['Name'].str.contains(owner_name, case=False, na=False)]
            if not match.empty:
                email = match.iloc[0].get('Email')
                if email and '@' in str(email):
                    return str(email).strip()
        except Exception:
            pass
    
    # Fallback: construct email
    return f"{owner_name.lower().replace(' ', '.')}@koenig-solutions.com"

def create_email_body(task):
    """Create HTML email body"""
    task_id = task.get('task_id', 'N/A')
    subject = task.get('Subject', 'No subject')
    priority = task.get('Priority', 'MEDIUM')
    due_date = task.get('Due Date', 'N/A')
    owner = task.get('Owner', 'N/A')
    remarks = task.get('Remarks', '')
    
    # Format due date
    if not pd.isna(due_date):
        try:
            if isinstance(due_date, str):
                due_date = pd.to_datetime(due_date).strftime('%d-%b-%Y')
            else:
                due_date = due_date.strftime('%d-%b-%Y')
        except Exception:
            pass
    
    # Priority color
    priority_colors = {
        'URGENT': '#d32f2f',
        'HIGH': '#ff9800',
        'MEDIUM': '#ffc107',
        'LOW': '#4caf50'
    }
    priority_color = priority_colors.get(priority, '#ffc107')
    
    html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 10px;">
            \u23f0 Task Reminder
        </h2>
        
        <p>Dear <strong>{owner}</strong>,</p>
        
        <p>This is a reminder for the following task assigned to you:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f5f5f5;">
                <td style="padding: 10px; border: 1px solid #ddd; width: 30%; font-weight: bold;">Task ID:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{task_id}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Subject:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{subject}</td>
            </tr>
            <tr style="background-color: #f5f5f5;">
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Priority:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <span style="background-color: {priority_color}; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">
                        {priority}
                    </span>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Due Date:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{due_date}</td>
            </tr>
        </table>
        
        {f'<p><strong>Remarks:</strong> {remarks}</p>' if remarks and not pd.isna(remarks) else ''}
        
        <p style="margin-top: 20px;">
            <strong>Action Required:</strong> Please provide an update on this task at your earliest convenience.
        </p>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            This is an automated reminder from the Follow-up & Reminder Team.<br>
            © 2026 Koenig Solutions
        </p>
    </div>
</body>
</html>
"""
    return html

def send_email(to_email, cc_emails, subject, body, task_id):
    """Send email with proper error handling"""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print(f"   ❌ SMTP credentials not configured")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['From'] = AGENT_SENDER_EMAIL or SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if cc_emails and isinstance(cc_emails, list):
            valid_cc = [email.strip() for email in cc_emails if email and '@' in str(email)]
            if valid_cc:
                msg['Cc'] = ', '.join(valid_cc)
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            recipients = [to_email]
            if 'Cc' in msg:
                recipients.extend([e.strip() for e in msg['Cc'].split(',')])
            
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())
        
        print(f"   ✅ Sent to {to_email} ({task_id})")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send to {to_email}: {e}")
        return False

def send_reminders():
    """Main reminder logic for sending task reminders."""
    from utils.excel_handler import ExcelHandler
    
    if not REGISTRY_FILE.exists():
        return "❌ Registry file not found"
    
    excel_handler = ExcelHandler(str(REGISTRY_FILE))
    df = excel_handler.load_data()
    
    if df.empty:
        return "No tasks found in registry"
    
    team_df = load_team_directory()
    sent_count = 0
    skipped_count = 0
    
    for idx, row in df.iterrows():
        task = row.to_dict()
        
        status = str(task.get('Status', '')).strip().upper()
        if status not in ['OPEN', 'PENDING', 'IN PROGRESS']:
            skipped_count += 1
            continue
        
        priority = str(task.get('Priority', 'MEDIUM')).strip().upper()
        if priority not in REMINDER_FREQUENCY:
            priority = 'MEDIUM'
        
        last_reminder = task.get('Last Reminder Date') or task.get('Last Reminder On')
        
        should_send = False
        if pd.isna(last_reminder) or not last_reminder:
            should_send = True
        else:
            try:
                if isinstance(last_reminder, str):
                    last_date = pd.to_datetime(last_reminder).date()
                else:
                    last_date = last_reminder.date() if hasattr(last_reminder, 'date') else last_reminder
                
                days_since = (datetime.now().date() - last_date).days
                frequency = REMINDER_FREQUENCY[priority]
                should_send = days_since >= frequency
                
            except Exception as e:
                print(f"   ⚠️  Error checking date: {e}")
                should_send = True
        
        if should_send:
            try:
                owner = str(task.get('Owner', '')).strip()
                subject_text = str(task.get('Subject', '')).strip()
                
                if owner and owner.lower() != 'unassigned':
                    owner_email = find_user_email(owner, team_df)
                    
                    cc_field = task.get('CC', '')
                    cc_emails = []
                    if cc_field and not pd.isna(cc_field):
                        cc_list = str(cc_field).replace(';', ',').split(',')
                        cc_emails = [e.strip() for e in cc_list if e.strip() and '@' in e.strip()]
                    
                    email_subject = f"\u23f0 Task Reminder: {subject_text}"
                    email_body = create_email_body(task)
                    
                    if send_email(owner_email, cc_emails, email_subject, email_body, task.get('task_id', 'N/A')):
                        excel_handler.update_row(idx, {
                            'Last Reminder Date': datetime.now().strftime('%Y-%m-%d'),
                            'Last Reminder On': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        sent_count += 1
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                print(f"❌ Error sending: {e}")
                skipped_count += 1
        else:
            skipped_count += 1
    
    return f"Sent {sent_count} reminders, skipped {skipped_count} tasks"

if __name__ == "__main__":
    print(send_reminders())
