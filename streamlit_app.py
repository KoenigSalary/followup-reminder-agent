#!/usr/bin/env python3
"""
Streamlit App - Follow-up & Reminder Team
"""

import os
import sys
import importlib
import inspect
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path(os.getcwd())
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


# --- session ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None


def show_login():
    st.title("Follow-up & Reminder Team")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Enter username and password.")


def show_sidebar():
    with st.sidebar:
        st.markdown(f"**User:** {st.session_state.username}")
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📥 View Follow-ups", "✍️ Manual Entry", "📂 Bulk MOM Upload", "📧 Send Task Reminders"],
            label_visibility="collapsed"
        )
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    return page


def show_dashboard():
    st.header("📊 Dashboard")
    excel = get_excel_handler()
    if not excel:
        return
    df = excel.load_data()
    st.metric("Total Tasks", len(df))


def show_view_followups():
    st.header("📥 View Follow-ups")
    excel = get_excel_handler()
    if not excel:
        return
    df = excel.load_data()
    st.dataframe(df, width="stretch")


def show_manual_entry():
    st.header("✍️ Manual Entry")
    excel = get_excel_handler()
    if not excel:
        return

    subject = st.text_input("Subject")
    owner = st.text_input("Owner")
    due_date = st.text_input("Due Date (YYYY-MM-DD)")
    remarks = st.text_area("Remarks")
    priority = st.selectbox("Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
    cc = st.text_input("CC")

    if st.button("Add Task", type="primary"):
        excel.add_entry(subject=subject, owner=owner, due_date=due_date, remarks=remarks, priority=priority, cc=cc)
        st.success("✅ Task added")


def show_bulk_upload():
    st.header("📂 Bulk MOM Upload")
    st.markdown("---")

    for k in ["subject_col", "owner_col", "priority_col", "due_date_col", "remarks_col", "cc_col"]:
        st.session_state.setdefault(k, "")

    uploaded_file = st.file_uploader("Upload file", type=["xlsx", "csv"])
    if uploaded_file is None:
        st.info("Upload an XLSX or CSV.")
        return

    default_priority = st.selectbox("Default Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
    default_status = st.selectbox("Default Status", ["OPEN", "PENDING", "IN PROGRESS"], index=0)

    df = pd.read_excel(uploaded_file, engine="openpyxl") if uploaded_file.name.lower().endswith(".xlsx") else pd.read_csv(uploaded_file)
    st.dataframe(df, width="stretch")

    cols = df.columns.tolist()
    st.selectbox("Meeting ID / MOM No. Column", [""] + cols, key="subject_col")
    st.selectbox("Owner Column", [""] + cols, key="owner_col")
    st.selectbox("Priority Column", [""] + cols, key="priority_col")
    st.selectbox("Due Date Column", [""] + cols, key="due_date_col")
    st.selectbox("Remarks Column", [""] + cols, key="remarks_col")
    st.selectbox("CC Column", [""] + cols, key="cc_col")

    if (not st.session_state["subject_col"]
        or not st.session_state["owner_col"]
        or not st.session_state["remarks_col"]
        or not st.session_state["due_date_col"]):
        st.error("Select MOM No., Owner, Remarks, Due Date.")
        st.stop()

    def clean(v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
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
        try:
            return pd.to_datetime(s, dayfirst=True).strftime("%Y-%m-%d")
        except Exception:
            return ""

    if st.button("Process & Create Tasks", type="primary"):
        excel = get_excel_handler()
        if not excel:
            return

        created = 0
        df2 = df.dropna(how="all")

        for idx, row in df2.iterrows():
            meeting_id = clean(row.get(st.session_state["subject_col"]))
            owner = clean(row.get(st.session_state["owner_col"]))
            remarks = clean(row.get(st.session_state["remarks_col"]))
            due = parse_due_date(row.get(st.session_state["due_date_col"]))
            priority = clean(row.get(st.session_state["priority_col"])).upper() if st.session_state["priority_col"] else ""
            cc = clean(row.get(st.session_state["cc_col"])) if st.session_state["cc_col"] else ""

            if not meeting_id and not owner and not remarks:
                continue

            subject = (remarks.splitlines()[0] if remarks else f"Task {idx+1}")[:80]

            excel.add_task({
                "meeting_id": meeting_id,
                "Owner": owner or "Unassigned",
                "Subject": subject,
                "Priority": priority or default_priority,
                "Status": default_status,
                "Due Date": due or datetime.now().strftime("%Y-%m-%d"),
                "Remarks": remarks,
                "CC": cc,
            })
            created += 1

        st.success(f"✅ Created {created} tasks")


def show_send_reminders():
    st.header("📧 Send Task Reminders")
    st.markdown("---")

    if st.button("Send Reminders Now", type="primary"):
        with st.spinner("Sending reminders..."):
            try:
                from run_reminders import send_reminders
                msg = send_reminders()
                st.success(msg)
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)


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


if __name__ == "__main__":
    main()
