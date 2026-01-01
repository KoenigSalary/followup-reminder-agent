"""
Shoddy Manager - With .env Support
-----------------------------------
Loads credentials from .env file automatically.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Config
HR_EMAIL = "hr@koenig-solutions.com"
TASK_FILE = "data/tasks_registry.xlsx"
SHODDY_LOG_FILE = "data/shoddy_log.xlsx"

# Email config from .env
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "praveen.chaudhary@koenig-solutions.com")
SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")
AGENT_SENDER_NAME = os.getenv("AGENT_SENDER_NAME", "Task Followup Agent")


def validate_dataframe_columns(df, required_columns):
    """Validate that DataFrame has all required columns"""
    missing = [col for col in required_columns if col not in df.columns]
    return (len(missing) == 0, missing)


def send_shoddy_email(task_row):
    """Send shoddy notification email to HR"""
    try:
        if not SMTP_PASSWORD:
            print("⚠️  Warning: CEO_AGENT_EMAIL_PASSWORD not found in .env file")
            print("   Add this line to your .env file:")
            print("   CEO_AGENT_EMAIL_PASSWORD=your_password_here")
            return False
        
        # Create email
        msg = MIMEMultipart()
        msg["From"] = f"{AGENT_SENDER_NAME} <{SMTP_USERNAME}>"
        msg["To"] = HR_EMAIL
        msg["Subject"] = f"⚠️ Shoddy Marked - {task_row['owner']}"
        
        # Calculate days overdue
        deadline = pd.to_datetime(task_row["deadline"])
        days_overdue = (datetime.now() - deadline).days
        
        # Email body
        body = f"""
Dear HR Team,

Please mark shoddy against the following person for missing task deadline:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMPLOYEE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {task_row['owner']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task ID: {task_row['task_id']}
Task: {task_row['task_text']}
Priority: {task_row.get('priority', 'MEDIUM')}
Deadline: {deadline.strftime('%Y-%m-%d')}
Days Overdue: {days_overdue} days

Source: {task_row.get('meeting_id', 'N/A')}
Created On: {task_row.get('created_on', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated notification from the Task Followup System.

Regards,
{AGENT_SENDER_NAME}
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"   ✅ Shoddy email sent to {HR_EMAIL} for: {task_row['owner']}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send email: {str(e)}")
        return False


def log_shoddy(task_row):
    """Log shoddy incident to Excel file"""
    try:
        # Prepare shoddy log entry
        deadline = pd.to_datetime(task_row["deadline"])
        days_overdue = (datetime.now() - deadline).days
        
        log_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_row["task_id"],
            "owner": task_row["owner"],
            "task_text": task_row["task_text"],
            "priority": task_row.get("priority", "MEDIUM"),
            "deadline": deadline.strftime("%Y-%m-%d"),
            "days_overdue": days_overdue,
            "meeting_id": task_row.get("meeting_id", "N/A")
        }
        
        # Load existing log or create new
        if Path(SHODDY_LOG_FILE).exists():
            log_df = pd.read_excel(SHODDY_LOG_FILE)
        else:
            log_df = pd.DataFrame(columns=list(log_entry.keys()))
        
        # Append new entry
        log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        log_df.to_excel(SHODDY_LOG_FILE, index=False)
        
        print(f"   ✅ Logged shoddy for: {task_row['owner']}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to log shoddy: {str(e)}")
        return False


def check_overdue_tasks():
    """Check for overdue tasks and send shoddy notifications"""
    print("\n" + "=" * 60)
    print("⏰ CHECKING OVERDUE TASKS")
    print("=" * 60)
    
    try:
        # Load tasks
        if not Path(TASK_FILE).exists():
            print(f"❌ Task file not found: {TASK_FILE}")
            print("   Run migrate_columns.py first!")
            return 0
        
        df = pd.read_excel(TASK_FILE)
        print(f"✓ Loaded {len(df)} total tasks")
        
        # Validate required columns
        required_columns = ["task_id", "task_text", "owner", "status", "deadline", "priority"]
        is_valid, missing = validate_dataframe_columns(df, required_columns)
        
        if not is_valid:
            print(f"❌ Missing required columns: {missing}")
            print("   Run migrate_columns.py to add missing columns!")
            return 0
        
        # Filter OPEN tasks with deadlines
        df = df[df["status"] == "OPEN"]
        print(f"✓ Found {len(df)} OPEN tasks")
        
        df = df[df["deadline"].notna()]
        print(f"✓ Found {len(df)} tasks with deadlines")
        
        # Convert deadline to datetime
        df["deadline"] = pd.to_datetime(df["deadline"])
        
        # Find overdue tasks
        today = datetime.now()
        overdue = df[df["deadline"] < today]
        
        if len(overdue) == 0:
            print("✅ No overdue tasks found!")
            return 0
        
        print(f"\n⚠️  Found {len(overdue)} OVERDUE tasks:")
        
        # Process each overdue task
        shoddy_count = 0
        for idx, task in overdue.iterrows():
            days_overdue = (today - task["deadline"]).days
            print(f"\n   📌 {task['task_id']}")
            print(f"      Owner: {task['owner']}")
            print(f"      Task: {task['task_text'][:50]}...")
            print(f"      Deadline: {task['deadline'].strftime('%Y-%m-%d')}")
            print(f"      Overdue by: {days_overdue} days")
            
            # Send shoddy email
            if send_shoddy_email(task):
                # Log shoddy
                log_shoddy(task)
                shoddy_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Shoddy Check Complete: {shoddy_count} notifications sent")
        print("=" * 60)
        
        return shoddy_count
        
    except Exception as e:
        print(f"❌ Error in check_overdue_tasks: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    # Debug: Show loaded credentials
    print("🔐 Credential Check:")
    print(f"   SMTP Username: {SMTP_USERNAME}")
    print(f"   Password Loaded: {'✅ Yes' if SMTP_PASSWORD else '❌ No'}")
    print(f"   Sender Name: {AGENT_SENDER_NAME}")
    print()
    
    check_overdue_tasks()
