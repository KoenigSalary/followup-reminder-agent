"""
Acknowledgement Manager
Sends performance-based feedback when tasks are completed
"""

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")


# ================= PERFORMANCE EVALUATION =================
def evaluate_performance(
    deadline: datetime,
    completed_date: datetime,
    priority: str
) -> dict:
    """
    Evaluate performance based on completion time
    
    Returns:
        {
            "rating": "excellent" | "good" | "well done" | "completed",
            "emoji": "🌟" | "👍" | "✅" | "✓",
            "message": "Performance message"
        }
    """
    
    # Calculate days difference
    days_diff = (deadline - completed_date).days
    
    # Performance criteria
    if days_diff >= 2:
        # Completed 2+ days early
        return {
            "rating": "excellent",
            "emoji": "🌟",
            "message": "Outstanding performance! Completed well ahead of schedule."
        }
    
    elif days_diff >= 1:
        # Completed 1 day early
        return {
            "rating": "good",
            "emoji": "👍",
            "message": "Good work! Completed ahead of deadline."
        }
    
    elif days_diff >= 0:
        # Completed on time (same day as deadline)
        return {
            "rating": "well done",
            "emoji": "✅",
            "message": "Well done! Completed on time."
        }
    
    else:
        # Completed late (but better than never)
        return {
            "rating": "completed",
            "emoji": "✓",
            "message": "Task completed. Please try to meet deadlines in future."
        }


def send_acknowledgement(
    owner: str,
    owner_email: str,
    task: dict,
    performance: dict
):
    """
    Send acknowledgement email for task completion
    """
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️ Email credentials not configured")
        return False
    
    try:
        msg = EmailMessage()
        msg["From"] = f"Task Followup Agent <{SMTP_USERNAME}>"
        msg["To"] = owner_email
        msg["Subject"] = f"{performance['emoji']} Task Completed - {performance['rating'].title()}"
        
        body = f"""Dear {owner},

{performance['message']}

Task Details:
-------------
Task ID     : {task['task_id']}
Task        : {task['task_text']}
Priority    : {task.get('priority', 'medium').upper()}
Deadline    : {task['deadline']}
Completed   : {task['completed_date']}

Meeting/Source: {task.get('meeting_id', 'N/A')}

Thank you for your dedication and timely completion!

Keep up the great work! {performance['emoji']}

Best regards,
Praveen Chaudhary
CEO, Koenig Solutions

---
Task Followup Agent
"""
        
        msg.set_content(body)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Acknowledgement sent to {owner} - {performance['rating']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send acknowledgement: {e}")
        return False


if __name__ == "__main__":
    # Test acknowledgement system
    from datetime import datetime, timedelta
    
    test_task = {
        "task_id": "MOM-20251231-001-T01",
        "task_text": "Update TDS return filing",
        "priority": "urgent",
        "deadline": datetime.now().date(),
        "completed_date": (datetime.now() - timedelta(days=2)).date(),
        "meeting_id": "MOM-20251231-001"
    }
    
    perf = evaluate_performance(
        datetime.now(),
        datetime.now() - timedelta(days=2),
        "urgent"
    )
    
    print(f"Performance: {perf['rating']} {perf['emoji']}")
    print(f"Message: {perf['message']}")
