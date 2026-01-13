import streamlit as st
from datetime import datetime

def render_manual_entry(excel_handler):
    st.subheader("✍️ Manual Entry")

    with st.form("manual_entry_form"):
        # ✅ NEW: Added Subject field
        subject = st.text_input("📌 Subject / Task Title", placeholder="e.g., Review Q4 Financial Report")
        
        owner = st.text_input("👤 Owner (Name)", placeholder="e.g., Praveen, Sunil, Sarika")
        
        # ✅ IMPROVED: Use text_area for description
        task_description = st.text_area(
            "📝 Task Description (Details)", 
            placeholder="Detailed description of the task...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            priority = st.selectbox("🎯 Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
        
        with col2:
            deadline_date = st.date_input("📅 Deadline")
        
        cc = st.text_input("📧 CC (comma-separated)", value=st.session_state.get("global_cc", ""))
        
        submitted = st.form_submit_button("💾 Save Task", type="primary")

        if submitted:
            # Validation
            if not owner:
                st.warning("⚠️ Please enter Owner name")
                return
            
            if not subject:
                st.warning("⚠️ Please enter Task Subject/Title")
                return

            # ✅ Generate unique task_id
            today = datetime.now()
            task_id_prefix = f"MAN-{today.strftime('%Y%m%d')}"
            
            # Load existing tasks to get next sequence number
            df = excel_handler.load_data()
            
            # Find existing manual tasks for today
            if len(df) > 0 and 'task_id' in df.columns:
                today_manual_tasks = df[
                    df['task_id'].astype(str).str.startswith(task_id_prefix, na=False)
                ]
                next_seq = len(today_manual_tasks) + 1
            else:
                next_seq = 1
            
            task_id = f"{task_id_prefix}-{next_seq:03d}"
            
            # ✅ Generate meeting_id for manual tasks
            meeting_id = f"MANUAL-{today.strftime('%Y%m%d')}"

            try:
                # ✅ Create task with ALL required fields
                new_task = {
                    "task_id": task_id,
                    "meeting_id": meeting_id,
                    "Owner": owner,
                    "Subject": subject,
                    "Status": "OPEN",
                    "Priority": priority,
                    "Due Date": deadline_date,
                    "CC": cc,
                    "Remarks": task_description if task_description else f"Priority: {priority}",
                    "Created On": datetime.now(),
                    "Last Updated": datetime.now(),
                    "Last Reminder Date": None,
                    "Last Reminder On": None,
                    "Completed Date": None,
                    "Auto Reply Sent": None
                }
                
                # Append to Excel
                total = excel_handler.append_rows([new_task])
                
                st.success(f"✅ Task created successfully!")
                st.info(f"📋 **Task ID:** {task_id}")
                st.info(f"👤 **Owner:** {owner}")
                st.info(f"🎯 **Priority:** {priority}")
                st.info(f"📅 **Deadline:** {deadline_date}")
                
                # Show total tasks
                st.metric("Total Tasks in System", total)
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error creating task: {e}")
                
                # Show debug info
                with st.expander("🔍 Debug Information"):
                    st.write("**Error Details:**", str(e))
                    st.write("**Task Data:**", new_task)
                    st.write("**Excel Columns:**", list(excel_handler.load_data().columns))
