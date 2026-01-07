import pandas as pd
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

class ExcelHandler:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.required_columns = [
            "Subject", "Owner", "CC", "Due Date", "Remarks", 
            "Status", "Created On", "Last Updated"
        ]
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create Excel file with required columns if it doesn't exist"""
        if not os.path.exists(self.excel_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            
            # Create empty dataframe with required columns
            empty_df = pd.DataFrame(columns=self.required_columns)
            empty_df.to_excel(self.excel_path, index=False)
            print(f"✅ Created new Excel file: {self.excel_path}")
    
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel file with error handling"""
        try:
            if not os.path.exists(self.excel_path):
                return pd.DataFrame(columns=self.required_columns)
            
            df = pd.read_excel(self.excel_path)
            
            # Ensure all required columns exist
            for col in self.required_columns:
                if col not in df.columns:
                    df[col] = None
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading Excel: {str(e)}")
            return pd.DataFrame(columns=self.required_columns)
    
    def save_data(self, df: pd.DataFrame):
        """Save a complete dataframe (overwrites file)"""
        try:
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)
            
            # Ensure all required columns exist
            for col in self.required_columns:
                if col not in df.columns:
                    df[col] = None
            
            df.to_excel(self.excel_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error saving Excel: {str(e)}")
            return False
    
    def append_rows(self, rows: list):
        """Append multiple rows to existing data"""
        try:
            if not rows:
                print("⚠️ No rows to append")
                return 0
            
            existing_df = self.load_data()
            new_df = pd.DataFrame(rows)
            
            # Ensure new rows have all required columns
            for col in self.required_columns:
                if col not in new_df.columns:
                    if col == "Created On" or col == "Last Updated":
                        new_df[col] = datetime.now()
                    else:
                        new_df[col] = None
            
            # Reorder columns to match required order
            new_df = new_df[self.required_columns]
            
            if existing_df.empty:
                combined = new_df
            else:
                combined = pd.concat([existing_df, new_df], ignore_index=True)
            
            self.save_data(combined)
            print(f"✅ Appended {len(rows)} rows. Total: {len(combined)}")
            return len(combined)
            
        except Exception as e:
            print(f"❌ Error in append_rows: {str(e)}")
            raise
    
    def append_row(self, row: dict):
        """Append a single row"""
        return self.append_rows([row])
    
    def add_entry(self, subject: str, owner: str, due_date, remarks: str, cc: str = ""):
        """Add a new entry with all required fields"""
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
        return self.append_row(new_row)
    
    def update_status(self, index: int, status: str):
        """Update status of a specific row"""
        try:
            df = self.load_data()
            if index < len(df):
                df.at[index, "Status"] = status
                df.at[index, "Last Updated"] = datetime.now()
                self.save_data(df)
                return True
            return False
        except Exception:
            return False
    
    def update_auto_reply_status(self, idx, value="Yes"):
        """Update auto-reply status"""
        try:
            df = self.load_data()
            if idx < len(df):
                if "Auto Reply Sent" not in df.columns:
                    df["Auto Reply Sent"] = None
                df.at[idx, "Auto Reply Sent"] = value
                self.save_data(df)
                return True
            return False
        except Exception:
            return False
    
    def get_total_rows(self):
        """Get total number of rows"""
        df = self.load_data()
        return len(df)
