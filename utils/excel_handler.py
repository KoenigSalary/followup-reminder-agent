import pandas as pd
from datetime import datetime
import os


class ExcelHandler:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path

    # ---------------------------------------------
    # Load data
    # ---------------------------------------------
    def load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            return pd.DataFrame()

        try:
            return pd.read_excel(self.excel_path)
        except Exception:
            return pd.DataFrame()

    # ---------------------------------------------
    # Save full dataframe
    # ---------------------------------------------
    def save_data(self, df: pd.DataFrame):
        df.to_excel(self.excel_path, index=False)

    # ---------------------------------------------
    # Generic append row (NEW)
    # ---------------------------------------------
    def append_row(self, row: dict):
        df = self.load_data()
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        self.save_data(df)

    # ---------------------------------------------
    # Add new follow-up entry (Manual)
    # ---------------------------------------------
    def add_entry(
        self,
        subject: str,
        owner: str,
        due_date,
        remarks: str,
        cc: str = ""
    ):
        new_row = {
            "Subject": subject,
            "Owner": owner,
            "CC": cc,
            "Due Date": due_date,
            "Remarks": remarks,
            "Status": "OPEN",
            "Created On": datetime.now(),
            "Last Updated": datetime.now()
        }

        self.append_row(new_row)

    # ---------------------------------------------
    # Update status
    # ---------------------------------------------
    def update_status(self, index: int, status: str):
        df = self.load_data()

        if index >= len(df):
            return

        df.at[index, "Status"] = status
        df.at[index, "Last Updated"] = datetime.now()
        self.save_data(df)

    # ---------------------------------------------
    # Auto reply flag
    # ---------------------------------------------
    def update_auto_reply_status(self, idx, value="Yes"):
        df = self.load_data()
        df.at[idx, "Auto Reply Sent"] = value
        self.save_data(df)
