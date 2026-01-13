"""
Priority Manager
Determines task priority based on keywords, context, and deadline
"""

from datetime import datetime, timedelta
from typing import Literal

PriorityLevel = Literal["urgent", "high", "medium", "low"]


# ================= PRIORITY KEYWORDS =================
URGENT_KEYWORDS = [
    "urgent", "asap", "immediately", "critical", "emergency",
    "today", "now", "right away", "stat", "priority"
]

HIGH_KEYWORDS = [
    "important", "significant", "key", "essential", "vital",
    "crucial", "major", "serious", "pressing", "high priority"
]

MEDIUM_KEYWORDS = [
    "moderate", "regular", "normal", "standard", "routine",
    "typical", "ordinary", "medium priority"
]

LOW_KEYWORDS = [
    "minor", "small", "low priority", "when possible", "eventually",
    "sometime", "nice to have", "optional"
]

# ================= DEPARTMENT PRIORITY =================
CRITICAL_DEPARTMENTS = [
    "finance", "tax", "statutory", "compliance", "audit",
    "legal", "ceo", "board", "investor"
]

HIGH_PRIORITY_DEPARTMENTS = [
    "hr", "operations", "sales", "customer", "client"
]

# ================= TASK TYPE PRIORITY =================
URGENT_TASK_TYPES = [
    "tds", "gst", "vat", "tax return", "filing", "deadline",
    "deposit", "payment", "statutory", "compliance"
]

HIGH_TASK_TYPES = [
    "report", "presentation", "meeting", "review", "approval",
    "invoice", "agreement", "contract"
]


def determine_priority(
    task_text: str,
    deadline_days: int = None,
    owner: str = None,
    mom_subject: str = None
) -> PriorityLevel:
    """
    Determine task priority based on multiple factors
    
    Args:
        task_text: The task description
        deadline_days: Days until deadline (if specified)
        owner: Task owner/department
        mom_subject: MOM subject line for context
    
    Returns:
        Priority level: "urgent", "high", "medium", or "low"
    
    Priority Rules:
    1. Urgent: Contains urgent keywords OR deadline < 2 days OR critical dept
    2. High: Contains high keywords OR deadline < 5 days OR high priority dept
    3. Medium: Contains medium keywords OR deadline < 10 days
    4. Low: Everything else OR no deadline
    """
    
    # Combine all text for analysis
    full_text = f"{task_text} {mom_subject or ''} {owner or ''}".lower()
    
    # ============= RULE 1: URGENT =============
    # Check urgent keywords
    if any(keyword in full_text for keyword in URGENT_KEYWORDS):
        return "urgent"
    
    # Check critical task types (tax, statutory, etc.)
    if any(task_type in full_text for task_type in URGENT_TASK_TYPES):
        return "urgent"
    
    # Check deadline (less than 2 days)
    if deadline_days is not None and deadline_days <= 2:
        return "urgent"
    
    # Check critical departments
    if owner and any(dept in owner.lower() for dept in CRITICAL_DEPARTMENTS):
        return "urgent"
    
    # ============= RULE 2: HIGH =============
    # Check high keywords
    if any(keyword in full_text for keyword in HIGH_KEYWORDS):
        return "high"
    
    # Check high priority task types
    if any(task_type in full_text for task_type in HIGH_TASK_TYPES):
        return "high"
    
    # Check deadline (less than 5 days)
    if deadline_days is not None and deadline_days <= 5:
        return "high"
    
    # Check high priority departments
    if owner and any(dept in owner.lower() for dept in HIGH_PRIORITY_DEPARTMENTS):
        return "high"
    
    # ============= RULE 3: MEDIUM =============
    # Check medium keywords
    if any(keyword in full_text for keyword in MEDIUM_KEYWORDS):
        return "medium"
    
    # Check deadline (less than 10 days)
    if deadline_days is not None and deadline_days <= 10:
        return "medium"
    
    # ============= RULE 4: LOW (DEFAULT) =============
    return "low"


def calculate_deadline(
    created_date: datetime,
    priority: PriorityLevel,
    custom_days: int = None
) -> datetime:
    """
    Calculate deadline based on priority
    
    Default Deadlines:
    - Urgent: 1 day
    - High: 3 days
    - Medium: 7 days
    - Low: 14 days
    
    Args:
        created_date: When task was created
        priority: Task priority level
        custom_days: Override with custom deadline (days)
    
    Returns:
        Deadline datetime
    """
    
    if custom_days:
        return created_date + timedelta(days=custom_days)
    
    deadline_map = {
        "urgent": 1,
        "high": 3,
        "medium": 7,
        "low": 14
    }
    
    days = deadline_map.get(priority, 7)
    return created_date + timedelta(days=days)


def get_priority_emoji(priority: PriorityLevel) -> str:
    """Get emoji for priority level"""
    emoji_map = {
        "urgent": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    return emoji_map.get(priority, "⚪")


if __name__ == "__main__":
    # Test priority determination
    test_cases = [
        ("Update TDS return filing. @Tax", None, "Tax", "Urgent"),
        ("Prepare board presentation. @CEO", 2, "CEO", "Urgent"),
        ("Review quarterly report. @Finance", 4, "Finance", "High"),
        ("Update team directory. @HR", 8, "HR", "Medium"),
        ("Organize files when possible. @Admin", 20, "Admin", "Low"),
    ]
    
    print("Priority Determination Tests:\n")
    for task, days, owner, expected in test_cases:
        priority = determine_priority(task, days, owner)
        emoji = get_priority_emoji(priority)
        print(f"{emoji} {priority.upper():8} | {task[:50]}")
        print(f"   Expected: {expected}, Days: {days}, Owner: {owner}")
        print()
