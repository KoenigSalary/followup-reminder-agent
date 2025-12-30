import re
from datetime import datetime
from typing import List, Dict

OWNER_PATTERN = re.compile(r"[\*@]([A-Za-z]+)", re.IGNORECASE)

def generate_meeting_id(meeting_date: datetime, counter: int = 1) -> str:
    return f"MOM-{meeting_date.strftime('%Y%m%d')}-{counter:03d}"

def generate_task_id(meeting_id: str, index: int) -> str:
    return f"{meeting_id}-T{index:02d}"

def clean_html(text: str) -> str:
    # very light cleaning (we’ll improve later)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_tasks_from_text(text: str) -> List[str]:
    """
    Extracts task-like lines.
    Strategy:
    - Split by sentences / line breaks
    - Keep lines that look like action points
    """
    candidates = re.split(r"[.\n]", text)
    tasks = []

    for line in candidates:
        line = line.strip()
        if len(line) < 15:
            continue
        if any(keyword in line.lower() for keyword in [
            "please", "share", "check", "update", "confirm",
            "take care", "follow", "send", "review", "let me know"
        ]):
            tasks.append(line)

    return tasks

def detect_owner(task_text: str, default_owner: str) -> str:
    match = OWNER_PATTERN.search(task_text)
    if match:
        return match.group(1).capitalize()
    return default_owner

def parse_mom_thread(thread_messages: List[Dict]) -> Dict:
    """
    Input: messages in chronological order (from graph_thread_reader)
    Output: structured MOM + tasks
    """

    # assume first message is the MOM
    first_msg = thread_messages[0]
    subject = first_msg.get("subject", "")
    sender = first_msg.get("from", {}).get("emailAddress", {}).get("address", "UNKNOWN")

    meeting_date = datetime.fromisoformat(
        first_msg["receivedDateTime"].replace("Z", "+00:00")
    )

    meeting_id = generate_meeting_id(meeting_date)

    full_text = ""
    for msg in thread_messages:
        body = msg.get("body", {}).get("content", "")
        full_text += " " + clean_html(body)

    raw_tasks = extract_tasks_from_text(full_text)

    tasks = []
    for idx, task_text in enumerate(raw_tasks, start=1):
        owner = detect_owner(task_text, sender)
        tasks.append({
            "task_id": generate_task_id(meeting_id, idx),
            "task_text": task_text,
            "owner": owner,
            "status": "OPEN"
        })

    return {
        "meeting_id": meeting_id,
        "subject": subject,
        "meeting_date": meeting_date.isoformat(),
        "created_by": sender,
        "task_count": len(tasks),
        "tasks": tasks
    }

if __name__ == "__main__":
    # mock one thread (simplified)
    sample_thread = [
        {
            "subject": "MOM | Meeting with Sarika | 25-Dec-2025",
            "receivedDateTime": "2025-12-25T10:22:00Z",
            "from": {"emailAddress": {"address": "praveen.chaudhary@koenig-solutions.com"}},
            "body": {"content": """
                Give Tripti additional responsibility as discussed.
                Advance tax to be taken care of by you from next month. *Sunil
                Share the WHT certificate received in Dubai.
                Please review the Tax Meeting video and share feedback.
            """}
        }
    ]

    result = parse_mom_thread(sample_thread)
    from pprint import pprint
    pprint(result)
