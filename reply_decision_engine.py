import re
from typing import List, Dict, Optional
from config import EMAIL_SIGNATURE

# ==================================================
# Heuristic markers
# ==================================================
QUESTION_MARKERS = [
    "?",
    "please confirm",
    "let me know",
    "can you",
    "could you",
    "what is",
    "when will",
    "why",
    "how",
    "status",
    "update"
]

FYI_MARKERS = [
    "fyi",
    "for your information",
    "attached",
    "invoice",
    "newsletter",
    "auto-generated",
    "no action required"
]

# ==================================================
# Helper detectors
# ==================================================
def contains_question(text: str) -> bool:
    """
    Detects whether the mail requires a response
    """
    t = text.lower()
    return any(marker in t for marker in QUESTION_MARKERS)


def is_fyi_mail(text: str) -> bool:
    """
    Detects FYI / no-action mails
    """
    t = text.lower()
    return any(marker in t for marker in FYI_MARKERS)


# ==================================================
# Core decision logic
# ==================================================
def decide_reply_type(
    thread_messages: List[Dict],
    parsed_mom: Optional[Dict] = None,
    ack_enabled: bool = True
) -> str:
    """
    Decide how the agent should respond.

    Returns:
        NO_REPLY
        ACK_ONLY
        TASK_CONFIRM
    """

    full_text = " ".join(
        msg.get("body", {}).get("content", "").lower()
        for msg in thread_messages
    )

    # 1️⃣ MOM threads → never reply
    if parsed_mom and parsed_mom.get("task_count", 0) > 0:
        return "NO_REPLY"

    # 2️⃣ FYI mails → never reply
    if is_fyi_mail(full_text):
        return "NO_REPLY"

    # 3️⃣ Questions → ACK (only if enabled)
    if ack_enabled and contains_question(full_text):
        return "ACK_ONLY"

    return "NO_REPLY"


# ==================================================
# Reply generators
# ==================================================
def generate_ack_reply() -> str:
    """
    Polite acknowledgement when agent is unsure
    """
    return (
        "Thanks for your email.\n\n"
        "I’ve noted this and will review it. "
        "I’ll get back to you shortly.\n\n"
        f"Regards,\n{EMAIL_SIGNATURE}"
    )


def generate_task_confirmation(task: Dict) -> str:
    """
    Confirmation when a task is created explicitly
    """
    return (
        "Thanks for the update.\n\n"
        f"I’ve noted this and created Task ID: {task.get('task_id')}.\n\n"
        "I’ll take this up and update you accordingly.\n\n"
        f"Regards,\n{EMAIL_SIGNATURE}"
    )


# ==================================================
# Local test (safe)
# ==================================================
if __name__ == "__main__":
    # Mock unclear question email
    thread = [
        {"body": {"content": "Can you please update?"}}
    ]

    reply_type = decide_reply_type(
        thread_messages=thread,
        parsed_mom=None,
        ack_enabled=True
    )

    print("Reply type:", reply_type)

    if reply_type == "ACK_ONLY":
        print("\n--- Reply Preview ---\n")
        print(generate_ack_reply())
