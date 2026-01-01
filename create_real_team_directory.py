#!/usr/bin/env python3
"""
Create Team Directory with Real Koenig Solutions Data
"""

import pandas as pd
from pathlib import Path

# Ensure data directory exists
Path('data').mkdir(exist_ok=True)

# Real Koenig Solutions Team Data
team_data = [
    # A&F Team
    {'Employee_ID': 'EMP1086', 'Name': 'Sunil Kushwaha', 'Email': 'Sunilkumar.kushwaha@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP3638', 'Name': 'Sarika Gupta', 'Email': 'sarika.gupta@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP2627', 'Name': 'Ritika Bhalla', 'Email': 'ritika.bhalla@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP3411', 'Name': 'Tripti Sharma', 'Email': 'tripti@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP3412', 'Name': 'Jony Saini', 'Email': 'jony.saini@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP521', 'Name': 'Anurag Chauhan', 'Email': 'anurag.chauhan@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP2411', 'Name': 'Ajay Rawat', 'Email': 'ajay.rawat@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP3306', 'Name': 'Aditya Singh', 'Email': 'aditya.singh@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP2211', 'Name': 'Jatin Khurana', 'Email': 'jatin.khurana@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    {'Employee_ID': 'EMP004', 'Name': 'Praveen Kumar', 'Email': 'praveen.chaudhary@koenig-solutions.com', 'Department': 'A&F', 'Type': 'Individual'},
    
    # Operations Team
    {'Employee_ID': 'EMP3201', 'Name': 'Vipin Nautiyal', 'Email': 'vipin.nautiyal@koenig-solutions.com', 'Department': 'Operations', 'Type': 'Individual'},
    {'Employee_ID': 'EMP3313', 'Name': 'Tamanna Alisha', 'Email': 'tamanna.alisha@koenig-solutions.com', 'Department': 'Operations', 'Type': 'Individual'},
    {'Employee_ID': 'EMP3135', 'Name': 'Nishant Yash', 'Email': 'nishant.yash@koenig-solutions.com', 'Department': 'Operations', 'Type': 'Individual'},
    {'Employee_ID': 'EMP2979', 'Name': 'Shkelzen Sadiku', 'Email': 'Shkelzen.Sadiku@koenig-solutions.com', 'Department': 'Operations', 'Type': 'Individual'},
    
    # COM EA Team
    {'Employee_ID': 'EMP1687', 'Name': 'Nupur Munjal', 'Email': 'nupur.munjal@koenig-solutions.com', 'Department': 'COM EA Team', 'Type': 'Individual'},
    
    # Departments
    {'Employee_ID': 'DEPT-HR', 'Name': 'HR', 'Email': 'praveen.chaudhary@koenig-solutions.com', 'Department': 'HR', 'Type': 'Department'},
    {'Employee_ID': 'DEPT-AP', 'Name': 'Accounts Payable', 'Email': 'praveen.chaudhary@koenig-solutions.com', 'Department': 'Finance', 'Type': 'Department'},
    {'Employee_ID': 'DEPT-AR', 'Name': 'Accounts Receivable', 'Email': 'praveen.chaudhary@koenig-solutions.com', 'Department': 'Finance', 'Type': 'Department'},
]

# Create DataFrame
df = pd.DataFrame(team_data)

# Save to Excel
output_file = 'data/Team_Directory.xlsx'
df.to_excel(output_file, index=False)

print('✅ Team Directory created!')
print('\n' + '='*80)
print(df.to_string(index=False))
print('='*80)

# Summary by department
print(f'\n📊 Summary:')
print(f'   Total Entries: {len(df)}')
print(f'   - Individuals: {len(df[df["Type"] == "Individual"])}')
print(f'   - Departments: {len(df[df["Type"] == "Department"])}')

print(f'\n📋 By Department:')
dept_counts = df[df['Type'] == 'Individual'].groupby('Department').size().sort_values(ascending=False)
for dept, count in dept_counts.items():
    print(f'   - {dept}: {count} people')

print(f'\n📁 Saved to: {output_file}')
print('\n🎯 Next Steps:')
print('   1. Test: python3 run_shoddy_check.py')
print('   2. Push: git add -f data/Team_Directory.xlsx')
print('   3. Commit: git commit -m "Add real team directory"')
print('   4. Deploy: git push origin main')
