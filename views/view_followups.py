import streamlit as st
import pandas as pd
from datetime import datetime

from utils.task_normalizer import normalize_df
from utils.safe_keys import unique_key
from reminder_scheduler import get_next_reminder_date
from priority_manager import get_priority_emoji


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
