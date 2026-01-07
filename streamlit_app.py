# =========================================================
# ENV + PATH SETUP
# =========================================================
import os
import pandas as pd
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
LOGO_PATH = BASE_DIR / "assets" / "koenig_logo.png"

load_dotenv(dotenv_path=ENV_PATH)

def run_script(script_name):
    result = subprocess.run(
        ["python3", script_name],
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip()

# =========================================================
# CONFIG & INTERNAL IMPORTS
# =========================================================
from config import (
    EXCEL_FILE_PATH,
    APP_TITLE,
    validate_paths,
)

from utils.excel_handler import ExcelHandler
from email_processor import EmailProcessor
from reminder_scheduler import ReminderScheduler, get_next_reminder_date
from manual_processor import ManualTaskProcessor

# =========================================================
# 🔐 AUTHENTICATION SYSTEM
# =========================================================
from user_manager import UserManager

# Initialize user manager
@st.cache_resource
def get_user_manager():
    return UserManager()

user_manager = get_user_manager()

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.permissions = None

# Login function
def login():
    """Display login page"""
    st.set_page_config(page_title="Login - Task Follow-up System", layout="centered")
    
    # Logo - slightly right of center
    col1, col2, col3 = st.columns([1.6, 2, 0.7])
    with col2:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=150)  # Smaller logo
        st.markdown("")  # Spacing
    
    st.markdown("<h1 style='text-align: center;'>🔐 Task Follow-up System</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please login to continue")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    user_info = user_manager.authenticate(username, password)
                    
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_info
                        st.session_state.permissions = user_manager.get_user_permissions(user_info)
                        st.success(f"✅ Welcome, {user_info['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.markdown("---")
        st.caption("🔒 Contact IT for account access")

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.permissions = None
    st.rerun()

# Check authentication status
if not st.session_state.authenticated:
    login()
    st.stop()

# Check authentication status
if not st.session_state.authenticated:
    login()
    st.stop()

# =========================================================
# GLOBAL CC CONFIGURATION
# =========================================================
# Initialize global_cc in session state if not exists
if 'global_cc' not in st.session_state:
    st.session_state.global_cc = ''

# Helper function
def extract_cc(line, global_cc):
    if "cc:" in line.lower():
        cc_part = line.split("cc:", 1)[1]
        return cc_part.strip()
    return global_cc

# =========================================================
# PAGE CONFIG (after authentication)
# =========================================================
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
)

# =========================================================
# SIDEBAR BRANDING + USER INFO
# =========================================================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)
    st.markdown("### Follow-up & Reminder Agent")
    st.markdown("---")
    
    # User info section
    st.markdown(f"**👤 Logged in as:**")
    st.markdown(f"**{st.session_state.user_info['full_name']}**")
    st.markdown(f"*{st.session_state.user_info['role'].replace('_', ' ').title()}*")
    st.caption(f"📧 {st.session_state.user_info['email']}")
    st.caption(f"🏢 {st.session_state.user_info['department']}")
    
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.markdown("---")

# =========================================================
# SIDEBAR - GLOBAL CC SETTING
# =========================================================
with st.sidebar.expander("⚙️ Global Settings"):
    global_cc_input = st.text_input(
        "Default CC Emails",
        value=st.session_state.get('global_cc', ''),
        placeholder="email1@example.com, email2@example.com",
        help="Default CC for all new tasks"
    )
    if st.button("💾 Save Global CC"):
        st.session_state.global_cc = global_cc_input
        st.success("✅ Global CC saved!")

st.sidebar.markdown("---")

# UTILS
# =========================================================
def status_badge(status: str):
    status = str(status).upper()
    if status == "OPEN":
        return "🟡 OPEN"
    if status == "COMPLETED":
        return "🟢 COMPLETED"
    return status

# =========================================================
# HEADER
# =========================================================
st.title(APP_TITLE)
st.caption("Follow-up & Reminder Agent")

# =========================================================
# VALIDATE PATHS (critical)
# =========================================================
validate_paths()

# =========================================================
# CACHED HANDLERS
# =========================================================
@st.cache_resource
def initialize_handlers():
    excel_handler = ExcelHandler(EXCEL_FILE_PATH)
    email_processor = EmailProcessor()
    reminder_scheduler = ReminderScheduler(EXCEL_FILE_PATH)
    manual_processor = ManualTaskProcessor()
    return excel_handler, email_processor, reminder_scheduler, manual_processor

excel_handler, email_processor, reminder_scheduler, manual_processor = initialize_handlers()

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
st.sidebar.header("Navigation")

# Build menu based on permissions
menu_options = [
    "📊 Dashboard Analytics",  # ✨ NEW: Always visible
    "📥 View Follow-ups",
    "🔍 DEBUG Tasks"           # ✨ NEW: Debug mode
]

if st.session_state.permissions.get('send_reminders'):
    menu_options.extend(["📧 Process Emails", "⏰ Run Reminder Scheduler", "📤 Send Task Reminders"])

if st.session_state.permissions.get('create_tasks'):
    menu_options.extend(["✍️ Manual Entry", "📄 Bulk MOM Upload"])

if st.session_state.permissions.get('manage_shoddy'):
    menu_options.append("⚠️ Shoddy Check")

if st.session_state.permissions.get('manage_users'):
    menu_options.append("👥 User Management")

menu_options.extend(["🔑 Change Password", "📊 Logs / Status"])
menu = st.sidebar.radio("Select Action", menu_options)

# =========================================================
# 📊 DASHBOARD ANALYTICS
# =========================================================
if menu == "📊 Dashboard Analytics":
    st.title("📊 Task Analytics Dashboard")
    
    # Load data
    df = excel_handler.load_data()
    
    # Normalize column names
    column_mapping = {
        'task_text': 'Subject',
        'deadline': 'Due Date',
        'owner': 'Owner',
        'status': 'Status',
        'priority': 'Priority',
        'created_on': 'Created On'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    if df.empty:
        st.info("📭 No tasks available for analysis.")
    else:
        # ✅ FIXED: Proper status filtering
        status_col = 'Status' if 'Status' in df.columns else 'status'
        
        # Calculate metrics
        total_tasks = len(df)
        
        # OPEN tasks
        open_tasks = len(df[df[status_col].astype(str).str.upper() == 'OPEN'])
        
        # COMPLETED tasks
        completed_tasks = len(df[df[status_col].astype(str).str.upper().isin(['COMPLETED', 'CLOSED'])])
        
        # OVERDUE tasks
        today = datetime.now().date()
        overdue_count = 0
        
        deadline_col = 'Due Date' if 'Due Date' in df.columns else 'deadline'
        
        for idx, row in df.iterrows():
            if row[status_col] and str(row[status_col]).upper() == 'OPEN':
                deadline = row.get(deadline_col)
                if deadline:
                    # Handle both string and datetime
                    if isinstance(deadline, str):
                        try:
                            deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
                        except:
                            continue
                    elif hasattr(deadline, 'date'):
                        deadline = deadline.date()
                    
                    if deadline < today:
                        overdue_count += 1
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Tasks", total_tasks)
        
        with col2:
            st.metric("📂 Open Tasks", open_tasks)
        
        with col3:
            st.metric("✅ Completed", completed_tasks)
        
        with col4:
            st.metric("🚨 Overdue", overdue_count, delta=None if overdue_count == 0 else "!")
        
        st.markdown("---")
                      
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Tasks by Priority")
            
            # Get priority column
            priority_col = 'Priority' if 'Priority' in df.columns else 'priority'
            if priority_col in df.columns:
                priority_counts = df[priority_col].value_counts()
                
                # Create chart data
                chart_data = pd.DataFrame({
                    'Priority': priority_counts.index,
                    'Count': priority_counts.values
                })
                
                # Map to display names with emojis
                priority_map = {
                    'URGENT': '🔴 URGENT',
                    'urgent': '🔴 URGENT',
                    'HIGH': '🟠 HIGH',
                    'high': '🟠 HIGH',
                    'MEDIUM': '🟡 MEDIUM',
                    'medium': '🟡 MEDIUM',
                    'LOW': '🟢 LOW',
                    'low': '🟢 LOW'
                }
                chart_data['Priority'] = chart_data['Priority'].map(lambda x: priority_map.get(x, x))
                
                st.bar_chart(chart_data.set_index('Priority'))
            else:
                st.info("No priority data available")
        
        with col2:
            st.subheader("📊 Task Status Distribution")
            
            status_col = 'Status' if 'Status' in df.columns else 'status'
            if status_col in df.columns:
                status_counts = df[status_col].str.upper().value_counts()
                
                chart_data = pd.DataFrame({
                    'Status': status_counts.index,
                    'Count': status_counts.values
                })
                
                st.bar_chart(chart_data.set_index('Status'))
            else:
                st.info("No status data available")
        
        st.divider()
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Tasks by Owner")
            
            owner_col = 'Owner' if 'Owner' in df.columns else 'owner'
            if owner_col in df.columns:
                owner_counts = df[owner_col].value_counts().head(10)
                
                chart_data = pd.DataFrame({
                    'Owner': owner_counts.index,
                    'Count': owner_counts.values
                })
                
                st.bar_chart(chart_data.set_index('Owner'))
            else:
                st.info("No owner data available")
        
        with col2:
            st.subheader("⏰ Upcoming Deadlines")
            
            # Filter open tasks
            open_df = df[df.get('Status', df.get('status', '')).str.upper() == 'OPEN'].copy()
            
            if len(open_df) > 0:
                deadline_col = 'Due Date' if 'Due Date' in open_df.columns else 'deadline'
                
                if deadline_col in open_df.columns:
                    # Calculate days until deadline
                    upcoming = []
                    for idx, row in open_df.iterrows():
                        deadline = row.get(deadline_col)
                        if pd.notna(deadline):
                            if isinstance(deadline, str):
                                deadline = pd.to_datetime(deadline).date()
                            elif hasattr(deadline, 'date'):
                                deadline = deadline.date()
                            
                            days_left = (deadline - today).days
                            task_name = row.get('Subject', row.get('task_text', 'Unknown'))[:30]
                            
                            upcoming.append({
                                'Task': task_name,
                                'Days': days_left,
                                'Priority': row.get('Priority', row.get('priority', 'MEDIUM'))
                            })
                    
                    if upcoming:
                        upcoming_df = pd.DataFrame(upcoming).sort_values('Days').head(10)
                        
                        for _, row in upcoming_df.iterrows():
                            if row['Days'] < 0:
                                st.error(f"⚠️ {row['Task']} - **OVERDUE by {abs(row['Days'])} days**")
                            elif row['Days'] == 0:
                                st.warning(f"🔔 {row['Task']} - **DUE TODAY**")
                            elif row['Days'] <= 2:
                                st.warning(f"⏰ {row['Task']} - {row['Days']} days left")
                            else:
                                st.info(f"📅 {row['Task']} - {row['Days']} days left")
                    else:
                        st.success("✅ No upcoming deadlines")
                else:
                    st.info("No deadline data available")
            else:
                st.success("✅ No open tasks")
        
        st.divider()
        
        # Completion Rate
        st.subheader("📈 Completion Rate")
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.progress(completion_rate / 100)
                st.write(f"**{completion_rate:.1f}%** of tasks completed")
            
            with col2:
                st.metric("Completed", completed_tasks)
            
            with col3:
                st.metric("Remaining", open_tasks)
        
        st.divider()
        
        # Overdue Tasks Alert
        if overdue_count > 0:
            st.error(f"⚠️ **{overdue_count} Overdue Tasks Require Attention!**")
            
            with st.expander("View Overdue Tasks"):
                overdue_tasks = []
                for idx, row in df.iterrows():
                    if row.get('Status', row.get('status', '')).upper() == 'OPEN':
                        deadline = row.get('Due Date', row.get('deadline'))
                        if pd.notna(deadline):
                            if isinstance(deadline, str):
                                deadline = pd.to_datetime(deadline).date()
                            elif hasattr(deadline, 'date'):
                                deadline = deadline.date()
                            if deadline < today:
                                days_overdue = (today - deadline).days
                                overdue_tasks.append({
                                    'Task': row.get('Subject', row.get('task_text', 'Unknown')),
                                    'Owner': row.get('Owner', row.get('owner', 'Unknown')),
                                    'Deadline': deadline,
                                    'Days Overdue': days_overdue,
                                    'Priority': row.get('Priority', row.get('priority', 'MEDIUM'))
                                })
                
                if overdue_tasks:
                    overdue_df = pd.DataFrame(overdue_tasks).sort_values('Days Overdue', ascending=False)
                    st.dataframe(overdue_df, use_container_width=True)

# =========================================================
# 🔍 DEBUG TASKS
# =========================================================
elif menu == "🔍 DEBUG Tasks":
    st.title("🔍 Debug: All Tasks")
    
    df = excel_handler.load_data()
    
    st.write(f"**📊 Total tasks:** {len(df)}")
    st.write(f"**📋 Columns:** {list(df.columns)}")
    
    if len(df) > 0:
        st.write("**📈 Status distribution:**")
        if 'status' in df.columns:
            st.write(df['status'].value_counts())
        else:
            st.warning("⚠️ No 'status' column found!")
        
        st.write("**📋 Last 20 tasks:**")
        display_cols = ['task_id', 'owner', 'task_text', 'status', 'priority', 'deadline']
        available_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[available_cols].tail(20))
        
        st.write("**🔍 Raw last row:**")
        st.json(df.iloc[-1].to_dict())
    else:
        st.info("No tasks in registry")

# =========================================================
# 1. VIEW FOLLOW-UPS
# =========================================================
elif menu == "📥 View Follow-ups":
    st.subheader("Follow-ups")

    df = excel_handler.load_data()
    
    # 🐛 DEBUG SECTION
    with st.expander("🔍 Debug: Raw Data"):
        st.write(f"**Total rows:** {len(df)}")
        st.write(f"**Columns:** {list(df.columns)}")
        if len(df) > 0:
            st.write("**Status values:**")
            st.write(df['status'].value_counts() if 'status' in df.columns else "No 'status' column")
            st.write("**Last 5 tasks:**")
            st.dataframe(df.tail(5))
    
    # ✨ FILTER TASKS BY USER ROLE
    # 🎚️ FILTER TOGGLE
    show_all = st.checkbox("📋 Show all tasks", value=True, help="Uncheck to see only tasks assigned to you/your department")
    
    if not show_all:
        df = user_manager.filter_tasks_by_user(df, st.session_state.user_info)
        st.info(f"🔍 Filtered to: {st.session_state.user_info.get('role')} - {st.session_state.user_info.get('department')}")
    else:
        st.info("📋 Showing all tasks")

    # 🔄 Normalize column names for compatibility
    column_mapping = {
        'task_text': 'Subject',
        'deadline': 'Due Date',
        'last_reminder_date': 'Last Reminder Date',
        'owner': 'Owner',
        'status': 'Status',
        'priority': 'Priority'
    }
    
    # Rename columns if they exist
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    # Add Remarks column if missing
    if 'Remarks' not in df.columns:
        df['Remarks'] = ''
    
    # 🔍 DEBUG: Show what we have
    st.write(f"**Total tasks loaded:** {len(df)}")
    
    if df.empty:
        st.info("No follow-ups available.")
    else:
        # 🔄 Normalize column names for compatibility
        column_mapping = {
            'task_text': 'Subject',
            'deadline': 'Due Date',
            'last_reminder_date': 'Last Reminder Date',
            'owner': 'Owner',
            'status': 'Status',
            'priority': 'Priority'
        }
        
        # Rename columns if they exist
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Add Remarks column if missing
        if 'Remarks' not in df.columns:
            df['Remarks'] = ''
        
        for idx, row in df.iterrows():
            # ✅ Extract scalar values safely
            subject = row.get("Subject", "N/A")
            if isinstance(subject, pd.Series):
                subject = subject.iloc[0] if not subject.empty else "N/A"
            
            owner = row.get("Owner", "N/A")
            if isinstance(owner, pd.Series):
                owner = owner.iloc[0] if not owner.empty else "N/A"
            
            due_date = row.get("Due Date", "N/A")
            if isinstance(due_date, pd.Series):
                due_date = due_date.iloc[0] if not due_date.empty else "N/A"
            
            status_val = row.get("Status", "N/A")
            if isinstance(status_val, pd.Series):
                status_val = status_val.iloc[0] if not status_val.empty else "N/A"
            status = status_badge(status_val)
            
            remarks = row.get("Remarks", "")
            if isinstance(remarks, pd.Series):
                remarks = remarks.iloc[0] if not remarks.empty else ""
            
            priority = row.get("Priority", "MEDIUM")
            if isinstance(priority, pd.Series):
                priority = priority.iloc[0] if not priority.empty else "MEDIUM"

            col1, col2 = st.columns([4, 1])

            with col1:
                # ✨ Add priority emoji
                from priority_manager import get_priority_emoji
                priority_display = f"{get_priority_emoji(priority)} {priority}"
                
                st.markdown(
                    f"""
**Subject:** {subject}  
**Owner:** {owner}  
**Priority:** {priority_display}  
**Due Date:** {due_date}  
**Status:** {status}  
**Remarks:** {remarks}
"""
                )

            with col2:
                if str(status_val).upper() not in ["COMPLETED", "CLOSED"]:
                    if st.button("✅ Mark Completed", key=f"complete_{idx}"):
                        excel_handler.update_status(idx, "COMPLETED")
                        st.success("Marked as completed.")
                        st.rerun()

            st.divider()

            # ✅ Extract date values safely
            last_reminder = row.get("Last Reminder Date")
            if isinstance(last_reminder, pd.Series):
                last_reminder = last_reminder.iloc[0] if not last_reminder.empty else None
            
            due = row.get("Due Date")
            if isinstance(due, pd.Series):
                due = due.iloc[0] if not due.empty else None

            # Convert to date objects if needed
            if hasattr(last_reminder, "date"):
                last_reminder = last_reminder.date()
            if hasattr(due, "date"):
                due = due.date()

            # Now safe to call
            next_reminder = get_next_reminder_date(
                priority,
                last_reminder,
                due
            )

            st.markdown(f"**Last Reminder:** {last_reminder or 'Not yet sent'}")
            st.markdown(f"**Next Reminder:** {next_reminder or 'Calculated on next run'}")

# =========================================================
# 2. PROCESS EMAILS
# =========================================================
elif menu == "📧 Process Emails":
    st.subheader("Process Emails")

    if st.button("Run Email Processor"):
        with st.spinner("Processing emails..."):
            count = email_processor.process_and_update(excel_handler)
        st.success(f"Email processing completed. {count} item(s) updated.")

# =========================================================
# 3. REMINDER SCHEDULER
# =========================================================
elif menu == "⏰ Run Reminder Scheduler":
    st.subheader("Run Reminder Scheduler")

    if st.button("📤 Send Task Reminders"):
        with st.spinner("Sending reminders..."):
            sent = reminder_scheduler.run()
        st.success(f"{sent} reminder(s) sent successfully.")

elif menu == "📤 Send Task Reminders":
    st.subheader("📤 Send Task Reminders")
    
    df = excel_handler.load_data()
    
    if df.empty:
        st.info("No tasks available")
    else:
        # ✅ NEW: Handle both column name variants
        status_col = 'status' if 'status' in df.columns else 'Status'
        
        # Filter OPEN tasks with safe column access
        open_tasks = df[df[status_col].astype(str).str.upper() == 'OPEN']
        
        st.write(f"**📊 Found {len(open_tasks)} OPEN tasks**")
        
        if open_tasks.empty:
            st.info("✅ No open tasks requiring reminders")
        else:
            # Show preview
            st.write("**Tasks that will receive reminders:**")
            
            # Safe column access for display
            display_cols = []
            for col in ['task_id', 'owner', 'task_text', 'priority', 'deadline']:
                if col in open_tasks.columns:
                    display_cols.append(col)
            
            st.dataframe(open_tasks[display_cols])
            
            if st.button("📧 Send Reminders Now"):
                with st.spinner("Sending reminders..."):
                    try:
                        # Use run_reminders.py logic
                        import subprocess
                        result = subprocess.run(
                            ['python3', 'run_reminders.py'],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ Reminders sent successfully!")
                            st.text(result.stdout)
                        else:
                            st.error("❌ Error sending reminders")
                            st.text(result.stderr)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# =========================================================
# 4. MANUAL ENTRY
# =========================================================
elif menu == "✍️ Manual Entry":
    st.subheader("Add Manual Follow-up")
    
    with st.form("manual_entry_form"):
        owner = st.text_input(
            "Owner (First Name)",
            placeholder="e.g., Sarika, Aditya, Praveen"
        )
        
        task_text = st.text_area(
            "Task Description",
            placeholder="e.g., Review Q4 financial statements"
        )
        
        cc = st.text_input(
            "CC (comma separated emails or names)",
            placeholder="sarika.gupta@..., Anurag, hr@koenig-solutions.com"
        )
        
        priority = st.selectbox(
            "Priority",
            ["URGENT", "HIGH", "MEDIUM", "LOW"],
            index=2
        )
        
        deadline_date = st.date_input("Deadline")
        
        submitted = st.form_submit_button("Save")
        
        if submitted:
            if owner and task_text:
                try:
                    # ✅ DIRECTLY use ExcelHandler's add_entry method
                    total = excel_handler.add_entry(
                        subject=task_text,
                        owner=owner,
                        due_date=deadline_date,
                        remarks=f"Priority: {priority}",
                        cc=cc
                    )
                    
                    st.success(f"✅ Task added successfully! Total tasks: {total}")
                    st.info(f"👤 Assigned to: {owner}")
                    st.info(f"📅 Deadline: {deadline_date}")
                    st.info(f"🎯 Priority: {priority}")
                    
                except Exception as e:
                    st.error(f"❌ Error adding task: {str(e)}")
                    # Fallback
                    try:
                        total = excel_handler.append_rows([{
                            "Subject": task_text,
                            "Owner": owner,
                            "CC": cc,
                            "Due Date": deadline_date,
                            "Remarks": f"Priority: {priority}",
                            "Status": "OPEN",
                            "Created On": datetime.now(),
                            "Last Updated": datetime.now()
                        }])
                        st.success(f"✅ Task added via fallback! Total: {total}")
                    except Exception as e2:
                        st.error(f"❌ Fallback also failed: {str(e2)}")
            else:
                st.warning("⚠️ Please fill in Owner and Task Description")
                
# =========================================================
# 5. BULK MOM UPLOAD 
# =========================================================
elif menu == "📄 Bulk MOM Upload":
    st.subheader("📄 Bulk MOM Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mom_subject = st.text_input(
            "MOM Subject/Title",
            placeholder="e.g., MOM-20250131 | Finance Team Meeting"
        )
    
    with col2:
        default_owner = st.text_input(
            "Default Owner",
            value="Praveen"
        )
    
    # CC Input
    cc_input = st.text_input(
        "📧 CC (comma-separated emails)",
        value=st.session_state.get('global_cc', ''),  # ✅ New
        placeholder="email1@example.com, email2@example.com",
        help="These people will be CC'd on all task notifications"
    )

    mom_text = st.text_area(
        "📝 Paste MOM Content (one task per line)",
        height=300,
        placeholder="Examples:\nUpdate TDS return. @Tax\nPrepare board presentation. @TASK\nReview report. @Finance",
        key="mom_text_input"
    )
    
    # Show priority legend
    with st.expander("ℹ️ Priority Rules"):
        st.markdown("""
        **Automatic Priority Assignment:**
        
        🔴 **URGENT** (1 day deadline):
        - Tax/Statutory tasks (TDS, GST, VAT, Filing)
        - Contains "urgent", "asap", "immediately"
        - Critical departments (Finance, Tax, CEO, Legal)
        - Deadline < 2 days
        
        🟠 **HIGH** (3 days deadline):
        - Reports, Presentations, Approvals
        - Contains "important", "essential", "crucial"
        - High-priority departments (HR, Operations, Sales)
        - Deadline < 5 days
        
        🟡 **MEDIUM** (7 days deadline):
        - Regular tasks
        - Deadline < 10 days
        
        🟢 **LOW** (14 days deadline):
        - Routine tasks, no specific deadline
        """)
    
    # Parse button
    if st.button("🔍 Parse Tasks", type="secondary"):
        if not mom_text.strip():
            st.warning("⚠️ Please paste MOM content")
        else:
            try:
                from bulk_mom_processor import parse_bulk_mom
                from priority_manager import get_priority_emoji
                
                # Parse MOM with CC
                tasks = parse_bulk_mom(
                    mom_subject=mom_subject,
                    mom_text=mom_text,
                    default_owner=default_owner,
                    default_deadline_days=None,
                    cc=cc_input.strip()
                )
                
                if tasks:
                    # Store in session state for deadline editing
                    st.session_state['parsed_tasks'] = tasks
                    st.session_state['mom_subject'] = mom_subject
                    st.session_state['mom_cc'] = cc_input.strip()
                    st.success(f"✅ Parsed {len(tasks)} task(s). Set individual deadlines below.")
                else:
                    st.warning("No tasks extracted. Use @username to assign tasks.")
                    
            except Exception as e:
                st.error(f"❌ Error parsing: {str(e)}")
    
    # Show parsed tasks with individual deadline inputs
    if 'parsed_tasks' in st.session_state and st.session_state['parsed_tasks']:
        st.markdown("---")
        st.markdown("### 📋 Set Individual Deadlines for Each Task")
        
        # Show CC info
        if st.session_state.get('mom_cc'):
            st.info(f"📧 CC: {st.session_state['mom_cc']}")
        
        tasks = st.session_state['parsed_tasks']
        
        # Create columns for headers
        header_cols = st.columns([0.5, 2, 1.5, 1, 1])
        with header_cols[0]:
            st.markdown("**#**")
        with header_cols[1]:
            st.markdown("**Task**")
        with header_cols[2]:
            st.markdown("**Owner**")
        with header_cols[3]:
            st.markdown("**Priority**")
        with header_cols[4]:
            st.markdown("**Deadline (Days)**")
        
        st.markdown("---")
        
        # Store deadline inputs
        if 'task_deadlines' not in st.session_state:
            st.session_state['task_deadlines'] = {}
        
        # Display each task with deadline input
        for i, task in enumerate(tasks):
            from priority_manager import get_priority_emoji
            
            cols = st.columns([0.5, 2, 1.5, 1, 1])
            
            with cols[0]:
                st.write(f"**{i+1}**")
            
            with cols[1]:
                task_display = task['task_text'][:80] + "..." if len(task['task_text']) > 80 else task['task_text']
                st.write(task_display)
            
            with cols[2]:
                st.write(task['owner'])
            
            with cols[3]:
                emoji = get_priority_emoji(task.get('priority', 'MEDIUM'))
                st.write(f"{emoji} {task.get('priority', 'MEDIUM')}")
            
            with cols[4]:
                # Get default deadline based on priority
                default_deadline = {
                    'URGENT': 1,
                    'HIGH': 3,
                    'MEDIUM': 7,
                    'LOW': 14
                }.get(task.get('priority', 'MEDIUM'), 7)
                
                # Deadline input for this specific task
                deadline = st.number_input(
                    "Days",
                    min_value=1,
                    max_value=90,
                    value=default_deadline,
                    key=f"deadline_{i}",
                    label_visibility="collapsed"
                )
                
                # Store in session state
                st.session_state['task_deadlines'][i] = deadline
        
        st.markdown("---")
        
        # Option to modify CC before saving
        with st.expander("✏️ Modify CC (Optional)"):
            updated_cc = st.text_input(
                "Update CC emails",
                value=st.session_state.get('mom_cc', ''),
                key="cc_update"
            )
            if st.button("Update CC"):
                st.session_state['mom_cc'] = updated_cc
                st.success("CC updated!")
        
        
        # Save button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("💾 Save All Tasks"):
                # Build new_rows list in the CORRECT format for ExcelHandler
               new_rows = []
              for i, task in enumerate(st.session_state.parsed_tasks):
                    deadline_days = st.session_state.task_deadlines[i]
                    deadline = (datetime.now() + timedelta(days=deadline_days))
            
                    # Use the SAME format as ExcelHandler.add_entry() expects
                    new_rows.append({
                        "Subject": task['task_text'],  # Map task_text to Subject
                        "Owner": task['owner'],
                        "CC": task.get('cc', st.session_state.get('mom_cc', '')),
                        "Due Date": deadline,
                        "Remarks": f"MOM: {st.session_state.get('mom_subject', '')} | Task ID: {task['task_id']}",
                        "Status": "OPEN",
                        "Created On": datetime.now(),
                        "Last Updated": datetime.now()
                    })
        
                try:
                    # ✅ FIXED: Now using the correct column format
                    if new_rows:
                        total = excel_handler.append_rows(new_rows)
                        st.success(f"✅ Saved {len(new_rows)} tasks! Total in registry: {total}")
                    else:
                        st.error("No valid tasks to save")
                
                except Exception as e:
                    st.error(f"❌ Error saving tasks: {str(e)}")
                    st.info("Trying alternative save method...")
            
                    # Fallback: Save directly to Excel
                    try:
                        existing_df = pd.read_excel(EXCEL_FILE_PATH) if os.path.exists(EXCEL_FILE_PATH) else pd.DataFrame()
                
                        # Build DataFrame in the correct format
                        formatted_rows = []
                        for task in st.session_state.parsed_tasks:
                            deadline_days = st.session_state.task_deadlines[i]
                            deadline = (datetime.now() + timedelta(days=deadline_days))
                    
                           formatted_rows.append({
                                "Subject": task['task_text'],
                                "Owner": task['owner'],
                                "CC": task.get('cc', st.session_state.get('mom_cc', '')),
                                "Due Date": deadline,
                                "Remarks": f"MOM: {st.session_state.get('mom_subject', '')}",
                                "Status": "OPEN",
                                "Created On": datetime.now(),
                                "Last Updated": datetime.now()
                           })
                
                        new_df = pd.DataFrame(formatted_rows)
                        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                        combined_df.to_excel(EXCEL_FILE_PATH, index=False)
                        total = len(combined_df)
                        st.success(f"✅ Saved {len(formatted_rows)} tasks via fallback! Total: {total}")
                
                    except Exception as e2:
                        st.error(f"❌ Fallback also failed: {str(e2)}")
                        total = 0

                # Clear session state regardless
                if 'parsed_tasks' in st.session_state:
                    del st.session_state.parsed_tasks
                if 'task_deadlines' in st.session_state:
                    del st.session_state.task_deadlines
                if 'mom_subject' in st.session_state:
                    del st.session_state.mom_subject
                if 'mom_cc' in st.session_state:
                    del st.session_state.mom_cc
        
                st.rerun()
# =========================================================
# ⚠️ SHODDY CHECK
# =========================================================
elif menu == "⚠️ Shoddy Check":
    st.title("⚠️ Shoddy Work Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Check Overdue Tasks", type="primary"):
            with st.spinner("Checking overdue tasks..."):
                from shoddy_manager import check_overdue_tasks
                count = check_overdue_tasks()
            
            if count > 0:
                st.error(f"⚠️ Sent {count} shoddy notification(s) to HR")
            else:
                st.success("✅ No overdue tasks found!")
    
    with col2:
        if st.button("📋 View Shoddy Log"):
                        
            log_file = Path("data/shoddy_log.xlsx")
            
            if log_file.exists():
                df = pd.read_excel(log_file)
                
                if not df.empty:
                    st.dataframe(
                        df[["shoddy_date", "owner", "task_text", "days_overdue", "priority"]],
                        use_container_width=True
                    )
                    
                    # Stats
                    st.markdown("### 📊 Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Shoddy", len(df))
                    
                    with col2:
                        owner_counts = df["owner"].value_counts()
                        worst_performer = owner_counts.index[0] if not owner_counts.empty else "N/A"
                        st.metric("Most Shoddy", worst_performer)
                    
                    with col3:
                        avg_overdue = df["days_overdue"].mean()
                        st.metric("Avg Days Overdue", f"{avg_overdue:.1f}")
                else:
                    st.info("No shoddy incidents recorded")
            else:
                st.info("No shoddy log file found")
    
    st.divider()
    
    # Acknowledgement section
    st.subheader("🎉 Send Acknowledgement")
    
    st.info("Manually send acknowledgement for completed task")
    
    with st.form("send_acknowledgement"):
        ack_owner = st.text_input("Owner Name")
        ack_email = st.text_input("Owner Email")
        ack_task_id = st.text_input("Task ID")
        ack_task_text = st.text_area("Task Description")
        ack_rating = st.selectbox(
            "Performance Rating",
            ["excellent", "good", "well done", "completed"]
        )
        
        if st.form_submit_button("📧 Send Acknowledgement"):
            if ack_owner and ack_email and ack_task_text:
                from acknowledgement_manager import send_acknowledgement
                
                task = {
                    "task_id": ack_task_id,
                    "task_text": ack_task_text,
                    "priority": "medium",
                    "deadline": datetime.now().strftime("%Y-%m-%d"),
                    "completed_date": datetime.now().strftime("%Y-%m-%d"),
                    "meeting_id": "Manual"
                }
                
                performance = {
                    "excellent": {
                        "rating": "excellent",
                        "emoji": "🌟",
                        "message": "Outstanding performance!"
                    },
                    "good": {
                        "rating": "good",
                        "emoji": "👍",
                        "message": "Good work!"
                    },
                    "well done": {
                        "rating": "well done",
                        "emoji": "✅",
                        "message": "Well done!"
                    },
                    "completed": {
                        "rating": "completed",
                        "emoji": "✓",
                        "message": "Task completed."
                    }
                }[ack_rating]
                
                send_acknowledgement(ack_owner, ack_email, task, performance)
                st.success(f"✅ Acknowledgement sent to {ack_owner}")
            else:
                st.error("Please fill all fields")

# =========================================================
# 7. LOGS / STATUS
# =========================================================

# =========================================================
# CHANGE PASSWORD
# =========================================================
elif menu == "🔑 Change Password":
    st.subheader("🔑 Change Your Password")
    
    st.info("💡 Use a strong password with at least 6 characters")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("🔐 Change Password", use_container_width=True)
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("❌ Please fill all fields")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            elif new_password != confirm_password:
                st.error("❌ New passwords don't match")
            else:
                # Verify current password
                user_info = user_manager.authenticate(
                    st.session_state.user_info['username'],
                    current_password
                )
                
                if not user_info:
                    st.error("❌ Current password is incorrect")
                else:
                    # Change password
                    success = user_manager.change_password(
                        st.session_state.user_info['username'],
                        new_password
                    )
                    
                    if success:
                        st.success("✅ Password changed successfully!")
                        st.info("💡 Please use your new password next time you login")
                        
                        # Send confirmation email
                        try:
                            email_body = f"""Dear {st.session_state.user_info['full_name']},

Your password has been changed successfully.

Account Details:
- Username: {st.session_state.user_info['username']}
- Changed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you did not make this change, please contact IT immediately.

Best regards,
Task Follow-up System
Koenig Solutions
"""
                            
                            email_processor.send_email(
                                to_email=st.session_state.user_info['email'],
                                subject="🔐 Password Changed Successfully",
                                body=email_body
                            )
                            
                            st.success("📧 Confirmation email sent to your email address")
                        except:
                            pass  # Email is optional
                    else:
                        st.error("❌ Failed to change password. Please try again.")

elif menu == "📊 Logs / Status":
    st.subheader("System Status")

    st.write("**Excel File:**", EXCEL_FILE_PATH)
    st.write("**Last Checked:**", datetime.now().strftime("%d-%b-%Y %H:%M:%S"))

    if os.path.exists(EXCEL_FILE_PATH):
        st.success("Excel file found and accessible.")
    else:
        st.error("Excel file missing.")

elif menu == "⚙️ Run Engines":
    st.subheader("⚙️ Engine Control Panel (Preview Mode)")
    st.caption("Safely run backend engines and preview outputs")

    st.divider()

    # 1️⃣ Fetch Emails
    if st.button("📥 Fetch Emails"):
        with st.spinner("Fetching inbox messages..."):
            out, err = run_script("graph_inbox_test.py")
        if err:
            st.error(err)
        else:
            st.success("Inbox fetched successfully")
            st.code(out)

    st.divider()

    # 2️⃣ Parse MOM
    if st.button("🧾 Parse MOM"):
        with st.spinner("Parsing MOM emails..."):
            out, err = run_script("mom_parser.py")
        if err:
            st.error(err)
        else:
            st.success("MOM parsed successfully")
            st.json(eval(out))  # MOM output is already dict-like

    st.divider()

    # 3️⃣ Update Task Registry
    if st.button("📌 Update Task Registry"):
        with st.spinner("Updating task registry..."):
            out, err = run_script("task_registry.py")
        if err:
            st.error(err)
        else:
            st.success("Task registry updated")
            st.code(out)

    st.divider()

    # 4️⃣ Generate Replies (Preview only)
    if st.button("📧 Generate Reply (Preview)"):
        with st.spinner("Generating reply draft..."):
            out, err = run_script("reply_decision_engine.py")
        if err:
            st.error(err)
        else:
            st.success("Reply generated (NOT SENT)")
            st.text_area(
                "Email Preview",
                out,
                height=250
            )

    st.divider()

    # 5️⃣ Send Reminders
    if st.button("⏰ Send Reminders"):
        with st.spinner("Sending reminders..."):
            out, err = run_script("reminder_engine.py")
        if err:
            st.error(err)
        else:
            st.success("Reminder process completed")
            st.code(out)


# Rebuild trigger - Thu Jan  1 16:53:52 IST 2026
