#!/usr/bin/env python3
"""
Smart Reply Processor - Automatically process employee status update emails
"""

import re
import pandas as pd
from pathlib import Path
from datetime import datetime

class SmartReplyProcessor:
    """
    Processes email replies and auto-completes tasks based on keywords
    """
    
    # Keywords that indicate task completion
    COMPLETION_KEYWORDS = [
        'COMPLETED', 'COMPLETE', 'DONE', 'FINISHED', 
        'ACCOMPLISHED', 'CLOSED', 'RESOLVED'
    ]
    
    # Keywords that indicate pending/in-progress
    PENDING_KEYWORDS = [
        'PENDING', 'IN PROGRESS', 'WORKING ON', 'AWAITING',
        'NEED', 'REQUIRE', 'WAITING FOR'
    ]
    
    def __init__(self, task_registry_path='data/tasks_registry.xlsx'):
        self.task_registry_path = Path(task_registry_path)
        
    def extract_task_updates(self, email_body):
        """
        Extract task IDs and their status from email body
        
        Returns:
            list of dict: [{'task_id': 'MOM-XXX-T01', 'status': 'COMPLETED', 'notes': '...'}]
        """
        updates = []
        
        # Pattern 1: "Task ID: MOM-XXX-T01\nStatus: COMPLETED"
        pattern1 = r'Task ID[:\s]+([A-Z0-9\-]+)[\s\n]+Status[:\s]+(\w+)'
        matches1 = re.findall(pattern1, email_body, re.IGNORECASE | re.MULTILINE)
        
        for task_id, status in matches1:
            updates.append({
                'task_id': task_id.strip(),
                'status': status.strip().upper(),
                'notes': self._extract_notes_after_task(email_body, task_id)
            })
        
        # Pattern 2: "MOM-XXX-T01: COMPLETED"
        pattern2 = r'([A-Z0-9\-]+)[:\s]+(COMPLETED|COMPLETE|DONE|PENDING|IN PROGRESS)'
        matches2 = re.findall(pattern2, email_body, re.IGNORECASE)
        
        for task_id, status in matches2:
            if not any(u['task_id'] == task_id for u in updates):
                updates.append({
                    'task_id': task_id.strip(),
                    'status': status.strip().upper(),
                    'notes': self._extract_notes_after_task(email_body, task_id)
                })
        
        # Pattern 3: Bullet points "• Task ID : MOM-XXX-T01"
        pattern3 = r'[•\-\*]\s*Task ID\s*[:]\s*([A-Z0-9\-]+)'
        task_ids = re.findall(pattern3, email_body, re.IGNORECASE)
        
        for task_id in task_ids:
            if not any(u['task_id'] == task_id for u in updates):
                # Check if COMPLETED appears near this task
                task_section = self._extract_task_section(email_body, task_id)
                status = self._detect_status_in_text(task_section)
                
                updates.append({
                    'task_id': task_id.strip(),
                    'status': status,
                    'notes': task_section[:200] if task_section else ''
                })
        
        return updates
    
    def _extract_task_section(self, email_body, task_id):
        """Extract text section related to a specific task"""
        lines = email_body.split('\n')
        task_section = []
        capturing = False
        
        for line in lines:
            if task_id in line:
                capturing = True
            elif capturing:
                if re.match(r'[•\-\*]\s*Task ID', line) or re.match(r'^Task ID:', line):
                    break  # Next task started
                task_section.append(line)
                if len(task_section) > 5:  # Limit to 5 lines
                    break
        
        return '\n'.join(task_section)
    
    def _detect_status_in_text(self, text):
        """Detect status keywords in text"""
        text_upper = text.upper()
        
        for keyword in self.COMPLETION_KEYWORDS:
            if keyword in text_upper:
                return 'COMPLETED'
        
        for keyword in self.PENDING_KEYWORDS:
            if keyword in text_upper:
                return 'PENDING'
        
        return 'UNKNOWN'
    
    def _extract_notes_after_task(self, email_body, task_id):
        """Extract notes/details after task mention"""
        task_section = self._extract_task_section(email_body, task_id)
        # Remove the task ID line itself
        lines = [l for l in task_section.split('\n') if task_id not in l]
        notes = '\n'.join(lines).strip()
        return notes[:200] if notes else ''  # Limit to 200 chars
    
    def process_reply_and_update_tasks(self, email_body, from_email):
        """
        Process email reply and update task registry
        
        Returns:
            dict: Summary of updates
        """
        updates = self.extract_task_updates(email_body)
        
        if not updates:
            return {
                'success': False,
                'message': 'No task updates found in email',
                'completed': [],
                'pending': []
            }
        
        # Load task registry
        if not self.task_registry_path.exists():
            return {
                'success': False,
                'message': 'Task registry not found',
                'completed': [],
                'pending': []
            }
        
        df = pd.read_excel(self.task_registry_path)
        
        completed_tasks = []
        pending_tasks = []
        updated_count = 0
        
        for update in updates:
            task_id = update['task_id']
            status = update['status']
            notes = update['notes']
            
            # Find task in registry
            task_idx = df[df['task_id'] == task_id].index
            
            if len(task_idx) == 0:
                continue  # Task not found
            
            idx = task_idx[0]
            
            # Update based on status
            if any(kw in status for kw in self.COMPLETION_KEYWORDS):
                # Mark as completed
                df.at[idx, 'status'] = 'COMPLETED'
                df.at[idx, 'completed_date'] = datetime.now()
                
                # Calculate days taken
                created_on = pd.to_datetime(df.at[idx, 'created_on'])
                days_taken = (datetime.now() - created_on).days
                df.at[idx, 'days_taken'] = days_taken
                
                # Performance rating based on deadline
                deadline = pd.to_datetime(df.at[idx, 'deadline'])
                if pd.notna(deadline):
                    if datetime.now() <= deadline:
                        df.at[idx, 'performance_rating'] = 'On Time'
                    else:
                        days_overdue = (datetime.now() - deadline).days
                        if days_overdue <= 2:
                            df.at[idx, 'performance_rating'] = 'Slightly Late'
                        else:
                            df.at[idx, 'performance_rating'] = 'Late'
                
                completed_tasks.append({
                    'task_id': task_id,
                    'task_text': df.at[idx, 'task_text'],
                    'notes': notes
                })
                updated_count += 1
                
            elif any(kw in status for kw in self.PENDING_KEYWORDS):
                # Keep as pending, but add notes
                pending_tasks.append({
                    'task_id': task_id,
                    'task_text': df.at[idx, 'task_text'],
                    'notes': notes
                })
        
        # Save updated registry
        if updated_count > 0:
            df.to_excel(self.task_registry_path, index=False)
        
        return {
            'success': True,
            'message': f'Updated {updated_count} tasks',
            'completed': completed_tasks,
            'pending': pending_tasks,
            'updated_count': updated_count
        }
    
    def generate_acknowledgment_email(self, process_result, to_name):
        """
        Generate acknowledgment email body
        """
        completed = process_result['completed']
        pending = process_result['pending']
        
        body = f"Dear {to_name},\n\n"
        body += "Thank you for the update. We acknowledge the following:\n\n"
        
        if completed:
            body += "✅ COMPLETED TASKS:\n"
            for task in completed:
                body += f"• {task['task_id']}: {task['task_text'][:60]}...\n"
            body += "\n"
        
        if pending:
            body += "🔄 PENDING TASKS:\n"
            for task in pending:
                notes_preview = task['notes'][:50] if task['notes'] else 'Status update noted'
                body += f"• {task['task_id']}: {task['task_text'][:60]}...\n"
                body += f"  Note: {notes_preview}\n"
            body += "\n"
            body += "Please work on the pending tasks and let us know once completed.\n\n"
        else:
            body += "Excellent work! All action items have been completed.\n"
            body += "No further action required.\n\n"
        
        body += "Best regards,\n"
        body += "Task Follow-up Team"
        
        return body


# Test function
def test_processor():
    """Test the smart reply processor"""
    
    sample_email = """
    Dear Sir,
    
    Task ID: MOM-20251231-001-T16
    Status: Pending
    Notes: Still waiting for access guide.
    
    Task ID: MOM-20251231-001-T18
    Status: COMPLETED
    Notes: PFA ratings for December.
    
    MOM-20251231-001-T19: COMPLETED - E-invoicing details provided
    
    MOM-20251231-001-T21: Pending - awaiting calculation
    
    Task ID: MOM-20251231-001-T23
    Status: COMPLETED
    
    Regards,
    Sarika
    """
    
    processor = SmartReplyProcessor()
    updates = processor.extract_task_updates(sample_email)
    
    print("📧 Extracted Updates:")
    print("="*70)
    for update in updates:
        print(f"Task ID: {update['task_id']}")
        print(f"Status: {update['status']}")
        print(f"Notes: {update['notes'][:50]}...")
        print("-"*70)
    
    # Test acknowledgment email
    result = {
        'completed': [
            {'task_id': 'MOM-001-T18', 'task_text': 'Automation & ratings', 'notes': 'PFA'},
            {'task_id': 'MOM-001-T19', 'task_text': 'E-invoicing info', 'notes': 'Details provided'},
        ],
        'pending': [
            {'task_id': 'MOM-001-T16', 'task_text': 'UK portal status', 'notes': 'Waiting for access'},
            {'task_id': 'MOM-001-T21', 'task_text': 'Advance tax', 'notes': 'Awaiting calculation'},
        ]
    }
    
    ack_email = processor.generate_acknowledgment_email(result, "Sarika")
    print("\n📨 Generated Acknowledgment Email:")
    print("="*70)
    print(ack_email)


if __name__ == "__main__":
    test_processor()
