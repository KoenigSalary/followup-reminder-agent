"""
Migration Script: Add Priority & Deadline Columns
--------------------------------------------------
Run this ONCE to add missing columns to your Excel files.
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

def migrate_excel_file(file_path, columns_to_add):
    """Add missing columns to Excel file without losing data"""
    print(f"\n📂 Migrating: {file_path}")
    
    if not Path(file_path).exists():
        print(f"   ⚠️  File not found: {file_path}")
        return False
    
    try:
        # Load existing data
        df = pd.read_excel(file_path)
        print(f"   ✓ Loaded {len(df)} rows")
        print(f"   ✓ Existing columns: {list(df.columns)}")
        
        # Add missing columns
        added = []
        for col_name, default_value in columns_to_add.items():
            if col_name not in df.columns:
                df[col_name] = default_value
                added.append(col_name)
                print(f"   ➕ Added column: '{col_name}' (default: {default_value})")
            else:
                print(f"   ✓ Column already exists: '{col_name}'")
        
        # Save back
        df.to_excel(file_path, index=False)
        print(f"   ✅ Saved! Added {len(added)} columns")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🔄 EXCEL SCHEMA MIGRATION")
    print("=" * 60)
    
    # Define migrations
    migrations = {
        "data/tasks_registry.xlsx": {
            "priority": "MEDIUM",
            "deadline": None,
            "completed_date": None,
            "days_taken": None,
            "performance_rating": None
        },
        "data/auto_reply_sent.xlsx": {
            "Priority": "Medium",
            "Deadline": None,
            "Completed On": None,
            "Performance": None
        }
    }
    
    # Run migrations
    success_count = 0
    for file_path, columns in migrations.items():
        if migrate_excel_file(file_path, columns):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Migration Complete: {success_count}/{len(migrations)} files")
    print("=" * 60)
    
    # Set default deadlines for OPEN tasks
    print("\n🗓️  Setting default deadlines for OPEN tasks...")
    try:
        df = pd.read_excel("data/tasks_registry.xlsx")
        
        # Find tasks without deadlines
        open_tasks = df[(df["status"] == "OPEN") & (df["deadline"].isna())]
        
        if len(open_tasks) > 0:
            for idx in open_tasks.index:
                # Get created_on date
                created = df.loc[idx, "created_on"]
                
                # Calculate deadline (7 days from creation or today)
                if pd.notna(created):
                    try:
                        created_date = pd.to_datetime(created)
                        deadline = created_date + timedelta(days=7)
                    except:
                        deadline = datetime.now() + timedelta(days=7)
                else:
                    deadline = datetime.now() + timedelta(days=7)
                
                df.loc[idx, "deadline"] = deadline.strftime("%Y-%m-%d")
            
            # Save
            df.to_excel("data/tasks_registry.xlsx", index=False)
            print(f"   ✅ Set deadlines for {len(open_tasks)} OPEN tasks")
            print(f"      (7 days from creation date)")
        else:
            print("   ✓ All OPEN tasks already have deadlines")
            
    except Exception as e:
        print(f"   ⚠️  Error setting deadlines: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL DONE!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("   1. Run: python3 run_shoddy_check.py")
    print("   2. Verify columns in Excel file")
    print("   3. Restart Streamlit if running")
    print()


if __name__ == "__main__":
    main()
