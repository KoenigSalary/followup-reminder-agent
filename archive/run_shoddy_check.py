"""
Scheduled Shoddy Check
Run this daily to check overdue tasks
"""

from shoddy_manager import check_overdue_tasks
from datetime import datetime

if __name__ == "__main__":
    print(f"🔍 Running scheduled shoddy check at {datetime.now()}")
    print("=" * 60)
    
    count = check_overdue_tasks()
    
    print("=" * 60)
    print(f"✅ Shoddy check complete. Sent {count} notification(s).")