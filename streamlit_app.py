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
from manual_processor import ManualProcessor

# =========================================================
# PAGE CONFIG (must be first Streamlit call)
# =========================================================
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
)

# =========================================================
# SIDEBAR BRANDING
# =========================================================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=220)
    st.markdown("### Follow-up & Reminder Agent")
    st.markdown("---")

# =========================================================
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
    manual_processor = ManualProcessor(EXCEL_FILE_PATH)
    return excel_handler, email_processor, reminder_scheduler, manual_processor

excel_handler, email_processor, reminder_scheduler, manual_processor = initialize_handlers()

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
st.sidebar.header("Navigation")

menu = st.sidebar.radio(
    "Select Action",
    [
        "📥 View Follow-ups",
        "📧 Process Emails",
        "⏰ Run Reminder Scheduler",
        "✍️ Manual Entry",
        "⚙️ Run Engines",
        "📊 Logs / Status"
    ]
)

# =========================================================
# 1. VIEW FOLLOW-UPS
# =========================================================
if menu == "📥 View Follow-ups":
    st.subheader("Follow-ups")

    df = excel_handler.load_data()

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
        subject = st.text_input("Subject")
        owner = st.text_input("Owner (Name)")
        due_date = st.date_input("Due Date")
        remarks = st.text_area("Remarks")

        submitted = st.form_submit_button("Save")

        if submitted:
            manual_processor.add_entry(
                subject=subject,
                owner=owner,
                due_date=due_date,
                remarks=remarks
            )
            st.success("Manual follow-up added successfully.")

# =========================================================
# 5. LOGS / STATUS
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

