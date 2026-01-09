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
        """Initialize email processor"""
        self.email_proc = EmailProcessor()
    
    def add_manual_task(
        self,
        owner,
        task_text,
        priority,
        deadline_date,
        cc,
        excel_handler
    ):
        """
        Add a manual task and send notification email
        
        Args:
            owner: First name of task owner
            task_text: Task description
            priority: Priority level (URGENT, HIGH, MEDIUM, LOW)
            deadline_date: Deadline date
            cc: CC recipients
            excel_handler: ExcelHandler instance
        
        Returns:
            dict with success, message, task_id, owner, owner_email
        """
        
        # Generate unique task ID
        today = datetime.now()
        task_id_prefix = f"MAN-{today.strftime('%Y%m%d')}"
        
        # Load existing tasks to get next sequence number
        df = excel_handler.load_data()
        
        # Find existing manual tasks for today
        if len(df) > 0 and 'task_id' in df.columns:
            today_manual_tasks = df[df['task_id'].astype(str).str.startswith(task_id_prefix, na=False)]
            next_seq = len(today_manual_tasks) + 1
        else:
            next_seq = 1
            
        task_id = f"{task_id_prefix}-{next_seq:03d}"
        
        # Get owner's full details from Team Directory
        emp_info = get_employee_info(owner)
        
        if not emp_info:
            return {
                'success': False,
                'message': f"❌ Owner '{owner}' not found in Team Directory",
                'task_id': None,
                'owner': owner,
                'owner_email': 'N/A'
            }
        
        owner_email = emp_info['email']
        owner_full_name = emp_info['full_name']
        owner_department = emp_info['department']
        employee_id = emp_info['employee_id']
        
        # Create new task
        new_task = {
            "task_id": task_id,
            "meeting_id": "MANUAL",
            "owner": owner,
            "task_text": task_text,
            "priority": priority,
            "deadline": deadline_date,
            "cc": cc,
            "status": "OPEN",
            "created_on": datetime.now(),
            "last_reminder_date": None
        }
        
        # Append to Excel
        excel_handler.append_row(new_task)
        
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
        
        email_status = "Email not sent"
        
        try:
            # Use corrected parameter order: to_email, subject, body
            self.email_proc.send_email(
                to_email=owner_email,
                subject=f"🆕 New Task Assigned: {task_text[:50]}...",
                body=email_body
            )
            
            email_status = f"✅ Notification sent to {owner_email}"
            
        except Exception as e:
            email_status = f"⚠️ Task created but email failed: {str(e)}"
        
        # Return with all required fields
        return {
            "success": True,
            "message": f"Task added successfully. {email_status}",
            "task_id": task_id,
            "owner": owner,
            "employee_id": employee_id,
            "owner_email": owner_email
        }
