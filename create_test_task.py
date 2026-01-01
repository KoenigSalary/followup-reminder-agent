"""
Test Script: Create a task with past deadline
----------------------------------------------
This will verify the shoddy email system works end-to-end.
"""

import pandas as pd
from datetime import datetime, timedelta

def create_test_task():
    """Add a test task with yesterday's deadline"""
    
    print("🧪 Creating test task with past deadline...")
    
    # Load existing tasks
    df = pd.read_excel("data/tasks_registry.xlsx")
    print(f"   ✓ Loaded {len(df)} existing tasks")
    
    # Create test task with yesterday's deadline
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    test_task = {
        "task_id": "TEST-OVERDUE-001",
        "meeting_id": "TEST-MOM-001",
        "owner": "TestUser",
        "task_text": "Test overdue task for shoddy notification",
        "status": "OPEN",
        "created_on": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "last_reminder_on": None,
        "last_reminder": None,
        "last_reminder_date": None,
        "priority": "HIGH",
        "deadline": yesterday,  # Yesterday - should trigger shoddy!
        "completed_date": None,
        "days_taken": None,
        "performance_rating": None
    }
    
    # Add to dataframe
    df = pd.concat([df, pd.DataFrame([test_task])], ignore_index=True)
    
    # Save
    df.to_excel("data/tasks_registry.xlsx", index=False)
    
    print(f"   ✅ Added test task: {test_task['task_id']}")
    print(f"      Owner: {test_task['owner']}")
    print(f"      Deadline: {yesterday} (OVERDUE)")
    print(f"      Priority: {test_task['priority']}")
    print()
    print("📋 Next Steps:")
    print("   1. Run: python3 run_shoddy_check.py")
    print("   2. Should find 1 overdue task")
    print("   3. Should send shoddy email to HR")
    print("   4. Check data/shoddy_log.xlsx for log entry")
    print()
    print("🗑️  To remove test task after testing:")
    print("   python3 remove_test_task.py")
    print()


if __name__ == "__main__":
    create_test_task()
