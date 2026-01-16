#!/usr/bin/env python3
"""
Streamlit App - Follow-up & Reminder Team
FINAL VERSION - Logo shifted right for perfect alignment
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import importlib
import inspect

# Setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from utils.excel_handler import ExcelHandler

# Excel file path
REGISTRY_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"


def ensure_registry_exists():
    """Create registry file if missing."""
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not REGISTRY_FILE.exists():
        # Create using ExcelHandler's required columns (future-proof)
        # We instantiate a temp handler to get required_columns, but we must ensure file exists first.
        # So we write minimal header that ExcelHandler can expand later.
        df = pd.DataFrame(columns=[
            "task_id", "meeting_id", "Subject", "Owner", "CC", "Due Date",
            "Remarks", "Priority", "Status", "Created On", "Last Updated",
            "Last Reminder Date", "Last Reminder On", "Completed Date", "Auto Reply Sent"
        ])
        df.to_excel(REGISTRY_FILE, index=False)


def get_excel_handler():
    """Get ExcelHandler with correct path (Cloud-safe)."""
    try:
        ensure_registry_exists()
        handler = ExcelHandler(str(REGISTRY_FILE))
        return handler
    except Exception as e:
        st.error(f"❌ Error initializing ExcelHandler: {e}")
        return None


# Page config
st.set_page_config(
    page_title="Follow-up & Reminder Team | Koenig Solutions",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Debug (keep while fixing)
with st.sidebar:
    debug_mode = st.toggle("🛠 Debug mode", value=False)

if debug_mode:
    st.info(f"ExcelHandler loaded from: {inspect.getfile(ExcelHandler)}")
    st.info(f"openpyxl spec: {importlib.util.find_spec('openpyxl')}")

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
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
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

def show_bulk_upload():
    st.header("📂 Bulk MOM Upload")
    st.markdown("Upload Minutes of Meeting (MOM) files to extract and create multiple tasks at once.")
    st.markdown("---")

    # ✅ DECLARE VARIABLES AT THE TOP with default values
    subject_col = owner_col = priority_col = due_date_col = remarks_col = cc_col = ""
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['xlsx', 'xls', 'csv', 'txt', 'pdf', 'docx'],
        help="Upload Excel, CSV, Text, PDF, or Word files containing task information"
    )

    if uploaded_file is None:
        st.info("👆 Upload a file to get started")

        st.markdown("---")
        st.subheader("📥 Download Sample Template")

        sample_data = {
            'Subject': ['Prepare Q1 Report', 'Review Contract', 'Update Documentation'],
            'Owner': ['Praveen', 'Rajesh', 'Amit'],
            'Priority': ['HIGH', 'MEDIUM', 'LOW'],
            'Due Date': ['2026-01-15', '2026-01-20', '2026-01-25'],
            'Remarks': ['Finance team needs this urgently', 'Legal review pending', 'Update user guide'],
            'CC': ['', 'praveen@example.com', '']
        }
        sample_df = pd.DataFrame(sample_data)

        st.download_button(
            label="📥 Download Excel Template",
            data=sample_df.to_csv(index=False).encode('utf-8'),
            file_name="task_upload_template.csv",
            mime="text/csv",
            use_container_width=True
        )
        return

    st.success(f"✅ File uploaded: {uploaded_file.name}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Name", uploaded_file.name)
    with col2:
        st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
    with col3:
        st.metric("File Type", uploaded_file.name.split('.')[-1].upper())

    st.markdown("---")
    st.subheader("⚙️ Processing Options")

    col1, col2 = st.columns(2)
    with col1:
        default_priority = st.selectbox("Default Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
    with col2:
        default_status = st.selectbox("Default Status", ["OPEN", "PENDING", "IN PROGRESS"], index=0)

    st.markdown("---")
    st.subheader("👁️ File Preview")

    df = None
    try:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            st.dataframe(df, width="stretch")
            st.info(f"📊 Found {len(df)} rows in the file")

        elif uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.dataframe(df, width="stretch")
            st.info(f"📊 Found {len(df)} rows in the file")

        elif uploaded_file.name.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
            st.text_area("File Content", content, height=300)
        else:
            st.info("📄 File uploaded successfully. Preview not available for this file type.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

    # Column mapping for Excel/CSV
    if df is not None:
        st.markdown("---")
        st.subheader("🔗 Column Mapping")
        st.markdown("Map your file columns to task fields:")

        cols = df.columns.tolist()
        c1, c2, c3 = st.columns(3)

        with c1:
            subject_col = st.selectbox("Subject Column", [""] + cols, key="subject_col")
            owner_col = st.selectbox("Owner Column", [""] + cols, key="owner_col")

        with c2:
            priority_col = st.selectbox("Priority Column", [""] + cols, key="priority_col")
            due_date_col = st.selectbox("Due Date Column", [""] + cols, key="due_date_col")

        with c3:
            remarks_col = st.selectbox("Remarks Column", [""] + cols, key="remarks_col")
            cc_col = st.selectbox("CC Column", [""] + cols, key="cc_col")

        # ✅ Debug section MOVED INSIDE the condition where variables are defined
        if debug_mode:  # Only show debug if debug_mode is True
            st.markdown("### ✅ Selected Mapping (Debug)")
            st.json({
                "subject_col": subject_col,
                "owner_col": owner_col,
                "priority_col": priority_col,
                "due_date_col": due_date_col,
                "remarks_col": remarks_col,
                "cc_col": cc_col
            })

        # ✅ Require mapping
        if not subject_col or not owner_col:
            st.error("Please select at least Subject Column and Owner Column before processing.")
            st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Process and Create Tasks", use_container_width=True, type="primary"):
            from datetime import datetime

            excel_handler = get_excel_handler()
            if not excel_handler:
                st.error("❌ Could not initialize ExcelHandler")
                return

            created_count = 0
            try:
                if df is not None:
                    for idx, row in df.iterrows():
                        task_data = {
                            "Owner": row.get(owner_col, "Unassigned") if owner_col else "Unassigned",
                            "Subject": row.get(subject_col, f"Task from {uploaded_file.name}") if subject_col else f"Task {idx+1}",
                            "Priority": row.get(priority_col, default_priority) if priority_col else default_priority,
                            "Status": default_status,
                            "Due Date": row.get(due_date_col, datetime.now().strftime("%Y-%m-%d")) if due_date_col else datetime.now().strftime("%Y-%m-%d"),
                            "Remarks": row.get(remarks_col, f"Imported from {uploaded_file.name}") if remarks_col else f"Imported from {uploaded_file.name}",
                            "CC": row.get(cc_col, "") if cc_col else ""
                        }
                        excel_handler.add_task(task_data)
                        created_count += 1

                st.success(f"✅ Successfully created {created_count} tasks from {uploaded_file.name}")
                st.balloons()

                st.info(
                    f"📊 Summary:\n"
                    f"- File: {uploaded_file.name}\n"
                    f"- Tasks Created: {created_count}\n"
                    f"- Priority: {default_priority}\n"
                    f"- Status: {default_status}"
                )

            except Exception as e:
                st.error(f"❌ Error processing file: {e}")
                st.exception(e)

def show_send_reminders():
    st.header("📧 Send Task Reminders")
    st.markdown("Send email reminders to task owners for pending tasks.")
    st.markdown("---")

    if st.button("📤 Send Reminders Now", type="primary", use_container_width=True):
        with st.spinner("Sending reminders..."):
            try:
                import subprocess
                result = subprocess.run(
                    ["python3", str(BASE_DIR / "run_reminders.py")],
                    capture_output=True,
                    text=True
                )
                st.text(result.stdout)
                if result.returncode == 0:
                    st.success("✅ Reminders sent successfully!")
                else:
                    st.error(f"❌ Error: {result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {e}")


def show_settings():
    try:
        settings_module = BASE_DIR / "views" / "settings_page.py"
        if settings_module.exists():
            from views.settings_page import render_settings
            render_settings()
        else:
            st.header("⚙️ Settings")
            st.warning("⚠️ Settings module not found. Please install settings_page.py in the views folder.")
            st.info("Download from the provided link and copy to: views/settings_page.py")
    except Exception as e:
        st.error(f"❌ Settings error: {e}")


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
