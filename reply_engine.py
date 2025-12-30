import re

QUESTION_MARKERS = [
    "?",
    "please confirm",
    "let me know",
    "can you",
    "could you",
    "what is",
    "when will",
    "why",
    "how"
]

FYI_MARKERS = [
    "fyi",
    "for your information",
    "attached",
    "invoice",
    "newsletter",
    "auto-generated"
]

def contains_question(text: str) -> bool:
    t = text.lower()
    return any(q in t for q in QUESTION_MARKERS)

def is_fyi_mail(text: str) -> bool:
    t = text.lower()
    return any(f in t for f in FYI_MARKERS)

def decide_reply_type(thread_messages: list, parsed_mom: dict | None) -> str:
    """
    Returns: NO_REPLY | ACK_ONLY | TASK_CONFIRM
    """

    full_text = " ".join(
        msg.get("body", {}).get("content", "").lower()
        for msg in thread_messages
    )

    # 1. MOM threads → no reply
    if parsed_mom and parsed_mom.get("task_count", 0) > 0:
        return "NO_REPLY"

    # 2. FYI mails → no reply
    if is_fyi_mail(full_text):
        return "NO_REPLY"

    # 3. Questions → polite ACK
    if contains_question(full_text):
        return "ACK_ONLY"

    return "NO_REPLY"

def generate_ack_reply() -> str:
    return (
        "Thanks for your email.\n\n"
        "I’ve noted this and will review it. "
        "I’ll get back to you shortly.\n\n"
        "Regards,\n"
        "Praveen"
    )

def generate_task_confirmation(task: dict) -> str:
    return (
        f"Thanks for the update.\n\n"
        f"I’ve noted this and created Task ID: {task['task_id']}.\n\n"
        "I’ll take this up and update you accordingly.\n\n"
        "Regards,\n"
        "Praveen"
    )

if __name__ == "__main__":
    # Mock unclear question email
    thread = [
        {"body": {"content": "Can you please update?"}}
    ]

    reply_type = decide_reply_type(thread, parsed_mom=None)
    print("Reply type:", reply_type)

    if reply_type == "ACK_ONLY":
        print(generate_ack_reply())
