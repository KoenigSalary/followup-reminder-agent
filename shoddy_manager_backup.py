"""
Shoddy Manager
Handles missed deadline notifications and performance tracking
"""

import os
import smtplib
import pandas as pd
from email.message import EmailMessage
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# ================= CONFIG =================
HR_EMAIL = "hr@koenig-solutions.com"
CC_EMAIL = os.getenv("SMTP_USERNAME", "praveen.chaudhary@koenig-solutions.com")

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")

TASK_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"
TEAM_FILE = BASE_DIR / "data" / "Team_Directory.xlsx"
SHODDY_LOG_FILE = BASE_DIR / "data" / "shoddy_log.xlsx"


# ================= HELPER FUNCTIONS =================
def resolve_email(owner: str) -> str:
    """Resolve owner name to email"""
    if "@" in owner:
        return owner
    
    try:
        df = pd.read_excel(TEAM_FILE)
        match = df[df["Name"].str.lower() == owner.lower()]
        if not match.empty:
            return match.iloc[0]["Email"]
    except Exception as e:
        print(f"Error resolving email for {owner}: {e}")
    
    return None


def init_shoddy_log():
    """Initialize shoddy log file"""
    if not SHODDY_LOG_FILE.exists():
        df = pd.DataFrame(columns=[
            "shoddy_date",
            "task_id",
            "task_text",
            "owner",
            "owner_email",
            "deadline",
            "days_overdue",
            "priority",
            "email_sent",
            "hr_notified"
        ])
        df.to_excel(SHODDY_LOG_FILE, index=False)


def log_shoddy(task: dict, days_overdue: int):
    """Log shoddy incident"""
    init_shoddy_log()
    
    df = pd.read_excel(SHODDY_LOG_FILE)
    
    # Check if already logged
    if not df.empty and task["task_id"] in df["task_id"].values:
        return  # Already logged
    
    new_entry = {
        "shoddy_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": task["task_id"],
        "task_text": task["task_text"],
        "owner": task["owner"],
        "owner_email": task.get("owner_email", ""),
        "deadline": task["deadline"],
        "days_overdue": days_overdue,
        "priority": task.get("priority", "medium"),
        "email_sent": True,
        "hr_notified": True
    }
    
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_excel(SHODDY_LOG_FILE, index=False)


# ================= EMAIL FUNCTIONS =================
def send_shoddy_email(owner: str, owner_email: str, task: dict, days_overdue: int):
    """
    Send shoddy notification to HR
    
    Subject: Shoddy Marked - [Owner Name]
    """
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️ Email credentials not configured")
        return False
    
    try:
        msg = EmailMessage()
        msg["From"] = f"Task Followup Agent <{SMTP_USERNAME}>"
        msg["To"] = HR_EMAIL
        msg["Cc"] = CC_EMAIL
        msg["Subject"] = f"Shoddy Marked - {owner}"
        
        body = f"""Dear HR Team,

Please mark SHODDY against {owner}.

Task Details:
-------------
Task ID     : {task['task_id']}
Task        : {task['task_text']}
Assigned To : {owner}
Email       : {owner_email or 'Not found'}
Priority    : {task.get('priority', 'medium').upper()}
Deadline    : {task['deadline']}
Days Overdue: {days_overdue} days

Meeting/Source: {task.get('meeting_id', 'N/A')}

This task has exceeded its deadline and remains incomplete.

---
This is an automated notification from Task Followup Agent.

Regards,
Task Followup System
"""
        
        msg.set_content(body)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Shoddy email sent for {owner}")
        
        # Log the incident
        task["owner_email"] = owner_email
        log_shoddy(task, days_overdue)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send shoddy email: {e}")
        return False


# ================= MAIN CHECK FUNCTION =================
def check_overdue_tasks():
    """
    Check for overdue tasks and send shoddy emails
    
    Returns:
        Number of shoddy emails sent
    """
    
    df = pd.read_excel(TASK_FILE)
    
    # Filter: Only OPEN tasks with deadlines
    df = df[df["status"] == "OPEN"]
    df = df[df["deadline"].notna()]
    
    if df.empty:
        print("No open tasks with deadlines")
        return 0
    
    today = datetime.now().date()
    sent_count = 0
    
    for _, task in df.iterrows():
        # Parse deadline
        deadline = pd.to_datetime(task["deadline"]).date()
        
        # Check if overdue
        if deadline < today:
            days_overdue = (today - deadline).days
            
            owner = task["owner"]
            owner_email = resolve_email(owner)
            
            if not owner_email:
                print(f"⚠️ No email found for {owner}, skipping shoddy notification")
                continue
            
            task_dict = {
                "task_id": task["task_id"],
                "task_text": task["task_text"],
                "owner": owner,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "meeting_id": task.get("meeting_id", ""),
                "priority": task.get("priority", "medium")
            }
            
            # Send shoddy email
            if send_shoddy_email(owner, owner_email, task_dict, days_overdue):
                sent_count += 1
    
    return sent_count


if __name__ == "__main__":
    print("🔍 Checking for overdue tasks...\n")
    count = check_overdue_tasks()
    print(f"\n📧 Sent {count} shoddy notification(s)")
