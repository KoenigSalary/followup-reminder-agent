import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from config import EXCEL_FILE_PATH, APP_TITLE, validate_paths
from utils.excel_handler import ExcelHandler
from email_processor import EmailProcessor
from reminder_scheduler import ReminderScheduler
from manual_processor import ManualTaskProcessor
from user_manager import UserManager

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
