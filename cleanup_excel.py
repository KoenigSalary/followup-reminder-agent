#!/usr/bin/env python3
"""
Excel Cleanup Script - Merge Duplicate Column Sets
Consolidates lowercase and Title Case columns into single standardized set
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

EXCEL_FILE = Path("data/tasks_registry.xlsx")
BACKUP_FILE = Path("data/tasks_registry_BACKUP_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx")

print("=" * 80)
print("🔧 EXCEL CLEANUP - MERGING DUPLICATE COLUMNS")
print("=" * 80)

# Backup original
print(f"\n📦 Creating backup: {BACKUP_FILE.name}")
import shutil
shutil.copy(EXCEL_FILE, BACKUP_FILE)
print("✅ Backup created")

# Load data
print(f"\n📂 Loading: {EXCEL_FILE}")
df = pd.read_excel(EXCEL_FILE)
print(f"   Total rows: {len(df)}")
print(f"   Total columns: {len(df.columns)}")

# Define canonical schema (Title Case)
CANONICAL_COLUMNS = {
    'task_id': 'task_id',
    'meeting_id': 'meeting_id',
    'owner': 'Owner',
    'Owner': 'Owner',
    'task_text': 'Subject',
    'Subject': 'Subject',
    'status': 'Status',
    'Status': 'Status',
    'priority': 'Priority',
    'Priority': 'Priority',
    'deadline': 'Due Date',
    'Due Date': 'Due Date',
    'cc': 'CC',
    'CC': 'CC',
    'created_on': 'Created On',
    'Created On': 'Created On',
    'last_reminder_date': 'Last Reminder Date',
    'Last Reminder Date': 'Last Reminder Date',
    'last_reminder_on': 'Last Reminder On',
    'completed_date': 'Completed Date',
    'Completed Date': 'Completed Date',
    'Remarks': 'Remarks',
    'Last Updated': 'Last Updated',
    'Auto Reply Sent': 'Auto Reply Sent'
}

print("\n🔄 Merging duplicate columns...")

# Create clean dataframe
clean_df = pd.DataFrame()

# Merge each column set
for old_col, new_col in CANONICAL_COLUMNS.items():
    if old_col in df.columns:
        if new_col not in clean_df.columns:
            clean_df[new_col] = df[old_col]
        else:
            # Merge: fill NaN values from alternate column
            mask = clean_df[new_col].isna()
            clean_df.loc[mask, new_col] = df.loc[mask, old_col]

# Add remaining columns not in mapping
for col in df.columns:
    if col not in CANONICAL_COLUMNS and col not in clean_df.columns:
        clean_df[col] = df[col]

# Remove rows where ALL key columns are NaN
key_columns = ['Owner', 'Subject', 'Status']
clean_df = clean_df.dropna(subset=key_columns, how='all')

# Fill missing Status with OPEN
if 'Status' in clean_df.columns:
    clean_df['Status'] = clean_df['Status'].fillna('OPEN')

# Ensure required columns exist
required = ['Subject', 'Owner', 'CC', 'Due Date', 'Remarks', 'Priority', 'Status', 'Created On', 'Last Updated']
for col in required:
    if col not in clean_df.columns:
        clean_df[col] = None

# Reorder columns
final_columns = ['task_id', 'meeting_id', 'Owner', 'Subject', 'Status', 'Priority', 
                 'Due Date', 'CC', 'Remarks', 'Created On', 'Last Updated', 
                 'Last Reminder Date', 'Last Reminder On', 'Completed Date', 
                 'Auto Reply Sent']

# Add any remaining columns
for col in clean_df.columns:
    if col not in final_columns:
        final_columns.append(col)

# Select only existing columns
final_columns = [col for col in final_columns if col in clean_df.columns]
clean_df = clean_df[final_columns]

print(f"\n✅ Merge complete!")
print(f"   Rows before: {len(df)}")
print(f"   Rows after: {len(clean_df)} (empty rows removed)")
print(f"   Columns before: {len(df.columns)}")
print(f"   Columns after: {len(clean_df.columns)}")

print(f"\n📋 New column structure:")
for i, col in enumerate(clean_df.columns, 1):
    print(f"   {i}. {col}")

# Save cleaned file
print(f"\n💾 Saving cleaned file...")
clean_df.to_excel(EXCEL_FILE, index=False)
print(f"✅ Saved: {EXCEL_FILE}")

# Show summary
print(f"\n📊 Status Distribution (After Cleanup):")
if 'Status' in clean_df.columns:
    print(clean_df['Status'].value_counts().to_string())

print(f"\n📋 Sample Data (First 3 rows):")
display_cols = ['Owner', 'Subject', 'Status', 'Priority', 'Due Date']
display_cols = [c for c in display_cols if c in clean_df.columns]
if len(clean_df) > 0:
    print(clean_df[display_cols].head(3).to_string())
else:
    print("   (No data)")

print("\n" + "=" * 80)
print("✅ CLEANUP COMPLETE!")
print("=" * 80)
print(f"\n📝 Summary:")
print(f"   • Backup saved: {BACKUP_FILE}")
print(f"   • Duplicate columns merged")
print(f"   • Empty rows removed")
print(f"   • Standardized to Title Case schema")
print(f"\n🚀 Next Steps:")
print(f"   1. Run: python3 diagnose_excel.py (verify cleanup)")
print(f"   2. Run: streamlit run streamlit_app.py")
print(f"   3. Add new tasks (old data was cleaned up)")
print()
