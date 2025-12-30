import os
from reminder_scheduler import ReminderScheduler
from config import EXCEL_FILE_PATH

# Manual .env loading (cron-safe)
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_FILE):
    with open(ENV_FILE) as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

if __name__ == "__main__":
    scheduler = ReminderScheduler(EXCEL_FILE_PATH)
    sent = scheduler.run()
    print(f"{sent} reminder(s) sent.")


