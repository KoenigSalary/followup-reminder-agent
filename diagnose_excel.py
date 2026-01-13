#!/usr/bin/env python3
"""
Diagnostic Script - Check Excel Data Structure
"""

import pandas as pd
from pathlib import Path

EXCEL_FILE = Path("data/tasks_registry.xlsx")

print("=" * 80)
print("🔍 EXCEL DATA DIAGNOSTICS")
print("=" * 80)

# Load data
df = pd.read_excel(EXCEL_FILE)

print(f"\n📊 Total rows: {len(df)}")
print(f"📊 Total columns: {len(df.columns)}")

print("\n📋 Column Names:")
for i, col in enumerate(df.columns):
    print(f"  {i+1}. '{col}' (type: {df[col].dtype})")

print("\n⚠️  Duplicate Columns:")
duplicates = df.columns[df.columns.duplicated()].tolist()
if duplicates:
    print(f"  ❌ Found: {duplicates}")
else:
    print(f"  ✅ None found")

print("\n📊 Status Distribution:")
if 'Status' in df.columns:
    print(df['Status'].value_counts().to_string())
elif 'status' in df.columns:
    print(df['status'].value_counts().to_string())
else:
    print("  ⚠️  No 'Status' or 'status' column found!")

print("\n📋 Sample Data (first 3 rows):")
print(df.head(3).to_string())

print("\n🔍 Checking for Data Type Issues:")
for col in ['Owner', 'Subject', 'Priority', 'Status']:
    if col in df.columns:
        sample = df[col].iloc[0] if len(df) > 0 else None
        print(f"  {col}: type={type(sample)}, value='{sample}'")
    elif col.lower() in df.columns:
        sample = df[col.lower()].iloc[0] if len(df) > 0 else None
        print(f"  {col.lower()}: type={type(sample)}, value='{sample}'")

print("\n📋 OPEN Tasks Detail:")
if 'Status' in df.columns:
    open_tasks = df[df['Status'].str.upper() == 'OPEN']
elif 'status' in df.columns:
    open_tasks = df[df['status'].str.upper() == 'OPEN']
else:
    open_tasks = pd.DataFrame()

if len(open_tasks) > 0:
    print(open_tasks[['Owner', 'Subject', 'Priority', 'Status', 'Due Date']].to_string())
else:
    print("  ℹ️  No OPEN tasks found")

print("\n" + "=" * 80)
