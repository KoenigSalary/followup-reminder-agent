"""
Fixed Bulk Upload with correct ExcelHandler method
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta
import re

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.excel_handler import ExcelHandler

def show_bulk_upload():
    """Display the bulk upload page"""
    
    st.markdown("### 📤 Bulk MOM Upload")
    st.markdown("---")
    
    # Instructions
    with st.expander("📖 How to upload tasks"):
        st.markdown("""
        **Supported Formats:**
        
        1. **Excel (.xlsx)** - Recommended
        2. **CSV (.csv)**
        3. **DOCX (.docx)** - With @mention format
        
        **Required Columns:**
        - Subject (Task description)
        - Owner (Assigned person)
        
        **Optional Columns:**
        - Priority (URGENT/HIGH/MEDIUM/LOW)
        - Due Date (DD-MM-YYYY or DD-MMM-YYYY)
        - Status (OPEN/IN PROGRESS/COMPLETED)
        - Remarks (Additional notes)
        - CC (CC recipients)
        """)
    
    # Upload section
    uploaded_file = st.file_uploader(
        "Upload File",
        type=['xlsx', 'csv', 'docx'],
        help="Upload Excel, CSV, or DOCX file with task information"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Display file info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Name", uploaded_file.name)
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        with col2:
            file_type = uploaded_file.name.split('.')[-1].upper()
            st.metric("File Type", file_type)
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        col1, col2 = st.columns(2)
        with col1:
            default_priority = st.selectbox(
                "Default Priority",
                ["URGENT", "HIGH", "MEDIUM", "LOW"],
                index=2
            )
        with col2:
            default_status = st.selectbox(
                "Default Status",
                ["OPEN", "IN PROGRESS", "COMPLETED"],
                index=0
            )
        
        # Add default due date option
        use_default_due = st.checkbox("Set default due date for tasks without dates", value=True)
        default_due_days = 7
        if use_default_due:
            default_due_days = st.number_input("Days from today", min_value=1, max_value=365, value=7)
        
        # Parse file
        tasks_to_create = []
        
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                st.warning("DOCX parsing requires python-docx. Please use Excel or CSV format.")
                return
            
            # Show preview
            st.markdown("### 👁️ File Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Column mapping
            st.markdown("### 🔗 Column Mapping")
            st.write("Map your file columns to task fields:")
            
            columns = [''] + list(df.columns)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                subject_col = st.selectbox("Subject Column", columns, index=columns.index('Subject') if 'Subject' in columns else 0)
                owner_col = st.selectbox("Owner Column", columns, index=columns.index('Owner') if 'Owner' in columns else 0)
            with col2:
                priority_col = st.selectbox("Priority Column", columns, index=columns.index('Priority') if 'Priority' in columns else 0)
                due_date_col = st.selectbox("Due Date Column", columns, index=columns.index('Due Date') if 'Due Date' in columns else 0)
            with col3:
                remarks_col = st.selectbox("Remarks Column", columns, index=columns.index('Remarks') if 'Remarks' in columns else 0)
                cc_col = st.selectbox("CC Column", columns, index=columns.index('CC') if 'CC' in columns else 0)
            
            # Validate required fields
            if not subject_col or not owner_col:
                st.warning("⚠️ Please select at least Subject and Owner columns")
                return
            
            # Convert to task list
            for idx, row in df.iterrows():
                task = {
                    'Subject': str(row[subject_col]) if subject_col and pd.notna(row.get(subject_col)) else '',
                    'Owner': str(row[owner_col]) if owner_col and pd.notna(row.get(owner_col)) else '',
                    'Priority': str(row[priority_col]) if priority_col and pd.notna(row.get(priority_col)) else default_priority,
                    'Status': default_status,
                    'Due Date': str(row[due_date_col]) if due_date_col and pd.notna(row.get(due_date_col)) else '',
                    'Remarks': str(row[remarks_col]) if remarks_col and pd.notna(row.get(remarks_col)) else '',
                    'CC': str(row[cc_col]) if cc_col and pd.notna(row.get(cc_col)) else ''
                }
                
                # Apply default due date
                if not task['Due Date'] and use_default_due:
                    due_date = datetime.now() + timedelta(days=default_due_days)
                    task['Due Date'] = due_date.strftime('%d-%b-%Y')
                
                # Validate task
                if task['Subject'] and task['Owner']:
                    tasks_to_create.append(task)
            
            # Show preview of mapped tasks
            if tasks_to_create:
                st.markdown(f"### ✅ Found {len(tasks_to_create)} valid tasks")
                preview_df = pd.DataFrame(tasks_to_create)
                st.dataframe(preview_df, use_container_width=True)
            else:
                st.warning("No valid tasks found. Please check your column mapping.")
                return
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return
        
        # Process button
        if tasks_to_create and st.button("🔄 Process and Create Tasks", type="primary"):
            with st.spinner("Creating tasks..."):
                try:
                    # Initialize ExcelHandler
                    registry_path = BASE_DIR / "data" / "tasks_registry.xlsx"
                    excel_handler = ExcelHandler(str(registry_path))
                    
                    # Read existing data
                    df_registry = excel_handler.read_data()
                    
                    created_count = 0
                    created_tasks = []
                    
                    for task_data in tasks_to_create:
                        try:
                            # Generate Task ID
                            today = datetime.now()
                            date_str = today.strftime('%Y%m%d')
                            
                            # Find next available number for today
                            existing_ids = df_registry[df_registry['Task ID'].str.contains(date_str, na=False)]['Task ID'].tolist()
                            next_num = len(existing_ids) + 1
                            task_id = f"MAN-{date_str}-{next_num:03d}"
                            
                            # Create new task row
                            new_task = {
                                'Task ID': task_id,
                                'Subject': task_data['Subject'],
                                'Owner': task_data['Owner'],
                                'Priority': task_data.get('Priority', default_priority),
                                'Status': task_data.get('Status', default_status),
                                'Due Date': task_data.get('Due Date', ''),
                                'Created Date': today.strftime('%d-%b-%Y'),
                                'Last Reminder Date': '',
                                'Remarks': task_data.get('Remarks', ''),
                                'CC': task_data.get('CC', '')
                            }
                            
                            # Append to dataframe
                            df_registry = pd.concat([df_registry, pd.DataFrame([new_task])], ignore_index=True)
                            created_tasks.append(new_task)
                            created_count += 1
                            
                        except Exception as e:
                            st.warning(f"⚠️ Skipped task: {task_data.get('Subject', 'Unknown')} - Error: {str(e)}")
                    
                    # Save updated registry
                    if created_count > 0:
                        excel_handler.write_data(df_registry)
                        
                        st.success(f"✅ Successfully created {created_count} tasks from {uploaded_file.name}")
                        
                        # Show summary
                        st.markdown("### 📊 Summary:")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tasks Created", created_count)
                        with col2:
                            st.metric("Default Priority", default_priority)
                        with col3:
                            st.metric("Default Status", default_status)
                        
                        # Show created tasks
                        st.markdown("### ✅ Created Tasks:")
                        created_df = pd.DataFrame(created_tasks)
                        st.dataframe(created_df, use_container_width=True)
                        
                        st.info("💡 Tip: Go to 'Dashboard' or 'View Follow-ups' to see all created tasks")
                        
                        # Offer to send reminders
                        if st.button("📧 Send Reminders Now"):
                            st.info("Running reminder script...")
                            import subprocess
                            result = subprocess.run(
                                ['python3', str(BASE_DIR / 'run_reminders.py')],
                                capture_output=True,
                                text=True
                            )
                            st.code(result.stdout)
                            if result.stderr:
                                st.error(result.stderr)
                    else:
                        st.warning("No tasks were created.")
                
                except Exception as e:
                    st.error(f"❌ Error creating tasks: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    show_bulk_upload()
