import os
import pandas as pd
from datetime import datetime
from datetime import timezone
from config import TASK_FILE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

REGISTRY_FILE = os.path.join(DATA_DIR, "tasks_registry.xlsx")

COLUMNS = [
    "meeting_id",
    "task_id",
    "task_text",
    "owner",
    "status",
    "priority",           # ✨ NEW
    "deadline",           # ✨ NEW
    "completed_date",     # ✨ NEW
    "created_by",
    "created_on",
    "last_reminder_date"
]

def init_registry():
    if not os.path.exists(REGISTRY_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(REGISTRY_FILE, index=False)

def load_registry() -> pd.DataFrame:
    init_registry()
    return pd.read_excel(REGISTRY_FILE)

def save_registry(df: pd.DataFrame):
    df.to_excel(REGISTRY_FILE, index=False)

def task_exists(df: pd.DataFrame, task_id: str) -> bool:
    return task_id in df["task_id"].astype(str).values

def add_tasks_from_mom(mom_data: dict):
    """
    mom_data = output from parse_mom_thread()
    """
    df = load_registry()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for task in mom_data["tasks"]:
        if task_exists(df, task["task_id"]):
            continue

        df.loc[len(df)] = {
            "meeting_id": mom_data["meeting_id"],
            "task_id": task["task_id"],
            "task_text": task["task_text"],
            "owner": task["owner"],
            "status": task["status"],
            "created_by": mom_data["created_by"],
            "created_on": now,
            "completed_on": ""
        }

    save_registry(df)

def append_tasks(tasks: list):
    if TASK_FILE.exists():
        df = pd.read_excel(TASK_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame(tasks)], ignore_index=True)
    df.to_excel(TASK_FILE, index=False)

def mark_task_completed(task_id: str):
    df = load_registry()
    if task_id not in df["task_id"].astype(str).values:
        raise ValueError("Task ID not found")

    df.loc[df["task_id"] == task_id, "status"] = "COMPLETED"
    df.loc[df["task_id"] == task_id, "completed_on"] = (
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )

    save_registry(df)

if __name__ == "__main__":
    from mom_parser import parse_mom_thread

    sample_thread = [
        {
            "subject": "MOM | Meeting with Sarika | 25-Dec-2025",
            "receivedDateTime": "2025-12-25T10:22:00Z",
            "from": {"emailAddress": {"address": "praveen.chaudhary@koenig-solutions.com"}},
            "body": {"content": """
                Share the WHT certificate received in Dubai. *Sunil
                Please review the Tax Meeting video and share feedback.
            """}
        }
    ]

    mom = parse_mom_thread(sample_thread)
    add_tasks_from_mom(mom)

    print("Tasks written to registry.")
