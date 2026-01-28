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

def show_bulk_upload():
    import pandas as pd
    from pathlib import Path
    from datetime import datetime

    st.header("📂 Bulk MOM Upload")
    st.markdown("Upload Minutes of Meeting (MOM) files to extract and create multiple tasks at once.")
    st.markdown("---")

    # Debug mode (keeps code output hidden unless you enable it)
    debug_mode = st.session_state.get("debug_mode", False)

    # ✅ ALWAYS define df first
    df = None

    # ✅ Ensure mapping keys always exist
    for k in ["subject_col", "owner_col", "due_date_col", "remarks_col", "cc_col"]:
        st.session_state.setdefault(k, "")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["xlsx", "csv"],
        help="Upload Excel (.xlsx) or CSV containing task information"
    )

    if uploaded_file is None:
        st.info("👆 Upload a file to get started")
        st.markdown("---")
        st.subheader("📥 Download Sample Template")

        sample_df = pd.DataFrame({
            "Subject": ["MOM-001", "MOM-001", "MOM-001"],
            "Owner": ["Praveen", "Rajesh", "Amit"],
            "Due Date": ["16.01.2026", "20.01.2026", "30.01.2026"],
            "Remarks": ["Task detail 1", "Task detail 2", "Task detail 3"],
            "CC": ["", "someone@example.com", ""]
        })

        st.download_button(
            label="📥 Download CSV Template",
            data=sample_df.to_csv(index=False).encode("utf-8"),
            file_name="task_upload_template.csv",
            mime="text/csv",
            use_container_width=True
        )
        return

    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # ✅ One-time options (apply to ALL tasks)
    st.subheader("⚙️ Processing Options")
    c1, c2 = st.columns(2)
    with c1:
        priority_raw = clean(row.get(st.session_state["priority_col"])) if st.session_state["priority_col"] else ""
        priority_final = (priority_raw or default_priority).strip().upper()
    if priority_final not in ["URGENT", "HIGH", "MEDIUM", "LOW"]:
        priority_final = default_priority

        task_data["Priority"] = priority_final
    with c2:
        default_status = st.selectbox(
            "Default Status (applies to all tasks)",
            ["OPEN", "PENDING", "IN PROGRESS"],
            index=0,
            key="bulk_default_status"
        )

    st.markdown("---")
    st.subheader("👁️ File Preview")

    # -------- helpers --------
    def clean(v):
        if v is None:
            return ""
        if isinstance(v, float) and pd.isna(v):
            return ""
        return str(v).strip()

    def parse_due_date(v):
        s = clean(v)
        if not s:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            return pd.to_datetime(s, dayfirst=True).strftime("%Y-%m-%d")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d")

    def parse_mom_lines_to_df(lines: list[str]) -> pd.DataFrame:
        """
        If CSV is actually 'one task per line', convert it into a table with
        Remarks + Owner extracted from '@Name'.
        """
        rows = []
        for line in lines:
            t = clean(line)
            if not t:
                continue

            # remove bullets
            t = t.lstrip("*•- ").strip()

            owner = ""
            remarks = t

            # ✅ FIXED: this must be on one line
            if "@" in t:
                parts = t.rsplit("@", 1)
                remarks = parts[0].strip()
                owner = parts[1].strip()

            rows.append({
                "Subject": "MOM-001",
                "Owner": owner,
                "Due Date": datetime.now().strftime("%Y-%m-%d"),
                "Remarks": remarks,
                "CC": ""
            })

        return pd.DataFrame(rows)

    # -------- read file --------
    try:
        if uploaded_file.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        elif uploaded_file.name.lower().endswith(".csv"):
            uploaded_file.seek(0)

            # tolerant read first
            df_try = pd.read_csv(
                uploaded_file,
                sep=None,
                engine="python",
                encoding="utf-8",
                on_bad_lines="skip"
            )

            # If the CSV becomes 1 column with a long "sentence" header (like your screenshot),
            # treat it as MOM text lines instead of a real table.
            if df_try.shape[1] == 1 and len(df_try.columns) == 1 and len(str(df_try.columns[0])) > 30:
                # rebuild text lines: header + column values
                colname = str(df_try.columns[0])
                lines = [colname] + df_try.iloc[:, 0].astype(str).tolist()
                df = parse_mom_lines_to_df(lines)
                st.info("📄 Detected MOM text-style CSV (one task per line). Converted into table automatically.")
            else:
                df = df_try

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.exception(e)
        df = None

    # ✅ Guard
    if df is None:
        st.error("❌ Could not read the uploaded file into a table. Only Excel (.xlsx) and CSV are supported for Bulk MOM Upload.")
        st.stop()

    # Preview
    st.dataframe(df.head(50), use_container_width=True)
    st.caption(f"Rows: {len(df)}")

    # Debug in sidebar (not on main page)
    if debug_mode:
        st.sidebar.markdown("### Debug: Bulk Upload")
        st.sidebar.write("df.shape:", df.shape)
        st.sidebar.write("df.columns:", df.columns.tolist())

    # Column mapping
    st.markdown("---")
    st.subheader("🔗 Column Mapping")
    st.markdown("Map your file columns to task fields:")

    cols = df.columns.tolist()
    x1, x2, x3, x4 = st.columns(3)

    with x1:
        st.selectbox("Meeting ID / MOM No. Column", [""] + cols, key="subject_col")
        st.selectbox("Owner Column", [""] + cols, key="owner_col")

    with x2:
        st.selectbox("Due Date Column", [""] + cols, key="due_date_col")
        st.selectbox("CC Column", [""] + cols, key="cc_col")

    with x3:
        st.selectbox("Remarks Column (task details)", [""] + cols, key="remarks_col")

    with x4:
        st.selectbox("Priority Column (optional)", [""] + cols, key="priority_col")

    # Require mapping
    if (not st.session_state["owner_col"]
        or not st.session_state["remarks_col"]
        or not st.session_state["due_date_col"]):
        st.warning("Select at least Owner, Remarks, and Due Date columns to enable processing.")

    st.markdown("---")
    st.subheader("💾 Bulk Upload Actions")

    # Save upload file (optional)
    UPLOAD_DIR = Path("data") / "uploads"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    colA, colB = st.columns(2)
    with colA:
        if st.button("💾 Save Upload File", use_container_width=True, key="bulk_save_upload_btn"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = UPLOAD_DIR / f"{ts}_{uploaded_file.name}"
            uploaded_file.seek(0)
            save_path.write_bytes(uploaded_file.read())
            st.success(f"✅ Saved upload to: {save_path}")

    with colB:
        if st.button("🚀 Process and Create Tasks", use_container_width=True, type="primary", key="bulk_create_tasks_btn"):

            # ✅ Your required snippet (first line after click)
            if df is None:
                st.error("❌ Could not read the uploaded file into a table. Only Excel (.xlsx) and CSV are supported for Bulk MOM Upload.")
                st.stop()

            # Require mapping before creating tasks
            if (not st.session_state["owner_col"]
                or not st.session_state["remarks_col"]
                or not st.session_state["due_date_col"]):
                st.error("Please select Owner, Remarks, and Due Date columns before processing.")
                st.stop()

            df2 = df.dropna(how="all")
            created_count = 0

            excel_handler = get_excel_handler()
            if not excel_handler:
                st.error("❌ Could not initialize ExcelHandler")
                st.stop()

            for idx, row in df2.iterrows():
                meeting_id_val = clean(row.get(st.session_state["subject_col"])) if st.session_state["subject_col"] else ""
                owner_val = clean(row.get(st.session_state["owner_col"]))
                remarks_val = clean(row.get(st.session_state["remarks_col"]))
                cc_val = clean(row.get(st.session_state["cc_col"])) if st.session_state["cc_col"] else ""
                due_val = parse_due_date(row.get(st.session_state["due_date_col"]))

                # skip empty
                if not owner_val and not remarks_val and not meeting_id_val:
                    continue

                subject_text = (remarks_val.splitlines()[0] if remarks_val else f"Task {idx+1}")[:80]

                task_data = {
                    "meeting_id": meeting_id_val,
                    "Owner": owner_val or "Unassigned",
                    "Subject": subject_text,
                    "Priority": default_priority,   # ✅ one-time priority for ALL tasks
                    "Status": default_status,       # ✅ one-time status for ALL tasks
                    "Due Date": due_val,
                    "Remarks": remarks_val or f"Imported from {uploaded_file.name}",
                    "CC": cc_val
                }

                excel_handler.add_task(task_data)
                created_count += 1

            st.success(f"✅ Successfully created {created_count} tasks from {uploaded_file.name}")
            st.balloons()
            
    def parse_due_date(v):
        # empty
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return ""

        # already datetime/date
        if hasattr(v, "strftime"):
            return v.strftime("%Y-%m-%d")

        s = str(v).strip()
        if not s:
            return ""

        # excel serial date (if it comes as a number-like string)
        if s.isdigit():
            try:
                return pd.to_datetime(float(s), unit="D", origin="1899-12-30").strftime("%Y-%m-%d")
            except Exception:
                pass

        # dd.mm.yyyy / dd-mm-yyyy / dd/mm/yyyy
        try:
            return pd.to_datetime(s, dayfirst=True, errors="raise").strftime("%Y-%m-%d")
        except Exception:
            return ""

    # Process button
    st.markdown("---")
    p1, p2, p3 = st.columns([1, 2, 1])
    with p2:
        if st.button("🚀 Process and Create Tasks", use_container_width=True, type="primary"):
            excel_handler = get_excel_handler()
            if not excel_handler:
                st.error("❌ Could not initialize ExcelHandler")
                return

            created_count = 0
            try:
                df2 = df.dropna(how="all")  # skip fully blank rows

                for idx, row in df2.iterrows():
                    meeting_id_val = clean(row.get(st.session_state["subject_col"]))
                    owner_val = clean(row.get(st.session_state["owner_col"]))
                    remarks_val = clean(row.get(st.session_state["remarks_col"]))

                    priority_val = clean(row.get(st.session_state["priority_col"])) if st.session_state["priority_col"] else ""
                    cc_val = clean(row.get(st.session_state["cc_col"])) if st.session_state["cc_col"] else ""
                    due_raw = row.get(st.session_state["due_date_col"])
                    due_val = parse_due_date(due_raw)

                    # Skip empty-ish rows
                    if not meeting_id_val and not owner_val and not remarks_val:
                        continue

                    # ✅ Make real Subject from remarks (first line / 80 chars)
                    subject_text = (remarks_val.splitlines()[0] if remarks_val else f"Task {idx+1}")[:80]

                    task_data = {
                        "meeting_id": meeting_id_val,
                        "Owner": owner_val or "Unassigned",
                        "Subject": subject_text,
                        "Priority": priority_val or default_priority,
                        "Status": default_status,
                        "Due Date": due_val or datetime.now().strftime("%Y-%m-%d"),
                        "Remarks": remarks_val or f"Imported from {uploaded_file.name}",
                        "CC": cc_val
                    }

                    excel_handler.add_task(task_data)
                    created_count += 1

                st.success(f"✅ Successfully created {created_count} tasks from {uploaded_file.name}")
                st.balloons()

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
                from run_reminders import send_reminders
                result_msg = send_reminders()
                st.success(f"✅ {result_msg}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)

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
