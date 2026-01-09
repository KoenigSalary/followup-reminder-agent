#!/usr/bin/env python3
"""
Automated Task Reminder System V2
Sends reminders based on priority, deadline proximity, and last reminder date
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from email_processor import EmailProcessor
from user_lookup import find_user_email, find_user_info

# Paths
BASE_DIR = Path(__file__).resolve().parent
TASK_REGISTRY = BASE_DIR / "data" / "tasks_registry.xlsx"
TEAM_DIRECTORY = BASE_DIR / "data" / "Team_Directory.xlsx"

def should_send_reminder(task, today):
    """
    Improved logic: Start reminders based on deadline proximity
    """
    priority = str(task.get('priority', 'MEDIUM')).strip().lower()
    deadline = task.get('deadline')
    last_reminder = task.get('last_reminder_date')
    
    # Parse deadline
    if pd.isna(deadline):
        return False
    
    if isinstance(deadline, str):
        deadline = pd.to_datetime(deadline).date()
    elif hasattr(deadline, 'date'):
        deadline = deadline.date()
    
    # Calculate days until deadline
    days_until_deadline = (deadline - today).days
    
    # Priority-based logic
    if priority in ['urgent']:
        should_start = days_until_deadline <= 10  # Start immediately
        interval = 1  # Daily
    elif priority in ['high']:
        should_start = days_until_deadline <= 7  # Start with 7 days left
        interval = 2  # Every 2 days
    elif priority in ['medium']:
        should_start = days_until_deadline <= 7  # Start with 7 days left
        interval = 3  # Every 3 days
    else:  # low
        should_start = days_until_deadline <= 10  # Start with 10 days left
        interval = 5  # Every 5 days
    
    if not should_start:
        return False
    
    # Check last reminder date
    if pd.isna(last_reminder):
        return True  # Never reminded, send now
    
    if isinstance(last_reminder, str):
        last_reminder = pd.to_datetime(last_reminder).date()
    elif hasattr(last_reminder, 'date'):
        last_reminder = last_reminder.date()
    
    # Check interval
    days_since_last = (today - last_reminder).days
    
    return days_since_last >= interval

def get_owner_email(owner, team_df=None):
    """Find owner's email using UserLookup (supports users.xlsx)"""
    return find_user_email(owner)

def send_task_reminder(task, owner_email, email_processor):
    """Send reminder email with full user context"""
    from user_lookup import find_user_info
    
    subject = f"⏰ Task Reminder: {task['task_text'][:50]}"
    
    # Get full user info
    user_info = find_user_info(task['owner'])
    
    priority_emoji = {
        'urgent': '🔴', 'URGENT': '🔴',
        'high': '🟠', 'HIGH': '🟠',
        'medium': '🟡', 'MEDIUM': '🟡',
        'low': '🟢', 'LOW': '🟢'
    }
    emoji = priority_emoji.get(task['priority'], '🟡')
    
    # Build email body with user context
    owner_name = user_info['full_name'] if user_info else task['owner']
    dept = user_info['department'] if user_info else 'N/A'
    emp_id = user_info['employee_id'] if user_info else 'N/A'
    
    body = f"""Dear {owner_name},

This is a reminder about your task:

📋 Task: {task['task_text']}
{emoji} Priority: {task['priority'].upper()}
📅 Deadline: {task['deadline']}
🆔 Task ID: {task['task_id']}
👤 Employee ID: {emp_id}
🏢 Department: {dept}

Please complete by the deadline.

Best regards,
Task Follow-up Team
"""
    
    email_processor.send_email(owner_email, subject, body)

def main():
    """Main execution"""
    print("=" * 80)
    print("🔔 Task Reminder System V2 - Running")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Load data
    try:
        tasks_df = pd.read_excel(TASK_REGISTRY)
        team_df = pd.read_excel(TEAM_DIRECTORY)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    print(f"📊 Total tasks: {len(tasks_df)}")
    
    # Filter OPEN tasks
    # Handle both 'status' and 'Status' column names
    status_col = 'status' if 'status' in tasks_df.columns else 'Status'
    open_tasks = tasks_df[tasks_df[status_col].str.upper() == 'OPEN']
    print(f"📋 OPEN tasks: {len(open_tasks)}")
    
    if len(open_tasks) == 0:
        print("✅ No OPEN tasks")
        return
    
    email_processor = EmailProcessor()
    today = datetime.now().date()
    
    sent_count = 0
    skipped_count = 0
    
    for idx, task in open_tasks.iterrows():
        task_id = task['task_id']
        owner = task['owner']
        priority = task.get('priority', 'MEDIUM')
        
        print(f"\n🔍 Task: {task_id}")
        print(f"   Owner: {owner} | Priority: {priority}")
        
        if not should_send_reminder(task, today):
            print(f"   ⏭️  Skipped (not due yet)")
            skipped_count += 1
            continue
        
        owner_email = get_owner_email(owner, team_df)
        
        if not owner_email:
            print(f"   ⚠️  No email for {owner}")
            skipped_count += 1
            continue
        
        try:
            send_task_reminder(task, owner_email, email_processor)
            
            tasks_df.at[idx, "last_reminder_date"] = pd.Timestamp(today)
            tasks_df.at[idx, 'last_reminder_on'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"   ✅ Sent to {owner_email}")
            sent_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            skipped_count += 1
    
    # Save
    if sent_count > 0:
        try:
            tasks_df.to_excel(TASK_REGISTRY, index=False, engine='openpyxl')
            print(f"\n💾 Registry updated")
        except Exception as e:
            print(f"\n❌ Save failed: {e}")
    
    print("\n" + "=" * 80)
    print(f"📧 Sent: {sent_count} | ⏭️ Skipped: {skipped_count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
