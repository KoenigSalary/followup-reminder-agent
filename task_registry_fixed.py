"""
Task Registry - Fixed append_tasks Function
--------------------------------------------
Properly saves tasks to tasks_registry.xlsx
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

TASK_FILE = "data/tasks_registry.xlsx"

def append_tasks(tasks):
    """
    Append tasks to tasks_registry.xlsx
    
    Args:
        tasks: List of task dictionaries with keys:
               - task_id, meeting_id, owner, task_text, status,
               - priority, deadline, etc.
    
    Returns:
        int: Number of tasks appended
    """
    try:
        print(f"📝 Attempting to save {len(tasks)} tasks to {TASK_FILE}...")
        
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)
        
        # Load existing tasks or create new DataFrame
        if Path(TASK_FILE).exists():
            df_existing = pd.read_excel(TASK_FILE)
            print(f"   ✓ Loaded {len(df_existing)} existing tasks")
        else:
            df_existing = pd.DataFrame()
            print("   ℹ Creating new tasks registry file")
        
        # Convert tasks to rows
        new_rows = []
        for task in tasks:
            row = {
                "task_id": task.get("task_id"),
                "meeting_id": task.get("meeting_id"),
                "owner": task.get("owner"),
                "task_text": task.get("task_text"),
                "status": task.get("status", "OPEN"),
                "created_on": task.get("created_on", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "last_reminder_on": task.get("last_reminder_on"),
                "last_reminder": task.get("last_reminder"),
                "last_reminder_date": task.get("last_reminder_date"),
                "priority": task.get("priority", "MEDIUM"),
                "deadline": task.get("deadline"),
                "completed_date": task.get("completed_date"),
                "days_taken": task.get("days_taken"),
                "performance_rating": task.get("performance_rating")
            }
            new_rows.append(row)
        
        # Create DataFrame from new tasks
        df_new = pd.DataFrame(new_rows)
        print(f"   ✓ Created DataFrame with {len(df_new)} new tasks")
        
        # Combine with existing
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        print(f"   ✓ Combined: {len(df_combined)} total tasks")
        
        # Save to Excel
        df_combined.to_excel(TASK_FILE, index=False)
        print(f"   ✅ Saved {len(tasks)} tasks to {TASK_FILE}")
        
        # Verify save
        df_verify = pd.read_excel(TASK_FILE)
        print(f"   ✓ Verified: {len(df_verify)} tasks in file")
        
        return len(tasks)
        
    except Exception as e:
        print(f"   ❌ Error in append_tasks: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


# Test function
if __name__ == "__main__":
    # Test with sample tasks
    test_tasks = [
        {
            "task_id": "TEST-001",
            "meeting_id": "TEST-MOM-001",
            "owner": "Aditya",
            "task_text": "Review Q1 budget",
            "status": "OPEN",
            "priority": "URGENT",
            "deadline": "2026-01-03"
        },
        {
            "task_id": "TEST-002",
            "meeting_id": "TEST-MOM-001",
            "owner": "Anurag",
            "task_text": "Update team directory",
            "status": "OPEN",
            "priority": "URGENT",
            "deadline": "2026-01-03"
        }
    ]
    
    print("\n🧪 Testing append_tasks function...")
    result = append_tasks(test_tasks)
    print(f"\n✅ Test complete! {result} tasks saved.")
    
    # Verify
    df = pd.read_excel(TASK_FILE)
    print(f"\n📊 Current registry:")
    print(df[["task_id", "owner", "task_text", "priority"]].tail(5))
