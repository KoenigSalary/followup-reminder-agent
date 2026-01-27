#!/usr/bin/env python3
"""
Streamlit App - Follow-up & Reminder Team
FINAL VERSION
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import importlib
import inspect
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from utils.excel_handler import ExcelHandler

REGISTRY_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"


def ensure_registry_exists():
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        df = pd.DataFrame(columns=[
            "task_id", "meeting_id", "Subject", "Owner", "CC", "Due Date",
            "Remarks", "Priority", "Status", "Created On", "Last Updated",
            "Last Reminder Date", "Last Reminder On", "Completed Date", "Auto Reply Sent"
        ])
        df.to_excel(REGISTRY_FILE, index=False)


def get_excel_handler():
    try:
        ensure_registry_exists()
        return ExcelHandler(str(REGISTRY_FILE))
    except Exception as e:
        st.error(f"❌ Error initializing ExcelHandler: {e}")
        st.exception(e)
        return None


st.set_page_config(
    page_title="Follow-up & Reminder Team | Koenig Solutions",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    debug_mode = st.toggle("🛠 Debug mode", value=False)

if debug_mode:
    st.sidebar.info(f"ExcelHandler loaded from: {inspect.getfile(ExcelHandler)}")
    st.sidebar.info(f"openpyxl spec: {importlib.util.find_spec('openpyxl')}")


# -------------------------
# Session init
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None


# -------------------------
# Your existing UI functions:
# show_login(), show_sidebar(), show_dashboard(), show_view_followups(), show_manual_entry()
# Keep them exactly as you have.
# -------------------------

def show_bulk_upload():
    st.header("📂 Bulk MOM Upload")
    st.markdown("Upload Minutes of Meeting (MOM) files to extract and create multiple tasks at once.")
    st.markdown("---")

    for k in ["subject_col", "owner_col", "priority_col", "due_date_col", "remarks_col", "cc_col"]:
        st.session_state.setdefault(k, "")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["xlsx", "xls", "csv", "txt", "pdf", "docx"],
        help="Upload Excel, CSV, Text, PDF, or Word files containing task information"
    )

    if uploaded_file is None:
        st.info("👆 Upload a file to get started")
        return

    st.success(f"✅ File uploaded: {uploaded_file.name}")

    st.subheader("⚙️ Processing Options")
    c1, c2 = st.columns(2)
    with c1:
        default_priority = st.selectbox("Default Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
    with c2:
        default_status = st.selectbox("Default Status", ["OPEN", "PENDING", "IN PROGRESS"], index=0)

    st.markdown("---")
    st.subheader("👁️ File Preview")

    df = None
    try:
        if uploaded_file.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            st.info("📄 Preview not available for this file type.")
            return

        st.dataframe(df, width="stretch")
        st.info(f"📊 Found {len(df)} rows in the file")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return

    st.markdown("---")
    st.subheader("🔗 Column Mapping")

    cols = df.columns.tolist()
    x1, x2, x3 = st.columns(3)

    with x1:
        st.selectbox("Meeting ID / MOM No. Column", [""] + cols, key="subject_col")
        st.selectbox("Owner Column", [""] + cols, key="owner_col")

    with x2:
        st.selectbox("Priority Column", [""] + cols, key="priority_col")
        st.selectbox("Due Date Column", [""] + cols, key="due_date_col")

    with x3:
        st.selectbox("Remarks Column (task details)", [""] + cols, key="remarks_col")
        st.selectbox("CC Column", [""] + cols, key="cc_col")

    if debug_mode:
        st.markdown("### ✅ Selected Mapping (Debug)")
        st.json({k: st.session_state[k] for k in ["subject_col","owner_col","priority_col","due_date_col","remarks_col","cc_col"]})

    if (not st.session_state["subject_col"]
        or not st.session_state["owner_col"]
        or not st.session_state["remarks_col"]
        or not st.session_state["due_date_col"]):
        st.error("Please select: MOM No., Owner, Remarks, and Due Date columns.")
        st.stop()

    def clean(v):
        if v is None:
            return ""
        if isinstance(v, float) and pd.isna(v):
            return ""
        return str(v).strip()

    def parse_due_date(v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return ""
        if hasattr(v, "strftime"):
            return v.strftime("%Y-%m-%d")
        s = str(v).strip()
        if not s:
            return ""
        if s.isdigit():
            try:
                return pd.to_datetime(float(s), unit="D", origin="1899-12-30").strftime("%Y-%m-%d")
            except Exception:
                pass
        try:
            return pd.to_datetime(s, dayfirst=True, errors="raise").strftime("%Y-%m-%d")
        except Exception:
            return ""

    st.markdown("---")
    if st.button("🚀 Process and Create Tasks", use_container_width=True, type="primary"):
        excel_handler = get_excel_handler()
        if not excel_handler:
            return

        created_count = 0
        df2 = df.dropna(how="all")

        for idx, row in df2.iterrows():
            meeting_id_val = clean(row.get(st.session_state["subject_col"]))
            owner_val = clean(row.get(st.session_state["owner_col"]))
            remarks_val = clean(row.get(st.session_state["remarks_col"]))
            priority_val = clean(row.get(st.session_state["priority_col"])) if st.session_state["priority_col"] else ""
            cc_val = clean(row.get(st.session_state["cc_col"])) if st.session_state["cc_col"] else ""
            due_val = parse_due_date(row.get(st.session_state["due_date_col"]))

            if not meeting_id_val and not owner_val and not remarks_val:
                continue

            subject_text = (remarks_val.splitlines()[0] if remarks_val else f"Task {idx+1}")[:80]

            task_data = {
                "meeting_id": meeting_id_val,
                "Owner": owner_val or "Unassigned",
                "Subject": subject_text,
                "Priority": (priority_val.upper() if priority_val else default_priority),
                "Status": default_status,
                "Due Date": due_val or datetime.now().strftime("%Y-%m-%d"),
                "Remarks": remarks_val or f"Imported from {uploaded_file.name}",
                "CC": cc_val
            }

            excel_handler.add_task(task_data)
            created_count += 1

        st.success(f"✅ Successfully created {created_count} tasks from {uploaded_file.name}")
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


def main():
    # Keep your login/sidebar routing exactly like before
    if not st.session_state.logged_in:
        # call your show_login()
        st.write("Login page here (keep your existing show_login())")
        return

    # call your show_sidebar() and route pages
    st.write("App routing here (keep your existing show_sidebar())")


if __name__ == "__main__":
    main()
