# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from datetime import datetime, date

from utils.task_normalizer import normalize_df
from priority_manager import get_priority_emoji


def render_view_followups(excel_handler, user_manager):
    st.subheader("📥 View Follow-ups")

    # ✅ LOAD DATA
    df_raw = excel_handler.load_data()

    if df_raw is None or df_raw.empty:
        st.info("No tasks available.")
        return

    # ✅ CRITICAL FIX: Remove duplicate columns FIRST
    df_raw = df_raw.loc[:, ~df_raw.columns.duplicated(keep='first')]
    
    # ✅ Normalize column names to lowercase for consistency
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    
    # ✅ Map common column variations
    column_map = {
        'task_text': 'subject',
        'task': 'subject',
        'due date': 'due_date',
        'deadline': 'due_date',
        'last reminder date': 'last_reminder_date'
    }
    
    df_raw = df_raw.rename(columns=column_map)
    
    # ✅ Ensure required columns exist
    required_cols = ['subject', 'owner', 'status', 'priority', 'due_date', 'remarks', 'cc']
    for col in required_cols:
        if col not in df_raw.columns:
            df_raw[col] = '' if col in ['subject', 'owner', 'remarks', 'cc'] else 'OPEN' if col == 'status' else 'MEDIUM' if col == 'priority' else None
    
    # ✅ Normalize status values
    df_raw['status'] = df_raw['status'].fillna('OPEN').astype(str).str.strip().str.upper()
    
    # ✅ Filter out deleted tasks
    df = df_raw[df_raw['status'] != 'DELETED'].copy()
    
    if df.empty:
        st.info("No active tasks available.")
        return

    # ✅ Convert due_date to date objects
    df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce').dt.date
    
    today = date.today()

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------
    st.markdown("### 🔍 Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        owners = sorted([str(o) for o in df['owner'].dropna().unique() if str(o).strip() and str(o) != 'nan'])
        owner_filter = st.selectbox("Owner", ["ALL"] + owners)

    with col2:
        status_filter = st.selectbox("Status", ["ALL", "OPEN", "DONE"])

    with col3:
        priority_filter = st.selectbox("Priority", ["ALL", "URGENT", "HIGH", "MEDIUM", "LOW"])

    with col4:
        due_filter = st.selectbox("Due", ["ALL", "Overdue", "Today", "Upcoming"])

    # --------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------
    filtered_df = df.copy()

    if owner_filter != "ALL":
        filtered_df = filtered_df[filtered_df["owner"].astype(str).str.strip() == owner_filter]

    if status_filter != "ALL":
        filtered_df = filtered_df[filtered_df["status"].astype(str).str.upper() == status_filter]

    if priority_filter != "ALL":
        filtered_df = filtered_df[filtered_df["priority"].astype(str).str.upper() == priority_filter]

    if due_filter == "Overdue":
        filtered_df = filtered_df[filtered_df["due_date"] < today]
    elif due_filter == "Today":
        filtered_df = filtered_df[filtered_df["due_date"] == today]
    elif due_filter == "Upcoming":
        filtered_df = filtered_df[filtered_df["due_date"] > today]

    # --------------------------------------------------
    # RENDER TASKS
    # --------------------------------------------------
    st.markdown(f"### 📋 Tasks ({len(filtered_df)})")

    if filtered_df.empty:
        st.info("No tasks match the selected filters.")
        return

    # ✅ CRITICAL: Iterate using iterrows() and extract SCALAR values
    for idx, row in filtered_df.iterrows():
        
        # ✅ Extract scalar values properly (NOT Series objects)
        subject = str(row["subject"]) if pd.notna(row["subject"]) else "No subject"
        owner = str(row["owner"]) if pd.notna(row["owner"]) else "Unknown"
        priority = str(row["priority"]).upper() if pd.notna(row["priority"]) else "MEDIUM"
        status = str(row["status"]).upper() if pd.notna(row["status"]) else "OPEN"
        due_date = row["due_date"]
        remarks = str(row["remarks"]) if pd.notna(row["remarks"]) else ""
        
        # Clean up values
        subject = subject.strip()
        owner = owner.strip()
        priority = priority.strip()
        status = status.strip()
        remarks = remarks.strip()

        priority_emoji = get_priority_emoji(priority)

        # ---------- TASK CARD ----------
        st.markdown(
            f"""
**📝 {subject}**  
👤 Owner: **{owner}**  
🎯 Priority: {priority_emoji} {priority}  
📅 Due Date: {due_date if pd.notna(due_date) else "N/A"}  
🏷 Status: **{status}**  
📝 Remarks: {remarks if remarks else "None"}
"""
        )

        # ---------- STATUS TOGGLE ----------
        col_status1, col_status2 = st.columns(2)
        
        with col_status1:
            if status == "OPEN":
                if st.button("✅ Mark Completed", key=f"complete_{idx}"):
                    # ✅ Update using ExcelHandler with Title Case columns
                    excel_handler.update_row(idx, {
                        "Status": "DONE",
                        "Completed Date": str(today),
                        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("✅ Task marked as completed!")
                    st.rerun()

        with col_status2:
            if status == "DONE":
                if st.button("🔁 Re-open", key=f"reopen_{idx}"):
                    excel_handler.update_row(idx, {
                        "Status": "OPEN",
                        "Completed Date": "",
                        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("🔁 Task re-opened!")
                    st.rerun()

        # ---------- EDIT / DELETE ----------
        with st.expander("✏️ Edit / Delete Task"):

            # Owner dropdown
            new_owner = st.selectbox(
                "Owner",
                owners,
                index=owners.index(owner) if owner in owners else 0,
                key=f"owner_{idx}",
            )

            # Due Date
            if pd.isna(due_date):
                safe_due = today
            else:
                safe_due = due_date

            new_due_date = st.date_input(
                "Due Date",
                value=safe_due,
                key=f"due_{idx}",
            )

            # Priority
            priorities = ["URGENT", "HIGH", "MEDIUM", "LOW"]
            new_priority = st.selectbox(
                "Priority",
                priorities,
                index=priorities.index(priority) if priority in priorities else 2,
                key=f"prio_{idx}",
            )

            # Remarks
            new_remarks = st.text_area(
                "Remarks",
                value=remarks,
                key=f"remarks_{idx}",
            )

            # Save Changes
            col_edit1, col_edit2 = st.columns(2)
            
            with col_edit1:
                if st.button("💾 Save Changes", key=f"save_{idx}", type="primary"):
                    excel_handler.update_row(idx, {
                        "Owner": new_owner,
                        "Due Date": str(new_due_date),
                        "Priority": new_priority,
                        "Remarks": new_remarks,
                        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("💾 Changes saved!")
                    st.rerun()

            # ✅ DELETE BUTTON - FIXED
            with col_edit2:
                if st.button("🗑️ Delete Task", key=f"delete_{idx}", type="secondary"):
                    # ✅ CRITICAL FIX: Use Title Case "Status" to match Excel schema
                    try:
                        excel_handler.update_row(idx, {
                            "Status": "DELETED",
                            "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.warning("🗑️ Task deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting task: {e}")
                        st.write(f"Debug - Row index: {idx}")
                        st.write(f"Debug - Available columns: {list(excel_handler.load_data().columns)}")

        # ---------- DUE STATUS INDICATOR ----------
        if isinstance(due_date, date):
            days = (due_date - today).days
            if days < 0:
                st.error(f"⚠️ Overdue by {abs(days)} day(s)")
            elif days == 0:
                st.warning("⏳ Due TODAY")
            else:
                st.success(f"✅ Due in {days} day(s)")

        st.divider()
