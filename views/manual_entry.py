import streamlit as st
from datetime import datetime

def render_manual_entry(excel_handler):
    st.subheader("✍️ Manual Entry")

    with st.form("manual_entry_form"):
        owner = st.text_input("Owner (Name)")
        task_text = st.text_area("Task Description")
        cc = st.text_input("CC", value=st.session_state.get("global_cc", ""))
        priority = st.selectbox("Priority", ["URGENT", "HIGH", "MEDIUM", "LOW"], index=2)
        deadline_date = st.date_input("Deadline")

        submitted = st.form_submit_button("Save")

        if submitted:
            if not owner or not task_text:
                st.warning("⚠️ Please fill in Owner and Task Description")
                return

            try:
                total = excel_handler.add_entry(
                    subject=task_text,
                    owner=owner,
                    due_date=deadline_date,
                    remarks=f"Priority: {priority}",
                    cc=cc,
                )
                st.success(f"✅ Task added! Total tasks: {total}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ add_entry failed: {e}")
                st.info("Trying fallback append...")

                total = excel_handler.append_rows([{
                    "Subject": task_text,
                    "Owner": owner,
                    "CC": cc,
                    "Due Date": deadline_date,
                    "Remarks": f"Priority: {priority}",
                    "Status": "OPEN",
                    "Created On": datetime.now(),
                    "Last Updated": datetime.now()
                }])
                st.success(f"✅ Task added via fallback! Total: {total}")
                st.rerun()
