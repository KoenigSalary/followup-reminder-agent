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
    import streamlit as st
    from datetime import datetime
    from pathlib import Path

    st.header("📂 Bulk MOM Upload")
    st.markdown("Upload Minutes of Meeting (MOM) files to extract and create multiple tasks at once.")
    st.markdown("---")

    debug_mode = st.session_state.get("debug_mode", False)

    # ✅ Always define df first
    df = None

    # ✅ Ensure session keys exist
    for k in [
        "subject_col", "owner_col", "priority_col", "due_date_col",
        "remarks_col", "cc_col", "bulk_tasks"
    ]:
        st.session_state.setdefault(k, "" if k != "bulk_tasks" else [])

    # ---------- helpers ----------
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
            return pd.to_datetime(s, dayfirst=True, errors="raise").strftime("%Y-%m-%d")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d")

    def normalize_priority(v, fallback="MEDIUM"):
        s = clean(v).upper()
        if not s:
            return fallback
        aliases = {"MED": "MEDIUM", "MID": "MEDIUM", "URG": "URGENT", "NORMAL": "MEDIUM"}
        s = aliases.get(s, s)
        if s not in ["URGENT", "HIGH", "MEDIUM", "LOW"]:
            return fallback
        return s

    def parse_mom_lines_to_tasks(lines):
        """
        Converts MOM text lines into task rows.
        Supports patterns like:
          '* Are balances updated?@Sunil'
        Owner is extracted after '@' if present.
        """
        rows = []
        for line in lines:
            t = clean(line)
            if not t:
                continue
            t = t.lstrip("*•- ").strip()

            owner = ""
            remarks = t
            if "@" in t:
                left, right = t.rsplit("@", 1)
                remarks = left.strip()
                owner = right.strip()

            subject = (remarks.splitlines()[0] if remarks else "")[:80]
            if not remarks and not owner:
                continue

            rows.append({
                "meeting_id": "MOM-001",
                "Owner": owner or "Unassigned",
                "Subject": subject or "Task",
                "Due Date": datetime.now().strftime("%Y-%m-%d"),
                "Remarks": remarks,
                "Priority": "MEDIUM",
                "Status": "OPEN",
                "CC": ""
            })
        return rows

    # ---------- upload ----------
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["xlsx", "csv"],
        help="Upload Excel (.xlsx) or CSV containing task information",
        key="bulk_uploader"
    )

    if uploaded_file is None:
        st.info("👆 Upload a file to get started")
        st.markdown("---")
        st.subheader("📥 Download Sample Template")

        sample_df = pd.DataFrame({
            "Subject": ["MOM-001", "MOM-001", "MOM-001"],
            "Owner": ["Praveen", "Rajesh", "Amit"],
            "Priority": ["HIGH", "MEDIUM", "LOW"],
            "Due Date": ["16.01.2026", "20.01.2026", "30.01.2026"],
            "Remarks": ["Task detail 1", "Task detail 2", "Task detail 3"],
            "CC": ["", "someone@example.com", ""]
        })

        st.download_button(
            label="📥 Download CSV Template",
            data=sample_df.to_csv(index=False).encode("utf-8"),
            file_name="task_upload_template.csv",
            mime="text/csv",
            use_container_width=True,
            key="bulk_template_download"
        )
        return

    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # ---------- processing defaults ----------
    st.subheader("⚙️ Processing Options")
    c1, c2 = st.columns(2)
    with c1:
        default_status = st.selectbox(
            "Default Status (applies to all tasks)",
            ["OPEN", "PENDING", "IN PROGRESS"],
            index=0,
            key="bulk_default_status"
        )
    with c2:
        default_priority = st.selectbox(
            "Default Priority (used only if per-task priority not set)",
            ["URGENT", "HIGH", "MEDIUM", "LOW"],
            index=2,
            key="bulk_default_priority"
        )

    st.markdown("---")
    st.subheader("👁️ File Preview")

    # ---------- read file ----------
    try:
        if uploaded_file.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        elif uploaded_file.name.lower().endswith(".csv"):
            uploaded_file.seek(0)
            df_try = pd.read_csv(
                uploaded_file,
                sep=None,
                engine="python",
                encoding="utf-8",
                on_bad_lines="skip"
            )

            # Detect MOM text-style CSV (1 column and header is a long sentence)
            if df_try.shape[1] == 1 and len(df_try.columns) == 1 and len(str(df_try.columns[0])) > 30:
                colname = str(df_try.columns[0])
                lines = [colname] + df_try.iloc[:, 0].astype(str).tolist()
                tasks = parse_mom_lines_to_tasks(lines)
                df = pd.DataFrame(tasks)
                st.info("📄 Detected MOM text-style CSV (one task per line). Converted into tasks automatically.")
            else:
                df = df_try

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.exception(e)
        df = None

    # Guard
    if df is None:
        st.error("❌ Could not read the uploaded file into a table. Only Excel (.xlsx) and CSV are supported for Bulk MOM Upload.")
        st.stop()

    st.dataframe(df.head(30), use_container_width=True)
    st.caption(f"Rows: {len(df)}")

    if debug_mode:
        st.sidebar.markdown("### Debug: Bulk Upload")
        st.sidebar.write("df.shape:", df.shape)
        st.sidebar.write("df.columns:", df.columns.tolist())

    # ---------- If df already task-like (from MOM conversion) ----------
    looks_task_like = {"Owner", "Remarks", "Due Date"}.issubset(set(df.columns))

    # ---------- mapping (only for true tables) ----------
    if not looks_task_like:
        st.markdown("---")
        st.subheader("🔗 Column Mapping")
        st.markdown("Map your file columns to task fields:")

        cols = df.columns.tolist()
        a, b, c = st.columns(3)
        with a:
            st.selectbox("Meeting ID / MOM No. Column (optional)", [""] + cols, key="subject_col")
            st.selectbox("Owner Column", [""] + cols, key="owner_col")
        with b:
            st.selectbox("Due Date Column", [""] + cols, key="due_date_col")
            st.selectbox("Priority Column (optional)", [""] + cols, key="priority_col")
        with c:
            st.selectbox("Remarks Column (task details)", [""] + cols, key="remarks_col")
            st.selectbox("CC Column (optional)", [""] + cols, key="cc_col")

        if not st.session_state["owner_col"] or not st.session_state["remarks_col"] or not st.session_state["due_date_col"]:
            st.warning("Select at least Owner, Remarks, and Due Date columns to continue.")
            return

        # Build tasks list from mapped table
        df2 = df.dropna(how="all")
        tasks = []
        for idx, row in df2.iterrows():
            meeting_id_val = clean(row.get(st.session_state["subject_col"])) if st.session_state["subject_col"] else ""
            owner_val = clean(row.get(st.session_state["owner_col"]))
            remarks_val = clean(row.get(st.session_state["remarks_col"]))
            cc_val = clean(row.get(st.session_state["cc_col"])) if st.session_state["cc_col"] else ""
            due_val = parse_due_date(row.get(st.session_state["due_date_col"]))

            # skip truly empty
            if not owner_val and not remarks_val and not meeting_id_val:
                continue

            subject_text = (remarks_val.splitlines()[0] if remarks_val else f"Task {idx+1}")[:80]
            priority_raw = clean(row.get(st.session_state["priority_col"])) if st.session_state["priority_col"] else ""
            priority_final = normalize_priority(priority_raw, default_priority)

            tasks.append({
                "meeting_id": meeting_id_val,
                "Owner": owner_val or "Unassigned",
                "Subject": subject_text,
                "Due Date": due_val,
                "Remarks": remarks_val,
                "Priority": priority_final,
                "Status": default_status,
                "CC": cc_val
            })

        st.session_state["bulk_tasks"] = tasks

    else:
        # df already contains tasks (from MOM conversion)
        tasks = []
        df2 = df.dropna(how="all")
        for idx, row in df2.iterrows():
            owner_val = clean(row.get("Owner"))
            remarks_val = clean(row.get("Remarks"))
            due_val = parse_due_date(row.get("Due Date"))
            pr = normalize_priority(row.get("Priority"), default_priority)

            if not owner_val and not remarks_val:
                continue

            subject_text = clean(row.get("Subject")) or (remarks_val.splitlines()[0] if remarks_val else f"Task {idx+1}")[:80]
            tasks.append({
                "meeting_id": clean(row.get("meeting_id")) or clean(row.get("Subject")) or "MOM-001",
                "Owner": owner_val or "Unassigned",
                "Subject": subject_text,
                "Due Date": due_val,
                "Remarks": remarks_val,
                "Priority": pr,
                "Status": default_status,
                "CC": clean(row.get("CC"))
            })
        st.session_state["bulk_tasks"] = tasks

    # ---------- review / per-task priority ----------
    st.markdown("---")
    st.subheader("✅ Review Tasks (Priority per Task)")

    tasks_list = st.session_state.get("bulk_tasks", [])
    st.info(f"Tasks detected: {len(tasks_list)}")

    if not tasks_list:
        st.warning("No tasks detected from the uploaded MOM.")
        return

    priorities = ["URGENT", "HIGH", "MEDIUM", "LOW"]

    edited = []
    for i, t in enumerate(tasks_list):
        with st.container(border=True):
            st.write(f"**{i+1}. {t.get('Subject','')}**")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.caption(f"Owner: {t.get('Owner','')} | Due: {t.get('Due Date','')}")
            with c2:
                pr = st.selectbox(
                    "Priority",
                    priorities,
                    index=priorities.index(t.get("Priority","MEDIUM")) if t.get("Priority","MEDIUM") in priorities else 2,
                    key=f"priority_row_{i}"
                )
            with c3:
                st.caption(f"Status: {t.get('Status', default_status)}")

            t["Priority"] = pr
            t["Status"] = default_status
            edited.append(t)

    st.session_state["bulk_tasks"] = edited

    st.markdown("---")
    st.subheader("💾 Bulk Upload Actions")
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
        if st.button("🚀 Create Tasks Now", use_container_width=True, type="primary", key="bulk_create_tasks_btn"):

            # ✅ Your required snippet (first line after click)
            if df is None:
                st.error("❌ Could not read the uploaded file into a table. Only Excel (.xlsx) and CSV are supported for Bulk MOM Upload.")
                st.stop()

            excel_handler = get_excel_handler()
            if not excel_handler:
                st.error("❌ Could not initialize ExcelHandler")
                st.stop()

            created = 0
            errors = 0

            for i, t in enumerate(st.session_state.get("bulk_tasks", [])):
                try:
                    excel_handler.add_task(t)
                    created += 1
                except Exception as e:
                    errors += 1
                    st.error(f"Failed on task {i+1}: {e}")

            st.success(f"✅ Created {created} tasks. Errors: {errors}")
            if created > 0:
                st.balloons()

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
