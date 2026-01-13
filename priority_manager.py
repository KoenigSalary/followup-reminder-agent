"""Priority Manager - Complete module"""

def get_priority_days(priority):
    """Days before deadline to start reminding"""
    priority_map = {
        'URGENT': 10,
        'HIGH': 7,
        'MEDIUM': 7,
        'LOW': 10
    }
    return priority_map.get(priority.upper(), 7)

def get_reminder_frequency(priority):
    """Reminder frequency in days"""
    frequency_map = {
        'URGENT': 1,
        'HIGH': 2,
        'MEDIUM': 3,
        'LOW': 5
    }
    return frequency_map.get(priority.upper(), 3)

def get_priority_emoji(priority):
    """Get emoji for priority level"""
    priority_map = {
        'URGENT': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }
    return priority_map.get(str(priority).upper(), '⚪')

def get_priority_color(priority):
    """Get color for priority level"""
    color_map = {
        'URGENT': '#FF4444',
        'HIGH': '#FF8800',
        'MEDIUM': '#FFBB00',
        'LOW': '#00CC44'
    }
    return color_map.get(str(priority).upper(), '#CCCCCC')
