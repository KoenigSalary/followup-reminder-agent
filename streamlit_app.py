#!/usr/bin/env python3
"""
Streamlit App - Follow-up & Reminder Team
FINAL VERSION - Logo shifted right for perfect alignment
"""

import os
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import importlib
import inspect
from datetime import datetime

from utils.excel_handler import ExcelHandler
from file_utils import safe_excel_operation, create_file_if_not_exists, backup_file, FileLockError

# Get the base directory more reliably
if "__file__" in globals():
    BASE_DIR = Path(__file__).resolve().parent
else:
    BASE_DIR = Path(os.getcwd())

# Excel file path
REGISTRY_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"


def ensure_registry_exists():
    """Create registry file if missing (safe + correct columns)."""

    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

    def create_registry(file_path):
        # ✅ MUST match ExcelHandler required_columns
        df = pd.DataFrame(columns=[
            "task_id", "meeting_id", "Subject", "Owner", "CC", "Due Date",
            "Remarks", "Priority", "Status", "Created On", "Last Updated",
            "Last Reminder Date", "Last Reminder On", "Completed Date", "Auto Reply Sent"
        ])
        df.to_excel(file_path, index=False)

    # 1) Ensure file exists (no locking needed for first create)
    try:
        create_file_if_not_exists(REGISTRY_FILE, create_registry)
    except Exception as e:
        st.error(f"❌ Failed to create registry file: {e}")
        raise


def save_tasks_to_registry(df: pd.DataFrame):
    """Save tasks to registry with safe file handling."""

    # Optional: Create backup before writing
    try:
        if REGISTRY_FILE.exists():
            backup_path = backup_file(REGISTRY_FILE)
            st.info(f"📋 Backup created: {backup_path.name}")
    except Exception as e:
        st.warning(f"⚠️ Could not create backup: {e}")

    def write_operation(file_path):
        df.to_excel(file_path, index=False)

    try:
        safe_excel_operation(REGISTRY_FILE, write_operation)
        st.success("✅ Tasks saved successfully!")
    except FileLockError as e:
        st.error(f"❌ Could not save tasks: {e}")
        st.info("💡 Please close the Excel file if it's open and try again.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")


def get_excel_handler():
    """Get ExcelHandler with correct path (Cloud-safe)."""
    try:
        ensure_registry_exists()
        return ExcelHandler(str(REGISTRY_FILE))
    except Exception as e:
        st.error(f"❌ Error initializing ExcelHandler: {e}")
        st.exception(e)
        return None


# Page config
st.set_page_config(
    page_title="Follow-up & Reminder Team | Koenig Solutions",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Debug
with st.sidebar:
    debug_mode = st.toggle("🛠 Debug mode", value=False)

if debug_mode:
    st.sidebar.info(f"ExcelHandler loaded from: {inspect.getfile(ExcelHandler)}")
    st.sidebar.info(f"openpyxl spec: {importlib.util.find_spec('openpyxl')}")

# Custom CSS with logo shifted right
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .main .block-container { padding-top: 3rem; }

    .logo-container { text-align: center; padding-left: 40px; }

    .centered-header {
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        margin: 20px auto 0 auto;
        padding: 0;
        line-height: 1.3;
    }

    .login-form-wrapper {
        max-width: 500px;
        margin: 40px auto;
        padding: 0 20px;
    }

    .login-form {
        background: white;
        padding: 35px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }

    .login-form h3 { margin-bottom: 25px; text-align: center; }

    .sidebar-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 15px 10px;
        margin-bottom: 15px;
    }

    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .stTextInput > div > div > input {
        border-radius: 8px;
        padding: 10px;
    }

    .stAlert { border-radius: 8px; margin-top: 20px; }

    hr {
        margin: 25px 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }

    @media (max-width: 768px) {
        .logo-container { padding-left: 0; }
        .centered-header { font-size: 22px; }
        .login-form { padding: 25px; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

def show_login():
    """Display login page with logo shifted right."""
    logo_path = BASE_DIR / "assets" / "koenig_logo.png"

    col1, col2, col3 = st.columns([1.95, 2, 1.2])
    with col2:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        if logo_path.exists():
            st.image(str(logo_path), width=280)
        else:
            st.markdown('<h1 style="color: #1f77b4; font-size: 38px; text-align: center;">🏢 KOENIG</h1>', unsafe_allow_html=True)
            st.markdown('<p style="color: #666; font-size: 16px; text-align: center;">step forward</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<h1 class="centered-header">Follow-up & Reminder Team</h1>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.subheader("🔐 Login")

        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

        if st.button("🚀 Login", use_container_width=True, type="primary"):
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("⚠️ Please enter both username and password")

        st.info("💡 Enter any username/password to access the system")
        st.markdown('</div>', unsafe_allow_html=True)


def show_sidebar():
    """Display sidebar with centered logo."""
    logo_path = BASE_DIR / "assets" / "koenig_logo.png"

    with st.sidebar:
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        if logo_path.exists():
            col1, col2, col3 = st.columns([0.5, 2, 0.5])
            with col2:
                st.image(str(logo_path), width=150)
        else:
            st.markdown("### 🏢 KOENIG")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📧 Follow-up & Reminder Team")
        st.markdown(f"Welcome back, **{st.session_state.username}**! 👋")
        st.markdown("---")

        st.markdown("### 📋 Navigation")
        page = st.radio(
            "Go to",
            ["📊 Dashboard", "📥 View Follow-ups", "✍️ Manual Entry",
             "📂 Bulk MOM Upload", "📧 Send Task Reminders", "⚙️ Settings"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

        st.markdown("---")
        st.caption("© 2026 Koenig Solutions")
        st.caption("Follow-up & Reminder Team v2.0")
        return page


def show_dashboard():
    from views.dashboard_analytics import render_dashboard
    excel_handler = get_excel_handler()
    if excel_handler:
        render_dashboard(excel_handler)


def show_view_followups():
    try:
        from views.view_followups import render_view_followups

        excel_handler = get_excel_handler()
        if not excel_handler:
            return

        try:
            from utils.user_lookup import UserManager
            user_manager = UserManager()
            render_view_followups(excel_handler, user_manager)
        except Exception:
            class DummyUserManager:
                def get_user_email(self, name):
                    return None
            try:
                render_view_followups(excel_handler)
            except Exception:
                render_view_followups(excel_handler, DummyUserManager())

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)


def show_manual_entry():
    try:
        from views.manual_entry import render_manual_entry
        excel_handler = get_excel_handler()
        if excel_handler:
            render_manual_entry(excel_handler)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)


# ✅ keep your show_bulk_upload(), show_send_reminders(), show_settings(), main()
# (Your bulk upload block is already OK in your paste; no changes required there.)

def main():
    if not st.session_state.logged_in:
        show_login()
        return

    page = show_sidebar()
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📥 View Follow-ups":
        show_view_followups()
    elif page == "✍️ Manual Entry":
        show_manual_entry()
    elif page == "📂 Bulk MOM Upload":
        show_bulk_upload()
    elif page == "📧 Send Task Reminders":
        show_send_reminders()
    elif page == "⚙️ Settings":
        show_settings()


if __name__ == "__main__":
    main()
