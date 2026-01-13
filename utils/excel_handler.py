# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime
import os
import warnings

warnings.filterwarnings("ignore")


class ExcelHandler:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path

        # ✅ UPDATED: Added task_id and meeting_id to required columns
        self.required_columns = [
            "task_id",
            "meeting_id",
            "Subject",
            "Owner",
            "CC",
            "Due Date",
            "Remarks",
            "Priority",
            "Status",
            "Created On",
            "Last Updated",
            "Last Reminder Date",
            "Last Reminder On",
            "Completed Date",
            "Auto Reply Sent"
        ]

        self._ensure_file_exists()

    # --------------------------------------------------
    # File handling
    # --------------------------------------------------
    def _ensure_file_exists(self):
        if not os.path.exists(self.excel_path):
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            pd.DataFrame(columns=self.required_columns).to_excel(
                self.excel_path, index=False
            )

    def load_data(self) -> pd.DataFrame:
        try:
            if not os.path.exists(self.excel_path):
                return pd.DataFrame(columns=self.required_columns)

            df = pd.read_excel(self.excel_path)

            # ✅ Ensure all required columns exist
            for col in self.required_columns:
                if col not in df.columns:
                    df[col] = None

            return df

        except Exception as e:
            print(f"❌ Excel load error: {e}")
            return pd.DataFrame(columns=self.required_columns)

    def save_data(self, df: pd.DataFrame) -> bool:
        try:
            df.to_excel(self.excel_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Excel save error: {e}")
            return False

    # --------------------------------------------------
    # Create
    # --------------------------------------------------
    def add_entry(
        self,
        subject: str,
        owner: str,
        due_date,
        remarks: str = "",
        priority: str = "MEDIUM",
        cc: str = "",
        task_id: str = None,  # ✅ NEW: Optional task_id
        meeting_id: str = None  # ✅ NEW: Optional meeting_id
    ):
        """
        Add a new task entry
        
        Args:
            subject: Task subject/title
            owner: Task owner name
            due_date: Due date
            remarks: Additional remarks
            priority: Priority level (URGENT, HIGH, MEDIUM, LOW)
            cc: CC recipients
            task_id: Optional task ID (auto-generated if not provided)
            meeting_id: Optional meeting ID (defaults to MANUAL if not provided)
        """
        
        # ✅ Auto-generate task_id if not provided
        if not task_id:
            today = datetime.now()
            task_id_prefix = f"MAN-{today.strftime('%Y%m%d')}"
            
            df = self.load_data()
            
            if len(df) > 0 and 'task_id' in df.columns:
                today_manual_tasks = df[
                    df['task_id'].astype(str).str.startswith(task_id_prefix, na=False)
                ]
                next_seq = len(today_manual_tasks) + 1
            else:
                next_seq = 1
            
            task_id = f"{task_id_prefix}-{next_seq:03d}"
        
        # ✅ Set meeting_id
        if not meeting_id:
            meeting_id = f"MANUAL-{datetime.now().strftime('%Y%m%d')}"
        
        row = {
            "task_id": task_id,
            "meeting_id": meeting_id,
            "Subject": subject,
            "Owner": owner,
            "CC": cc,
            "Due Date": due_date,
            "Remarks": remarks,
            "Priority": priority,
            "Status": "OPEN",
            "Created On": datetime.now(),
            "Last Updated": datetime.now(),
            "Last Reminder Date": None,
            "Last Reminder On": None,
            "Completed Date": None,
            "Auto Reply Sent": None
        }
        return self.append_row(row)

    def append_row(self, row: dict):
        return self.append_rows([row])

    def append_rows(self, rows: list):
        if not rows:
            return 0

        df = self.load_data()
        new_df = pd.DataFrame(rows)

        # ✅ Ensure all required columns exist in new rows
        for col in self.required_columns:
            if col not in new_df.columns:
                new_df[col] = None

        new_df = new_df[self.required_columns]
        combined = pd.concat([df, new_df], ignore_index=True)
        self.save_data(combined)
        return len(combined)

    # --------------------------------------------------
    # Update (INDEX-BASED — UI SAFE)
    # --------------------------------------------------
    def update_row(self, index: int, updates: dict) -> bool:
        try:
            df = self.load_data()

            if index < 0 or index >= len(df):
                return False

            for col, val in updates.items():
                if col in df.columns:
                    df.at[index, col] = val

            df.at[index, "Last Updated"] = datetime.now()
            self.save_data(df)
            return True

        except Exception as e:
            print(f"❌ update_row error: {e}")
            return False

    def update_status(self, index: int, status: str) -> bool:
        return self.update_row(index, {"Status": status})

    # --------------------------------------------------
    # Soft delete (SAFE)
    # --------------------------------------------------
    def delete_row(self, index: int) -> bool:
        return self.update_row(index, {"Status": "DELETED"})

    # --------------------------------------------------
    # Stats
    # --------------------------------------------------
    def get_total_rows(self) -> int:
        return len(self.load_data())
