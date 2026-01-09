import os
import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from datetime import datetime, timedelta

from config import EXCEL_FILE_PATH, APP_TITLE, validate_paths
from utils.excel_handler import ExcelHandler
from utils.task_normalizer import normalize_df
from utils.safe_keys import unique_key
from reminder_scheduler import get_next_reminder_date
from priority_manager import get_priority_emoji
from email_processor import EmailProcessor
from reminder_scheduler import ReminderScheduler
from manual_processor import ManualTaskProcessor
from user_manager import UserManager
from bulk_mom_processor import parse_bulk_mom
from priority_manager import get_priority_emoji
from utils.task_normalizer import normalize_df
from datetime import datetime
from config import EXCEL_FILE_PATH

# Page modules
from pages.view_followups import render_view_followups
from pages.process_emails import render_process_emails
from pages.reminder_scheduler_page import render_reminder_scheduler
from pages.send_task_reminders import render_send_task_reminders
from pages.manual_entry import render_manual_entry
from pages.bulk_mom_upload import render_bulk_mom_upload
from pages.shoddy_check import render_shoddy_check
from pages.debug_tasks import render_debug_tasks
from pages.change_password import render_change_password
from pages.logs_status import render_logs_status
from pages.run_engines import render_run_engines

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
LOGO_PATH = BASE_DIR / "assets" / "koenig_logo.png"
load_dotenv(dotenv_path=ENV_PATH)

# ----------------------------
# Cached singletons
# ----------------------------
@st.cache_resource
def get_user_manager():
    return UserManager()

@st.cache_resource
def init_handlers():
    excel_handler = ExcelHandler(EXCEL_FILE_PATH)
    email_processor = EmailProcessor()
    reminder_scheduler = ReminderScheduler(EXCEL_FILE_PATH)
    manual_processor = ManualTaskProcessor()
    return excel_handler, email_processor, reminder_scheduler, manual_processor


# ----------------------------
# Auth
# ----------------------------
def login_page(user_manager: UserManager):
    st.set_page_config(page_title="Login - Task Follow-up System", layout="centered")
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)
    st.markdown("<h2 style='text-align:center'>🔐 Task Follow-up System</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("🔓 Login", use_container_width=True)

        if submitted:
            user_info = user_manager.authenticate(username, password)
            if user_info:
                st.session_state.authenticated = True
                st.session_state.user_info = user_info
                st.session_state.permissions = user_manager.get_user_permissions(user_info)
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    st.caption("🔒 Contact IT for access")


def logout():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.permissions = None
    st.rerun()

# ----------------------------
# App Boot
# ----------------------------
user_manager = get_user_manager()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.permissions = {}

if "global_cc" not in st.session_state:
    st.session_state.global_cc = ""

if not st.session_state.authenticated:
    login_page(user_manager)
    st.stop()

# Now authenticated
st.set_page_config(page_title=APP_TITLE, layout="wide")
validate_paths()

excel_handler, email_processor, reminder_scheduler, manual_processor = init_handlers()

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)

    st.markdown("### Follow-up & Reminder Agent")
    st.markdown("---")

    ui = st.session_state.user_info
    st.markdown(f"**👤 {ui['full_name']}**")
    st.caption(f"📧 {ui['email']}")
    st.caption(f"🏢 {ui.get('department','')}")
    st.caption(f"🔑 {ui.get('role','').replace('_',' ').title()}")

    if st.button("🚪 Logout", use_container_width=True):
        logout()

    st.markdown("---")

    st.session_state.global_cc = st.text_input(
        "Default CC (Global)",
        value=st.session_state.global_cc,
        placeholder="email1@..., email2@..."
    )

    st.markdown("---")

# ----------------------------
# Navigation based on permissions
# ----------------------------
perm = st.session_state.permissions or {}

menu_options = [
    "📊 Dashboard Analytics",
    "📥 View Follow-ups",
    "🔍 DEBUG Tasks",
]

if perm.get("send_reminders"):
    menu_options += ["📧 Process Emails", "⏰ Run Reminder Scheduler", "📤 Send Task Reminders"]

if perm.get("create_tasks"):
    menu_options += ["✍️ Manual Entry", "📄 Bulk MOM Upload"]

if perm.get("manage_shoddy"):
    menu_options += ["⚠️ Shoddy Check"]

if perm.get("manage_users"):
    menu_options += ["👥 User Management"]  # keep if you have a page/module for it

menu_options += ["🔑 Change Password", "📊 Logs / Status", "⚙️ Run Engines"]

menu = st.sidebar.radio("Select Action", menu_options)

# ----------------------------
# Route
# ----------------------------
st.title(APP_TITLE)
st.caption("Follow-up & Reminder Agent")

if menu == "📊 Dashboard Analytics":
    from dashboard_analytics import render_dashboard
    render_dashboard(excel_handler)

elif menu == "📥 View Follow-ups":
    render_view_followups(excel_handler, user_manager)

elif menu == "🔍 DEBUG Tasks":
    render_debug_tasks(excel_handler)

elif menu == "📧 Process Emails":
    render_process_emails(email_processor, excel_handler)

elif menu == "⏰ Run Reminder Scheduler":
    render_reminder_scheduler(reminder_scheduler)

elif menu == "📤 Send Task Reminders":
    render_send_task_reminders(excel_handler)

elif menu == "✍️ Manual Entry":
    render_manual_entry(excel_handler)

elif menu == "📄 Bulk MOM Upload":
    render_bulk_mom_upload(excel_handler)

elif menu == "⚠️ Shoddy Check":
    render_shoddy_check()

elif menu == "🔑 Change Password":
    render_change_password(user_manager)

elif menu == "📊 Logs / Status":
    render_logs_status()

elif menu == "⚙️ Run Engines":
    render_run_engines()
    
def render_view_followups(excel_handler, user_manager):
    st.subheader("📥 View Follow-ups")

    raw_df = excel_handler.load_data()
    df = normalize_df(raw_df)

    if df.empty:
        st.info("📭 No follow-ups available.")
        return

    show_all = st.checkbox("📋 Show all tasks", value=True)

    if not show_all:
        df = user_manager.filter_tasks_by_user(df, st.session_state.user_info)

    st.write(f"✅ Showing **{len(df)}** task(s)")

    for idx, row in df.iterrows():
        subject = row.get("Subject", "")
        owner = row.get("Owner", "")
        priority = row.get("Priority", "MEDIUM")
        due_date = row.get("Due Date", "")
        status = row.get("Status", "OPEN")
        remarks = row.get("Remarks", "")
        task_id = row.get("task_id", row.get("Task ID", None))

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"""
**📝 Subject:** {subject}  
**👤 Owner:** {owner}  
**🎯 Priority:** {get_priority_emoji(priority)} {priority}  
**📅 Due Date:** {due_date}  
**🏷️ Status:** {"🟡 OPEN" if status == "OPEN" else "🟢 COMPLETED"}  
**📝 Remarks:** {remarks or ""}
"""
            )

        with col2:
            if status == "OPEN":
                btn_key = unique_key("mark_done", idx, task_id)
                if st.button("✅ Mark Done", key=btn_key):
                    # Prefer task_id update if available
                    success = False
                    if task_id not in [None, "", "nan"]:
                        try:
                            success = excel_handler.update_status_by_task_id(task_id, "DONE")
                        except Exception:
                            success = False

                    # Fallback to index update (older Excel format)
                    if not success:
                        success = excel_handler.update_status(idx, "DONE")

                    if success:
                        st.success("✅ Task marked as done!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update task")

        # Reminder info (safe)
        last_reminder = row.get("Last Reminder Date", None)
        due = row.get("Due Date", None)

        try:
            next_rem = get_next_reminder_date(priority, last_reminder, due)
        except Exception:
            next_rem = None

        st.caption(f"Last Reminder: {last_reminder if pd.notna(last_reminder) else '—'}")
        st.caption(f"Next Reminder: {next_rem if next_rem else 'Calculated on next run'}")

        st.divider()

def render_process_emails(email_processor, excel_handler):
    st.subheader("📧 Process Emails")

    if st.button("Run Email Processor"):
        with st.spinner("Processing emails..."):
            count = email_processor.process_and_update(excel_handler)
        st.success(f"✅ Email processing completed. {count} item(s) updated.")

def render_reminder_scheduler(reminder_scheduler):
    st.subheader("⏰ Run Reminder Scheduler")

    if st.button("📤 Send Task Reminders"):
        with st.spinner("Sending reminders..."):
            sent = reminder_scheduler.run()
        st.success(f"✅ {sent} reminder(s) sent successfully.")

def render_send_task_reminders(excel_handler):
    st.subheader("📤 Send Task Reminders")

    df = normalize_df(excel_handler.load_data())
    if df.empty:
        st.info("No tasks available.")
        return

    open_tasks = df[df["Status"] == "OPEN"].copy()
    st.write(f"📌 Found **{len(open_tasks)}** OPEN tasks")

    if open_tasks.empty:
        st.success("✅ No open tasks requiring reminders.")
        return

    st.dataframe(open_tasks[["Subject", "Owner", "Priority", "Due Date", "Status"]], use_container_width=True)

    if st.button("📧 Send Reminders Now"):
        with st.spinner("Running reminder engine..."):
            result = subprocess.run(["python3", "run_reminders.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ Reminders sent successfully!")
            st.text(result.stdout)
        else:
            st.error("❌ Error sending reminders")
            st.text(result.stderr)

def render_manual_entry(excel_handler):
    st.subheader("✍️ Manual Entry")

    with st.form("manual_entry_form"):
        owner = st.text_input("Owner (Name)")
        task_text = st.text_area("Task Description")
        cc = st.text_input("CC", value=st.session_state.get("global_cc", ""))
        priority = st.selectbox("Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
        deadline_date = st.date_input("Deadline")

        submitted = st.form_submit_button("Save")

        if submitted:
            if not owner or not task_text:
                st.warning("⚠️ Please fill in Owner and Task Description")
                return

            try:
                total = excel_handler.add_entry(
                    subject=task_text,
                    owner=owner,
                    due_date=deadline_date,
                    remarks=f"Priority: {priority}",
                    cc=cc,
                )
                st.success(f"✅ Task added! Total tasks: {total}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ add_entry failed: {e}")
                st.info("Trying fallback append...")

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
                st.rerun()

def render_bulk_mom_upload(excel_handler):
    st.subheader("📄 Bulk MOM Upload")

    col1, col2 = st.columns([2, 1])
    with col1:
        mom_subject = st.text_input("MOM Subject/Title")
    with col2:
        default_owner = st.text_input("Default Owner", value="Praveen")

    cc_input = st.text_input(
        "📧 CC (comma-separated emails)",
        value=st.session_state.get("global_cc", ""),
        placeholder="email1@..., email2@..."
    )

    mom_text = st.text_area("📝 Paste MOM Content (one task per line)", height=300)

    if st.button("🔍 Parse Tasks", type="secondary"):
        if not mom_text.strip():
            st.warning("⚠️ Please paste MOM content")
        else:
            tasks = parse_bulk_mom(
                mom_subject=mom_subject,
                mom_text=mom_text,
                default_owner=default_owner,
                default_deadline_days=None,
                cc=cc_input.strip()
            )
            if tasks:
                st.session_state["parsed_tasks"] = tasks
                st.session_state["mom_subject"] = mom_subject
                st.session_state["mom_cc"] = cc_input.strip()
                st.success(f"✅ Parsed {len(tasks)} task(s). Set deadlines below.")
            else:
                st.warning("No tasks extracted.")

    if "parsed_tasks" not in st.session_state or not st.session_state["parsed_tasks"]:
        return

    st.markdown("---")
    st.markdown("### 📋 Set deadlines")

    tasks = st.session_state["parsed_tasks"]

    if "task_deadlines" not in st.session_state:
        st.session_state["task_deadlines"] = {}

    for i, task in enumerate(tasks):
        cols = st.columns([0.5, 2.5, 1.5, 1, 1])
        with cols[0]:
            st.write(i + 1)
        with cols[1]:
            st.write(task["task_text"])
        with cols[2]:
            st.write(task["owner"])
        with cols[3]:
            pr = task.get("priority", "MEDIUM")
            st.write(f"{get_priority_emoji(pr)} {pr}")
        with cols[4]:
            default_days = {"URGENT": 1, "HIGH": 3, "MEDIUM": 7, "LOW": 14}.get(task.get("priority","MEDIUM"), 7)
            st.session_state["task_deadlines"][i] = st.number_input(
                "Days",
                min_value=1,
                max_value=90,
                value=default_days,
                key=f"deadline_days_{i}",
                label_visibility="collapsed"
            )

    st.markdown("---")
    if st.button("💾 Save All Tasks"):
        new_rows = []
        for i, task in enumerate(tasks):
            days = st.session_state["task_deadlines"][i]
            deadline = (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")

            new_rows.append({
                "task_id": task.get("task_id"),
                "meeting_id": task.get("meeting_id",""),
                "Subject": task.get("task_text",""),
                "Owner": task.get("owner",""),
                "Status": "OPEN",
                "Priority": task.get("priority","MEDIUM"),
                "Due Date": deadline,
                "Remarks": f"MOM: {st.session_state.get('mom_subject','')}",
                "CC": task.get("cc", st.session_state.get("mom_cc","")),
                "Created On": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        total = excel_handler.append_rows(new_rows)
        st.success(f"✅ Saved {len(new_rows)} tasks! Total in registry: {total}")

        # Clear state
        for k in ["parsed_tasks", "task_deadlines", "mom_subject", "mom_cc"]:
            if k in st.session_state:
                del st.session_state[k]

        st.rerun()

def render_shoddy_check():
    st.title("⚠️ Shoddy Work Check")

    if st.button("🔍 Check Overdue Tasks", type="primary"):
        with st.spinner("Checking overdue tasks..."):
            count = check_overdue_tasks()
        if count > 0:
            st.error(f"⚠️ Sent {count} shoddy notification(s) to HR")
        else:
            st.success("✅ No overdue tasks found!")

    st.divider()

    log_file = Path("data/shoddy_log.xlsx")
    if log_file.exists():
        df = pd.read_excel(log_file)
        if not df.empty:
            st.dataframe(df, use_container_width=True)

def render_debug_tasks(excel_handler):
    st.title("🔍 DEBUG Tasks")
    df = normalize_df(excel_handler.load_data())
    st.write("Rows:", len(df))
    st.write("Columns:", list(df.columns))
    st.dataframe(df, use_container_width=True)

def render_change_password(user_manager):
    st.subheader("🔑 Change Password")

    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        submitted = st.form_submit_button("Change Password")

        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                username = st.session_state.user_info["username"]
                user = user_manager.authenticate(username, current_password)
                if not user:
                    st.error("Current password incorrect")
                else:
                    user_manager.change_password(username, new_password)
                    st.success("✅ Password changed successfully!")

def render_logs_status():
    st.subheader("📊 Logs / Status")
    st.write("Excel File:", EXCEL_FILE_PATH)
    st.write("Last Checked:", datetime.now().strftime("%d-%b-%Y %H:%M:%S"))
    if os.path.exists(EXCEL_FILE_PATH):
        st.success("Excel file found and accessible.")
    else:
        st.error("Excel file missing.")

def run_script(script_name):
    r = subprocess.run(["python3", script_name], capture_output=True, text=True)
    return r.stdout, r.stderr

def render_run_engines():
    st.subheader("⚙️ Run Engines")

    engines = [
        ("📥 Fetch Emails", "graph_inbox_test.py"),
        ("🧾 Parse MOM", "mom_parser.py"),
        ("📌 Update Task Registry", "task_registry.py"),
        ("📧 Generate Reply (Preview)", "reply_decision_engine.py"),
        ("⏰ Send Reminders", "reminder_engine.py"),
    ]

    for label, script in engines:
        if st.button(label):
            out, err = run_script(script)
            if err:
                st.error(err)
            else:
                st.success("✅ Success")
                st.code(out)
        st.divider()
