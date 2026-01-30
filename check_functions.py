# check_functions.py
import inspect
import run_reminders

print("📋 Functions available in run_reminders.py:")
for name, obj in inspect.getmembers(run_reminders):
    if inspect.isfunction(obj) and not name.startswith('_'):
        print(f"  - {name}")