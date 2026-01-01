from datetime import timedelta
from datetime import datetime
from email_processor import EmailProcessor
from utils.excel_handler import ExcelHandler
from datetime import date, timedelta
import pandas as pd

def should_send_based_on_priority(priority: str, due_date, today, last_reminder_date=None):
    priority = str(priority).strip().lower()

    # Never remind before due date
    if today < due_date:
        return False

    # If never reminded before → send immediately
    if not last_reminder_date:
        return True

    days_since_last = (today - last_reminder_date).days

    if priority == "high":
        return days_since_last >= 2     # alternate day

    if priority == "medium":
        return days_since_last >= 3     # every 3 days

    if priority == "low":
        return days_since_last >= 7     # weekly

    return False

def get_next_reminder_date(priority, last_reminder_date, due_date):
    """
    Returns the next reminder date based on priority.
    Handles empty / NaN dates safely.
    """

    # Normalize priority
    priority = str(priority).strip().lower()

    # Normalize dates
    if pd.isna(last_reminder_date):
        last_reminder_date = None

    if pd.isna(due_date):
        return None

    # Convert to date objects
    if hasattr(due_date, "date"):
        due_date = due_date.date()

    if last_reminder_date and hasattr(last_reminder_date, "date"):
        last_reminder_date = last_reminder_date.date()

    # Decide base date
    base_date = last_reminder_date or due_date

    # Cadence
    if priority == "high":
        delta = 2
    elif priority == "medium":
        delta = 3
    elif priority == "low":
        delta = 7
    else:
        delta = 3  # safe default

    return base_date + timedelta(days=delta)

class ReminderScheduler:
    def __init__(self, excel_path: str):
        self.excel_handler = ExcelHandler(excel_path)
        self.email_processor = EmailProcessor()

    def run(self) -> int:
        df = self.excel_handler.load_data()
        if df.empty:
            return 0

        today = datetime.now().date()
        sent_count = 0

        for _, row in df.iterrows():
            status = str(row.get("Status", "")).strip().lower()
            if status != "pending":
                continue

            due_date = row.get("Due Date")
            if not due_date:
                continue

            # Normalize Excel / pandas date
            if hasattr(due_date, "date"):
                due_date = due_date.date()

            priority = row.get("Priority", "Medium")

            if due_date <= today and should_send_based_on_priority(priority, due_date, today):
                subject = f"[{priority.upper()}] Follow-up Due: {row.get('Subject')}"
                body = f"""
Hello,

This is a reminder for the Pending Task:

Subject  : {row.get('Subject')}
Owner    : {row.get('Owner')}
Priority : {priority}
Due Date : {due_date}
Remarks  : {row.get('Remarks')}

Regards,
Task Followup Team
"""
                self.email_processor.send_email(subject, body)
                sent_count += 1

        return sent_count

