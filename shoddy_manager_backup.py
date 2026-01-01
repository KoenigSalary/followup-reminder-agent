"""
Shoddy Manager - With Employee ID Support
------------------------------------------
Enhanced version with Employee ID, Full Name, and Department
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
HR_EMAIL = "Praveen.chaudhary@koenig-solutions.com"
TASK_FILE = "data/tasks_registry.xlsx"
SHODDY_LOG_FILE = "data/shoddy_log.xlsx"
TEAM_FILE = "data/Team_Directory.xlsx"

# Email config
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "praveen.chaudhary@koenig-solutions.com")
SMTP_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD")
AGENT_SENDER_NAME = os.getenv("AGENT_SENDER_NAME", "Task Followup Agent")

# Name mapping (fallback)
NAME_MAP = {
    "Aditya": "Aditya Kumar",
    "Anurag": "Anurag Sharma",
    "Praveen": "Praveen Chaudhary",
    "Tax": "Tax Department",
    "Finance": "Finance Team",
    "HR": "HR Department"
}


def get_employee_info(owner):
    """
    Get complete employee information
    
    Args:
        owner: First name, department, or email
    
    Returns:
        dict: {'full_name', 'employee_id', 'department'}
    """
    try:
        # Try Team Directory
        if Path(TEAM_FILE).exists():
            df = pd.read_excel(TEAM_FILE)
            
            # Match by name
            match = df[df["Name"].str.lower().str.contains(owner.lower(), na=False)]
            if not match.empty:
                row = match.iloc[0]
                return {
                    'full_name': row["Name"],
                    'employee_id': row.get("Employee_ID", "N/A"),
                    'department': row.get("Department", "N/A")
                }
            
            # Match by email
            if "@" in owner:
                match = df[df["Email"].str.lower() == owner.lower()]
                if not match.empty:
                    row = match.iloc[0]
                    return {
                        'full_name': row["Name"],
                        'employee_id': row.get("Employee_ID", "N/A"),
                        'department': row.get("Department", "N/A")
                    }
        
        # Fallback
        return {
            'full_name': NAME_MAP.get(owner, owner),
            'employee_id': 'N/A',
            'department': 'N/A'
        }
        
    except Exception as e:
        return {
            'full_name': NAME_MAP.get(owner, owner),
            'employee_id': 'N/A',
            'department': 'N/A'
        }


def validate_dataframe_columns(df, required_columns):
    """Validate DataFrame columns"""
    missing = [col for col in required_columns if col not in df.columns]
    return (len(missing) == 0, missing)


def send_shoddy_email(task_row):
    """Send shoddy notification to HR"""
    try:
        if not SMTP_PASSWORD:
            print("⚠️  Warning: Email password not configured")
            return False
        
        # Get employee info
        emp_info = get_employee_info(task_row['owner'])
        
        # Create email
        msg = MIMEMultipart()
        msg["From"] = f"{AGENT_SENDER_NAME} <{SMTP_USERNAME}>"
        msg["To"] = HR_EMAIL
        msg["Subject"] = f"⚠️ Shoddy Marked - {emp_info['full_name']} ({emp_info['employee_id']})"
        
        # Calculate days overdue
        deadline = pd.to_datetime(task_row["deadline"])
        days_overdue = (datetime.now() - deadline).days
        
        # Email body
        body = f"""
Dear HR Team,

Please mark shoddy against the following employee for missing task deadline:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMPLOYEE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Employee ID: {emp_info['employee_id']}
Full Name: {emp_info['full_name']}
Department: {emp_info['department']}
System ID: {task_row['owner']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task ID: {task_row['task_id']}
Task Description: {task_row['task_text']}
Priority: {task_row.get('priority', 'MEDIUM')}
Original Deadline: {deadline.strftime('%d-%b-%Y')}
Days Overdue: {days_overdue} day(s)

Source Meeting: {task_row.get('meeting_id', 'N/A')}
Task Created On: {task_row.get('created_on', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated notification from the Task Followup System.

Please take appropriate action as per company policy.

For any queries, contact: {SMTP_USERNAME}

Regards,
{AGENT_SENDER_NAME}
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        # Send
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"   ✅ Shoddy email sent for: {emp_info['full_name']} ({emp_info['employee_id']})")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send email: {str(e)}")
        return False


def log_shoddy(task_row):
    """Log shoddy incident"""
    try:
        emp_info = get_employee_info(task_row['owner'])
        deadline = pd.to_datetime(task_row["deadline"])
        days_overdue = (datetime.now() - deadline).days
        
        log_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "employee_id": emp_info['employee_id'],
            "full_name": emp_info['full_name'],
            "department": emp_info['department'],
            "system_id": task_row["owner"],
            "task_id": task_row["task_id"],
            "task_text": task_row["task_text"],
            "priority": task_row.get("priority", "MEDIUM"),
            "deadline": deadline.strftime("%Y-%m-%d"),
            "days_overdue": days_overdue,
            "meeting_id": task_row.get("meeting_id", "N/A")
        }
        
        # Load or create
        if Path(SHODDY_LOG_FILE).exists():
            log_df = pd.read_excel(SHODDY_LOG_FILE)
        else:
            log_df = pd.DataFrame(columns=list(log_entry.keys()))
        
        # Append
        log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
        log_df.to_excel(SHODDY_LOG_FILE, index=False)
        
        print(f"   ✅ Logged shoddy for: {emp_info['full_name']} ({emp_info['employee_id']})")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to log: {str(e)}")
        return False


def check_overdue_tasks():
    """Check for overdue tasks"""
    print("\n" + "=" * 60)
    print("⏰ CHECKING OVERDUE TASKS")
    print("=" * 60)
    
    try:
        if not Path(TASK_FILE).exists():
            print(f"❌ Task file not found: {TASK_FILE}")
            return 0
        
        df = pd.read_excel(TASK_FILE)
        print(f"✓ Loaded {len(df)} total tasks")
        
        # Validate
        required = ["task_id", "task_text", "owner", "status", "deadline", "priority"]
        is_valid, missing = validate_dataframe_columns(df, required)
        
        if not is_valid:
            print(f"❌ Missing columns: {missing}")
            return 0
        
        # Filter
        df = df[df["status"] == "OPEN"]
        print(f"✓ Found {len(df)} OPEN tasks")
        
        df = df[df["deadline"].notna()]
        print(f"✓ Found {len(df)} tasks with deadlines")
        
        df["deadline"] = pd.to_datetime(df["deadline"])
        
        # Find overdue
        today = datetime.now()
        overdue = df[df["deadline"] < today]
        
        if len(overdue) == 0:
            print("✅ No overdue tasks!")
            return 0
        
        print(f"\n⚠️  Found {len(overdue)} OVERDUE tasks:")
        
        # Process
        shoddy_count = 0
        for idx, task in overdue.iterrows():
            emp_info = get_employee_info(task['owner'])
            days_overdue = (today - task["deadline"]).days
            
            print(f"\n   📌 {task['task_id']}")
            print(f"      Employee: {emp_info['full_name']} ({emp_info['employee_id']})")
            print(f"      Task: {task['task_text'][:50]}...")
            print(f"      Overdue: {days_overdue} days")
            
            if send_shoddy_email(task):
                log_shoddy(task)
                shoddy_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Complete: {shoddy_count} notifications sent")
        print("=" * 60)
        
        return shoddy_count
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == "__main__":
    check_overdue_tasks()
