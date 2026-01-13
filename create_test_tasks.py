#!/usr/bin/env python3
"""
Quick script to create 5 test tasks for dashboard testing
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from utils.excel_handler import ExcelHandler

def create_test_tasks():
    """Create 5 varied test tasks"""
    
    excel_handler = ExcelHandler('data/tasks_registry.xlsx')
    
    # Test tasks with varied priorities and deadlines
    test_tasks = [
        {
            'subject': 'Prepare Q1 Sales Report',
            'owner': 'Praveen',
            'due_date': datetime.now().date(),  # Today - overdue test
            'priority': 'URGENT',
            'remarks': 'Test overdue alert'
        },
        {
            'subject': 'Review Contract Terms',
            'owner': 'Rajesh',
            'due_date': (datetime.now() + timedelta(days=1)).date(),  # Tomorrow
            'priority': 'HIGH',
            'remarks': 'Test due soon'
        },
        {
            'subject': 'Customer Feedback Analysis',
            'owner': 'Praveen',
            'due_date': (datetime.now() + timedelta(days=3)).date(),
            'priority': 'MEDIUM',
            'remarks': 'Test medium priority'
        },
        {
            'subject': 'Update Marketing Materials',
            'owner': 'Amit',
            'due_date': (datetime.now() + timedelta(days=7)).date(),
            'priority': 'LOW',
            'remarks': 'Test low priority'
        },
        {
            'subject': 'Team Meeting Preparation',
            'owner': 'Praveen',
            'due_date': (datetime.now() + timedelta(days=5)).date(),
            'priority': 'HIGH',
            'remarks': 'Test workload distribution'
        }
    ]
    
    print("=" * 60)
    print("🎯 Creating Test Tasks for Dashboard")
    print("=" * 60)
    
    created_count = 0
    for task in test_tasks:
        try:
            result = excel_handler.add_entry(
                subject=task['subject'],
                owner=task['owner'],
                due_date=task['due_date'],
                remarks=task['remarks'],
                priority=task['priority']
            )
            
            if result:
                created_count += 1
                print(f"✅ Created: {task['subject']}")
                print(f"   Owner: {task['owner']}, Priority: {task['priority']}, Due: {task['due_date']}")
            else:
                print(f"❌ Failed: {task['subject']}")
        except Exception as e:
            print(f"❌ Error creating {task['subject']}: {e}")
    
    print("=" * 60)
    print(f"✅ Successfully created {created_count}/5 test tasks")
    print(f"📊 Total tasks now: {excel_handler.get_total_rows()}")
    print("=" * 60)
    print("\n🎯 Next steps:")
    print("1. Refresh your Streamlit page")
    print("2. Click '📊 Dashboard' in sidebar")
    print("3. You should now see analytics!")
    print("\nOr run: python3 run_reminders.py")
    print("       (Should send reminders for URGENT tasks)")

if __name__ == "__main__":
    create_test_tasks()
