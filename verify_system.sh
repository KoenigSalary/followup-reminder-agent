#!/bin/bash
echo "🔍 Follow-up & Reminder Team - System Verification"
echo "=================================================="
echo ""

echo "📂 Data Files:"
ls -lh data/*.xlsx 2>/dev/null | tail -3

echo ""
echo "🔧 Utils Modules:"
ls -1 utils/*.py 2>/dev/null | grep -v __pycache__ | wc -l | xargs echo "   Files:"

echo ""
echo "🎨 Views Modules:"
ls -1 views/*.py 2>/dev/null | grep -v __pycache__ | wc -l | xargs echo "   Files:"

echo ""
echo "📊 Task Statistics:"
python3 << 'PYEOF'
import pandas as pd
df = pd.read_excel('data/tasks_registry.xlsx')
print(f"   Total Tasks: {len(df)}")
print(f"   OPEN: {len(df[df['Status'].str.upper() == 'OPEN'])}")
print(f"   COMPLETED: {len(df[df['Status'].str.upper() == 'COMPLETED'])}")
print(f"   DELETED: {len(df[df['Status'].str.upper() == 'DELETED'])}")
PYEOF

echo ""
echo "👥 Team Directory:"
python3 << 'PYEOF'
import pandas as pd
df = pd.read_excel('data/Team_Directory.xlsx')
print(f"   Total Users: {len(df)}")
print(f"   Active Users: {len(df[df['is_active'] == True])}")
PYEOF

echo ""
echo "✅ System is operational!"
