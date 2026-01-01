# =========================================================
# ENV + PATH SETUP
# =========================================================
import os
import subprocess
from pathlib import Path
from datetime import datetime

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
    
    # Center logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=300)
        st.markdown("##")  # Spacing
    
    st.title("🔐 Task Follow-up System")
    st.caption("Koenig Solutions")
    
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
        st.image(str(LOGO_PATH), width=220)
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
menu_options = ["📥 View Follow-ups"]

if st.session_state.permissions.get('send_reminders'):
    menu_options.extend(["📧 Process Emails", "⏰ Run Reminder Scheduler"])

if st.session_state.permissions.get('create_tasks'):
    menu_options.extend(["✍️ Manual Entry", "📄 Bulk MOM Upload"])

if st.session_state.permissions.get('manage_shoddy'):
    menu_options.append("⚠️ Shoddy Check")

if st.session_state.permissions.get('manage_users'):
    menu_options.append("👥 User Management")

menu_options.append("📊 Logs / Status")

menu = st.sidebar.radio("Select Action", menu_options)

# =========================================================
# 1. VIEW FOLLOW-UPS
# =========================================================
if menu == "📥 View Follow-ups":
    st.subheader("Follow-ups")

    df = excel_handler.load_data()
    
    # ✨ FILTER TASKS BY USER ROLE
    df = user_manager.filter_tasks_by_user(df, st.session_state.user_info)

    if df.empty:
        st.info("No follow-ups available.")
    else:
        for idx, row in df.iterrows():
            subject = row.get("Subject", "N/A")
            owner = row.get("Owner", "N/A")
            due_date = row.get("Due Date", "N/A")
            status = status_badge(row.get("Status", "N/A"))
            remarks = row.get("Remarks", "")

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(
                    f"""
**Subject:** {subject}  
**Owner:** {owner}  
**Due Date:** {due_date}  
**Status:** {status}  
**Remarks:** {remarks}
"""
                )

            with col2:
                if str(row.get("Status", "")).lower() != "completed":
                    if st.button("✅ Mark Completed", key=f"complete_{idx}"):
                        excel_handler.update_status(idx, "COMPLETED")
                        st.success("Marked as completed.")
                        st.rerun()

            st.divider()

            last_reminder = row.get("Last Reminder Date")
            due = row.get("Due Date")

            if hasattr(last_reminder, "date"):
                last_reminder = last_reminder.date()
            if hasattr(due, "date"):
                due = due.date()

            next_reminder = get_next_reminder_date(
                row.get("Priority"),
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

    if st.button("Send Due Reminders"):
        with st.spinner("Sending reminders..."):
            sent = reminder_scheduler.run()
        st.success(f"{sent} reminder(s) sent successfully.")

# =========================================================
# 4. MANUAL ENTRY
# =========================================================
elif menu == "✍️ Manual Entry":
    st.subheader("Add Manual Follow-up")

    with st.form("manual_entry_form"):
        owner = st.text_input("Owner (First Name)", placeholder="e.g., Sarika, Aditya, Praveen")
        task_text = st.text_area("Task Description", placeholder="e.g., Review Q4 financial statements")
        priority = st.selectbox("Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
        deadline_date = st.date_input("Deadline")

        submitted = st.form_submit_button("Save")

        if submitted:
            if owner and task_text:
                result = manual_processor.add_manual_task(
                    owner=owner,
                    task_text=task_text,
                    priority=priority,
                    deadline_date=deadline_date,
                    excel_handler=excel_handler
                )
                
                if result['success']:
                    st.success(result['message'])
                    st.info(f"📋 Task ID: {result['task_id']}")
                    st.info(f"👤 Assigned to: {result['owner']} ({result['employee_id']})")
                    st.info(f"📧 Email sent to: {result['owner_email']}")
                else:
                    st.error(result['message'])
            else:
                st.warning("⚠️ Please fill in Owner and Task Description")

# =========================================================
# 5. BULK MOM UPLOAD 
# =========================================================
elif menu == "📄 Bulk MOM Upload":
    st.subheader("📄 Bulk MOM Upload")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
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
    
    with col3:
        deadline_days = st.number_input(
            "Deadline (Days)",
            min_value=1,
            max_value=30,
            value=None,
            help="Leave empty for auto-priority calculation"
        )
    
    mom_text = st.text_area(
        "📝 Paste MOM Content (one task per line)",
        height=300,
        placeholder="Examples:\nUpdate TDS return. @Tax\nPrepare board presentation. @TASK\nReview report. @Finance"
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
    
    if st.button("📤 Process & Save MOM Tasks", type="primary"):
        if not mom_text.strip():
            st.warning("⚠️ Please paste MOM content")
        else:
            try:
                from bulk_mom_processor import parse_bulk_mom
                from priority_manager import get_priority_emoji
                import pandas as pd
                from datetime import datetime, timedelta
                from pathlib import Path
                
                # Parse MOM
                tasks = parse_bulk_mom(
                    mom_subject=mom_subject,
                    mom_text=mom_text,
                    default_owner=default_owner,
                    default_deadline_days=deadline_days
                )
                
                if tasks:
                    # SAVE TO EXCEL DIRECTLY (Don't rely on append_tasks)
                    task_file = "data/tasks_registry.xlsx"
                    
                    # Load existing tasks
                    if Path(task_file).exists():
                        df_existing = pd.read_excel(task_file)
                    else:
                        df_existing = pd.DataFrame()
                    
                    # Convert tasks to DataFrame
                    new_rows = []
                    for task in tasks:
                        new_row = {
                            "task_id": task["task_id"],
                            "meeting_id": task["meeting_id"],
                            "owner": task["owner"],
                            "task_text": task["task_text"],
                            "status": task["status"],
                            "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "last_reminder_on": task.get("last_reminder"),
                            "last_reminder": None,
                            "last_reminder_date": None,
                            "priority": task.get("priority", "MEDIUM"),
                            "deadline": task.get("deadline"),
                            "completed_date": None,
                            "days_taken": None,
                            "performance_rating": None
                        }
                        new_rows.append(new_row)
                    
                    # Combine and save
                    new_df = pd.DataFrame(new_rows)
                    combined = pd.concat([df_existing, new_df], ignore_index=True)
                    combined.to_excel(task_file, index=False)
                    
                    st.success(f"✅ {len(tasks)} task(s) saved to registry!")
                    
                    # Show tasks with priorities
                    st.markdown("### 📋 Created Tasks")
                    for task in tasks:
                        emoji = get_priority_emoji(task["priority"])
                        st.write(f"{emoji} **{task['owner']}**: {task['task_text']}")
                    
                    # Show summary
                    st.markdown("### 📊 Summary by Owner")
                    owner_counts = new_df["owner"].value_counts()
                    for owner, count in owner_counts.items():
                        st.write(f"- **{owner}**: {count} task(s)")
                    
                    st.balloons()
                    
                else:
                    st.warning("No tasks extracted. Use @username to assign tasks.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# =========================================================
# 6. SHODDY CHECK
# =========================================================
elif menu == "⚠️ Shoddy Check":
    st.subheader("⚠️ Overdue Tasks & Shoddy Management")
    
    st.info("Check for overdue tasks and send shoddy notifications to HR")
    
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
            import pandas as pd
            from pathlib import Path
            
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
            out, err = run_script("reply_engine.py")
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
