"""
Manual Task Entry Processor
Creates new tasks from UI input and sends notification to owner
"""

import pandas as pd
from datetime import datetime
from email_processor import EmailProcessor
from shoddy_manager import get_employee_info

class ManualTaskProcessor:
    def __init__(self):
        self.email_proc = EmailProcessor()
    
    def add_manual_task(self, owner, task_text, priority, deadline_date, excel_handler):
        """
        Add a new manual task and notify the owner via email
        
        Args:
            owner: Owner first name (e.g., 'Sarika', 'Aditya')
            task_text: Task description
            priority: Task priority (URGENT/HIGH/MEDIUM/LOW)
            deadline_date: Deadline as datetime object
            excel_handler: ExcelHandler instance
        
        Returns:
            dict: Task creation result with task_id and status
        """
        
        # Generate unique task ID
        today = datetime.now()
        task_id = f"MAN-{today.strftime('%Y%m%d')}"
        
        # Load existing tasks to get next sequence number
        df = excel_handler.load_data()
        
        # Find existing manual tasks for today
        today_manual_tasks = df[df['Task ID'].str.startswith(task_id)]
        next_seq = len(today_manual_tasks) + 1
        task_id = f"{task_id}-{next_seq:03d}"
        
        # Get owner's full details from Team Directory
        emp_info = get_employee_info(owner)
        
        if not emp_info:
            return {
                'success': False,
                'message': f"❌ Owner '{owner}' not found in Team Directory",
                'task_id': None
            }
        
        owner_email = emp_info['email']
        owner_full_name = emp_info['full_name']
        owner_department = emp_info['department']
        employee_id = emp_info['employee_id']
        
        # Create new task
        new_task = {
            'Task ID': task_id,
            'Meeting ID': 'MANUAL',
            'Owner': owner,  # First name only for consistency
            'Task Text': task_text,
            'Status': 'OPEN',
            'Created On': today.strftime('%Y-%m-%d'),
            'Last Reminder Date': '',
            'Priority': priority,
            'Deadline': deadline_date.strftime('%Y-%m-%d'),
            'Completed Date': '',
            'Days Taken': '',
            'Performance Rating': '',
            'Auto Reply Sent': 'No'
        }
        
        # Append to dataframe
        df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
        
        # Save to Excel
        excel_handler.save_data(df)
        
        # Send notification email to owner
        email_body = f"""Dear {owner_full_name},

A new task has been assigned to you:

📋 Task: {task_text}
🔴 Priority: {priority}
📅 Deadline: {deadline_date.strftime('%Y-%m-%d')}
🆔 Task ID: {task_id}
👤 Employee ID: {employee_id}
🏢 Department: {owner_department}

Please acknowledge and complete by the deadline.

To mark this task as completed, simply reply to this email with:
✅ COMPLETED

Best regards,
Task Follow-up Team
Koenig Solutions
"""
        
        try:
            self.email_proc.send_email(
                to_email=owner_email,  # ✅ Send to owner's email
                subject=f"🆕 New Task Assigned: {task_text[:50]}...",
                body=email_body
            )
            
            email_status = f"✅ Notification sent to {owner_email}"
            
        except Exception as e:
            email_status = f"⚠️ Task created but email failed: {str(e)}"
        
        return {
            'success': True,
            'message': f"✅ Task created successfully!\n{email_status}",
            'task_id': task_id,
            'owner': owner_full_name,
            'owner_email': owner_email,
            'employee_id': employee_id
        }


# Test function
if __name__ == "__main__":
    print("Testing Manual Task Processor...")
    
    # Simulate task creation
    from excel_handler import ExcelHandler
    
    processor = ManualTaskProcessor()
    excel_handler = ExcelHandler()
    
    test_deadline = datetime(2026, 1, 10)
    
    result = processor.add_manual_task(
        owner="Sarika",
        task_text="Review Q4 financial statements",
        priority="HIGH",
        deadline_date=test_deadline,
        excel_handler=excel_handler
    )
    
    print("\n" + "="*70)
    print(result)
    print("="*70)
