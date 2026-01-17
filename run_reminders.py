#!/usr/bin/env python3
"""
Task Reminder System V3 - FIXED VERSION
Sends reminder emails for OPEN tasks based on priority
"""

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# Email configuration from .env
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.office365.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('CEO_AGENT_EMAIL_PASSWORD')
AGENT_SENDER_EMAIL = os.getenv('AGENT_SENDER_EMAIL', SMTP_USERNAME)

# Import user lookup
from utils.user_lookup import find_user_email

# File paths
REGISTRY_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"
TEAM_FILE = BASE_DIR / "data" / "Team_Directory.xlsx"

# Priority-based reminder frequency (days)
REMINDER_FREQUENCY = {
    'URGENT': 1,   # Daily
    'HIGH': 2,     # Every 2 days
    'MEDIUM': 3,   # Every 3 days
    'LOW': 5       # Every 5 days
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

def load_registry():
    """Load task registry"""
    try:
        df = pd.read_excel(REGISTRY_FILE)
        print(f"📂 Loaded registry: {len(df)} rows")
        print(f"📋 Columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        print(f"❌ Error loading registry: {e}")
        return None

def send_reminders():
    """Main reminder logic"""for this task"""
    # Must be OPEN
    status = str(task.get('Status', '')).strip().upper()
    if status not in ['OPEN', 'PENDING', 'IN PROGRESS']:
        return False
    
    # Get priority
    priority = str(task.get('Priority', 'MEDIUM')).strip().upper()
    if priority not in REMINDER_FREQUENCY:
        priority = 'MEDIUM'
    
    # Check last reminder date
    last_reminder = task.get('Last Reminder Date') or task.get('Last Reminder On')
    
    if pd.isna(last_reminder):
        # Never sent - send now
        return True
    
    # Check if enough days have passed
    try:
        if isinstance(last_reminder, str):
            last_date = pd.to_datetime(last_reminder).date()
        else:
            last_date = last_reminder.date() if hasattr(last_reminder, 'date') else last_reminder
        
        days_since = (datetime.now().date() - last_date).days
        frequency = REMINDER_FREQUENCY[priority]
        
        return days_since >= frequency
        
    except Exception as e:
        print(f"   ⚠️  Error checking reminder date: {e}")
        return True  # Send if can't determine

def send_email(to_email, cc_emails, subject, body, task_id):
    """Send email with proper error handling"""
    try:
        # Validate SMTP credentials
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print(f"   ❌ SMTP credentials not configured in .env")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = AGENT_SENDER_EMAIL or SMTP_USERNAME
        msg['To'] = to_email  # Single email address
        msg['Subject'] = subject
        
        # Add CC if present
        if cc_emails and isinstance(cc_emails, list) and len(cc_emails) > 0:
            # Filter out empty strings and validate emails
            valid_cc = [email.strip() for email in cc_emails if email and '@' in str(email)]
            if valid_cc:
                msg['Cc'] = ', '.join(valid_cc)
        
        # Attach body
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Build recipient list (To + CC)
            recipients = [to_email]
            if 'Cc' in msg:
                recipients.extend([email.strip() for email in msg['Cc'].split(',')])
            
            # Send to all recipients
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())
        
        print(f"   ✅ Sent reminder to {to_email} ({task_id})")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send to {to_email}: {e}")
        return False

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
        except:
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
    ⏰ Task Reminder
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
                        <span style="background-color: {priority_color}; 
                                     color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;">
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

def update_reminder_date(task_id):
    """Update Last Reminder Date in registry"""
    try:
        df = pd.read_excel(REGISTRY_FILE)
        
        # Find task
        mask = df['task_id'] == task_id
        if mask.any():
            # Update both possible columns
            if 'Last Reminder Date' in df.columns:
                df.loc[mask, 'Last Reminder Date'] = datetime.now().strftime('%Y-%m-%d')
            if 'Last Reminder On' in df.columns:
                df.loc[mask, 'Last Reminder On'] = datetime.now().strftime('%Y-%m-%d')
            
            # Save
            df.to_excel(REGISTRY_FILE, index=False)
            return True
    except Exception as e:
        print(f"   ⚠️  Could not update reminder date: {e}")
    return False

def main():
    """Main execution"""
    print("=" * 80)
    print("🔔 Task Reminder System V3 - Running")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Check SMTP config
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("❌ ERROR: SMTP credentials not configured!")
        print("   Please set SMTP_USERNAME and CEO_AGENT_EMAIL_PASSWORD in .env file")
        return
    
    print(f"📧 Email: {SMTP_USERNAME}")
    print(f"🔐 Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
    
    # Load data
    df = load_registry()
    if df is None:
        print("❌ Cannot proceed without task registry")
        return
    
    team_df = load_team_directory()
    
    # Get OPEN tasks
    open_tasks = df[df['Status'].str.upper().isin(['OPEN', 'PENDING', 'IN PROGRESS'])]
    print(f"\n📊 Total tasks: {len(df)}")
    print(f"📋 OPEN tasks: {len(open_tasks)}")
    
    if len(open_tasks) == 0:
        print("\n✅ No open tasks to remind!")
        return
    
    # Send reminders
    sent_count = 0
    skipped_count = 0
    
    for idx, task in open_tasks.iterrows():
        task_id = task.get('task_id', 'N/A')
        owner = task.get('Owner', '')
        priority = task.get('Priority', 'MEDIUM')
        
        print(f"\n🔍 Task: {task_id}")
        print(f"   Owner: {owner} | Priority: {priority}")
        
        # Check if should send
        if not should_send_reminder(task, team_df):
            print(f"   ⏭️  Skipping (too soon)")
            skipped_count += 1
            continue
        
        # Get owner email
        owner_email = find_user_email(owner, team_df)
        if not owner_email:
            print(f"   ❌ No email found for {owner}")
            skipped_count += 1
            continue
        
        # Parse CC emails
        cc_emails = []
        cc_field = task.get('CC', '')
        if cc_field and not pd.isna(cc_field):
            # Split by comma or semicolon and validate
            cc_list = str(cc_field).replace(';', ',').split(',')
            cc_emails = [email.strip() for email in cc_list if email.strip() and '@' in email.strip()]
        
        # Create email
        subject = f"⏰ Task Reminder: {task.get('Subject', 'No subject')}"
        body = create_email_body(task)
        
        # Send email
        if send_email(owner_email, cc_emails, subject, body, task_id):
            sent_count += 1
            update_reminder_date(task_id)
        else:
            skipped_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print(f"📧 Sent: {sent_count} | ⏭️ Skipped: {skipped_count}")
    print("=" * 80)

if __name__ == "__main__":
    # this only runs when called directly (python run_reminders.py)
    print(send_reminders())
