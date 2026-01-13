"""
Task Normalizer - Standardizes task data format
"""
import pandas as pd
from datetime import datetime

def normalize_column_names(df):
    """
    Normalize column names to standard format (Title Case)
    """
    column_mapping = {
        'task_id': 'task_id',
        'meeting_id': 'meeting_id',
        'owner': 'Owner',
        'Owner': 'Owner',
        'subject': 'Subject',
        'Subject': 'Subject',
        'status': 'Status',
        'Status': 'Status',
        'priority': 'Priority',
        'Priority': 'Priority',
        'due_date': 'Due Date',
        'Due Date': 'Due Date',
        'due date': 'Due Date',
        'cc': 'CC',
        'CC': 'CC',
        'remarks': 'Remarks',
        'Remarks': 'Remarks',
        'created_on': 'Created On',
        'Created On': 'Created On',
        'last_updated': 'Last Updated',
        'Last Updated': 'Last Updated',
        'last_reminder_date': 'Last Reminder Date',
        'Last Reminder Date': 'Last Reminder Date',
        'last_reminder_on': 'Last Reminder On',
        'Last Reminder On': 'Last Reminder On',
        'completed_date': 'Completed Date',
        'Completed Date': 'Completed Date',
        'auto_reply_sent': 'Auto Reply Sent',
        'Auto Reply Sent': 'Auto Reply Sent',
        'last_reminder': 'last_reminder',
        'days_taken': 'days_taken',
        'performance_rating': 'performance_rating'
    }
    
    df = df.rename(columns=column_mapping)
    return df

def normalize_status(status):
    """Normalize status values"""
    if pd.isna(status):
        return 'OPEN'
    
    status = str(status).strip().upper()
    
    status_mapping = {
        'OPEN': 'OPEN',
        'IN PROGRESS': 'OPEN',
        'PENDING': 'OPEN',
        'COMPLETED': 'COMPLETED',
        'DONE': 'COMPLETED',
        'CLOSED': 'COMPLETED',
        'DELETED': 'DELETED',
        'CANCELLED': 'DELETED'
    }
    
    return status_mapping.get(status, 'OPEN')

def normalize_priority(priority):
    """Normalize priority values"""
    if pd.isna(priority):
        return 'MEDIUM'
    
    priority = str(priority).strip().upper()
    
    priority_mapping = {
        'URGENT': 'URGENT',
        'HIGH': 'HIGH',
        'MEDIUM': 'MEDIUM',
        'NORMAL': 'MEDIUM',
        'LOW': 'LOW'
    }
    
    return priority_mapping.get(priority, 'MEDIUM')

def normalize_date(date_value):
    """Normalize date format to YYYY-MM-DD"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, str):
        try:
            dt = pd.to_datetime(date_value, errors='coerce')
            if pd.notna(dt):
                return dt.strftime('%Y-%m-%d')
        except:
            pass
    elif isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    
    return date_value

def normalize_tasks(df):
    """Normalize entire task dataframe"""
    df = normalize_column_names(df)
    
    if 'Status' in df.columns:
        df['Status'] = df['Status'].apply(normalize_status)
    
    if 'Priority' in df.columns:
        df['Priority'] = df['Priority'].apply(normalize_priority)
    
    date_columns = ['Due Date', 'Created On', 'Last Updated', 'Completed Date']
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_date)
    
    return df

# Alias for compatibility
normalize_df = normalize_tasks

def get_required_columns():
    """Return list of required columns"""
    return [
        'task_id', 'meeting_id', 'Owner', 'Subject', 'Status', 
        'Priority', 'Due Date', 'CC', 'Remarks', 'Created On', 
        'Last Updated', 'Last Reminder Date', 'Last Reminder On', 
        'Completed Date', 'Auto Reply Sent', 'last_reminder', 
        'days_taken', 'performance_rating'
    ]
