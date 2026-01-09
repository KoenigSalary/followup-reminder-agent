import pandas as pd
from datetime import datetime, date, timedelta

def get_next_reminder_date(priority, last_reminder_date, due_date):
    """Calculate next reminder date based on priority and last reminder"""
    
    # Normalize priority
    priority = str(priority).upper() if priority else "MEDIUM"
    
    # Convert last_reminder_date to date object
    if last_reminder_date:
        if isinstance(last_reminder_date, str):
            try:
                last_reminder_date = pd.to_datetime(last_reminder_date).date()
            except:
                last_reminder_date = None
        elif hasattr(last_reminder_date, 'date'):
            last_reminder_date = last_reminder_date.date()
        elif isinstance(last_reminder_date, date):
            pass  # Already a date
        else:
            last_reminder_date = None
    
    # Convert due_date to date object
    if due_date:
        if isinstance(due_date, str):
            try:
                due_date = pd.to_datetime(due_date).date()
            except:
                due_date = None
        elif hasattr(due_date, 'date'):
            due_date = due_date.date()
        elif isinstance(due_date, date):
            pass  # Already a date
        else:
            due_date = None
    
    # If no due date, can't calculate
    if not due_date:
        return None
    
    # Use last reminder as base, or due date if no reminder yet
    base_date = last_reminder_date if last_reminder_date else due_date
    
    # Final check: ensure base_date is a date object
    if not isinstance(base_date, date):
        return None
    
    # Priority-based intervals
    if priority == "URGENT":
        delta = 1
    elif priority == "HIGH":
        delta = 2
    elif priority == "MEDIUM":
        delta = 3
    elif priority == "LOW":
        delta = 7
    else:
        delta = 3
    
    # Return next reminder date
    return base_date + timedelta(days=delta)


class ReminderScheduler:
    def __init__(self, excel_path):
        from utils.excel_handler import ExcelHandler
        from email_processor import EmailProcessor
        
        self.excel_handler = ExcelHandler(excel_path)
        self.email_processor = EmailProcessor()

    def run(self):
        """Check and send reminders for pending tasks"""
        
        df = self.excel_handler.load_data()
        
        if df.empty:
            print("No tasks to process")
            return 0
        
        sent_count = 0
        today = datetime.now().date()
        
        for idx, row in df.iterrows():
            status = str(row.get('Status', row.get('status', ''))).strip().lower()
            
            if status != 'pending':
                continue
            
            due_date = row.get('Due Date', row.get('deadline'))
            if pd.isna(due_date):
                continue
            
            # Convert to date
            if isinstance(due_date, str):
                due_date = pd.to_datetime(due_date).date()
            elif hasattr(due_date, 'date'):
                due_date = due_date.date()
            
            priority = row.get('Priority', row.get('priority', 'Medium'))
            last_reminder = row.get('Last Reminder Date', row.get('last_reminder_date'))
            
            # Check if should send
            if due_date <= today and should_send_based_on_priority(
                priority, due_date, today, last_reminder
            ):
                # Build and send email
                subject = f"[{priority}] Follow-up Due: {row.get('Subject', row.get('task_text', 'Task'))}"
                
                body = f"""
                Subject: {row.get('Subject', row.get('task_text', 'N/A'))}
                Owner: {row.get('Owner', row.get('owner', 'N/A'))}
                Priority: {priority}
                Due Date: {due_date}
                Remarks: {row.get('Remarks', '')}
                """
                
                owner_email = row.get('owner_email', row.get('Owner Email', 'default@example.com'))
                
                # Send email
                self.email_processor.send_email(
                    to_email=owner_email,
                    subject=subject,
                    body=body
                )
                
                sent_count += 1
        
        return sent_count
