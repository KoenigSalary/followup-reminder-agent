"""
Remove Test Task
----------------
Removes the test overdue task after testing is complete.
"""

import pandas as pd

def remove_test_task():
    """Remove test tasks from registry"""
    
    print("🗑️  Removing test tasks...")
    
    # Load tasks
    df = pd.read_excel("data/tasks_registry.xlsx")
    print(f"   ✓ Loaded {len(df)} tasks")
    
    # Find test tasks
    test_tasks = df[df["task_id"].str.startswith("TEST-", na=False)]
    print(f"   ✓ Found {len(test_tasks)} test task(s)")
    
    if len(test_tasks) > 0:
        # Remove test tasks
        df = df[~df["task_id"].str.startswith("TEST-", na=False)]
        
        # Save
        df.to_excel("data/tasks_registry.xlsx", index=False)
        print(f"   ✅ Removed {len(test_tasks)} test task(s)")
        print(f"   ✓ Remaining tasks: {len(df)}")
    else:
        print("   ℹ️  No test tasks found")
    
    print()


if __name__ == "__main__":
    remove_test_task()
