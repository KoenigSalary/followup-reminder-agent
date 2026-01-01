from datetime import datetime
import re
from priority_manager import determine_priority, calculate_deadline

def generate_mom_id():
    today = datetime.now().strftime("%Y%m%d")
    return f"MOM-{today}-001"

# Update parse_bulk_mom function:
def parse_bulk_mom(
    mom_subject: str,
    mom_text: str,
    default_owner: str,
    default_deadline_days: int = None  # NEW PARAMETER
):
    mom_id = generate_mom_id()
    tasks = []
    created_date = datetime.now()
    
    lines = [l.strip() for l in mom_text.split("\n") if l.strip()]
    task_counter = 1

    for line in lines:
        owners = re.findall(r"@(\w+)", line)
        task_text = re.sub(r"@\w+", "", line).strip()

        if not owners:
            owners = [default_owner]

        for owner in owners:
            task_id = f"{mom_id}-T{str(task_counter).zfill(2)}"
            
            # ✨ NEW: Determine priority
            priority = determine_priority(
                task_text=task_text,
                deadline_days=default_deadline_days,
                owner=owner,
                mom_subject=mom_subject
            )
            
            # ✨ NEW: Calculate deadline
            deadline = calculate_deadline(
                created_date=created_date,
                priority=priority,
                custom_days=default_deadline_days
            )
            
            tasks.append({
                "task_id": task_id,
                "task_text": task_text,
                "owner": owner,
                "status": "OPEN",
                "priority": priority,  # ✨ NEW
                "deadline": deadline.strftime("%Y-%m-%d"),  # ✨ NEW
                "meeting_id": mom_id,
                "created_on": created_date.strftime("%Y-%m-%d %H:%M:%S"),
                "last_reminder_date": ""
            })
            task_counter += 1

    return tasks