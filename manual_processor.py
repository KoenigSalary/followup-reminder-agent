from utils.excel_handler import ExcelHandler
from datetime import datetime


class ManualProcessor:
    def __init__(self, excel_path: str):
        self.excel_handler = ExcelHandler(excel_path)

    def add_entry(self, subject, owner, due_date, remarks):
        self.excel_handler.add_entry(
            subject=subject,
            owner=owner,
            due_date=due_date,
            remarks=remarks
        )
