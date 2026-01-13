#!/usr/bin/env python3
"""
Streamlit App - Follow-up & Reminder Team
FINAL VERSION - Logo shifted right for perfect alignment
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from utils.excel_handler import ExcelHandler

# Excel file path
REGISTRY_FILE = BASE_DIR / "data" / "tasks_registry.xlsx"

# Page config
st.set_page_config(
    page_title="Follow-up & Reminder Team | Koenig Solutions",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with logo shifted right
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Center all login page content */
    .main .block-container {
        padding-top: 3rem;
    }
    
    /* Shift logo right */
    .logo-container {
        text-align: center;
        padding-left: 40px;  /* Shift logo to the right */
    }
    
    /* Centered header text */
    .centered-header {
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        margin: 20px auto 0 auto;
        padding: 0;
        line-height: 1.3;
    }
    
    /* Login Form Container */
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
    
    .login-form h3 {
        margin-bottom: 25px;
        text-align: center;
    }
    
    /* Sidebar Logo - Centered */
    .sidebar-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 15px 10px;
        margin-bottom: 15px;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Info box */
    .stAlert {
        border-radius: 8px;
        margin-top: 20px;
    }
    
    /* Divider */
    hr {
        margin: 25px 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .logo-container {
            padding-left: 0;  /* Reset on mobile */
        }
        
        .centered-header {
            font-size: 22px;
        }
        
        .login-form {
            padding: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

def show_login():
    """Display login page with logo shifted right"""
    logo_path = BASE_DIR / "assets" / "koenig_logo.png"
    
    # Logo shifted right using custom columns and padding
    col1, col2, col3 = st.columns([1.95, 2, 1.2])  # Shifted right by adjusting column ratios
    
    with col2:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        if logo_path.exists():
            st.image(str(logo_path), width=280)
        else:
            st.markdown('<h1 style="color: #1f77b4; font-size: 38px; text-align: center;">🏢 KOENIG</h1>', unsafe_allow_html=True)
            st.markdown('<p style="color: #666; font-size: 16px; text-align: center;">step forward</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Centered header text
    st.markdown('<h1 class="centered-header">Follow-up & Reminder Team</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Login form - centered
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
    """Display sidebar with centered logo"""
    logo_path = BASE_DIR / "assets" / "koenig_logo.png"
    
    with st.sidebar:
        # Centered logo with fixed width
        st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
        if logo_path.exists():
            # Center it using columns
            col1, col2, col3 = st.columns([0.5, 2, 0.5])
            with col2:
                st.image(str(logo_path), width=150)
        else:
            st.markdown("### 🏢 KOENIG")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        st.markdown(f"### 📧 Follow-up & Reminder Team")
        st.markdown(f"Welcome back, **{st.session_state.username}**! 👋")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📋 Navigation")
        page = st.radio(
            "Go to",
            ["📊 Dashboard", "📥 View Follow-ups", "✍️ Manual Entry", 
             "📂 Bulk MOM Upload", "📧 Send Task Reminders", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption("© 2026 Koenig Solutions")
        st.caption("Follow-up & Reminder Team v2.0")
        
        return page

def get_excel_handler():
    """Get ExcelHandler with correct path"""
    try:
        from utils.excel_handler import ExcelHandler
        return ExcelHandler(str(REGISTRY_FILE))
    except Exception as e:
        st.error(f"❌ Error initializing ExcelHandler: {e}")
        return None

def show_dashboard():
    """Display dashboard"""
    try:
        from views.dashboard_analytics import render_dashboard
        
        excel_handler = get_excel_handler()
        if excel_handler:
            render_dashboard(excel_handler)
    except Exception as e:
        st.error(f"❌ Dashboard error: {e}")
        st.exception(e)

def show_view_followups():
    """Display view follow-ups page"""
    try:
        from views.view_followups import render_view_followups
        
        excel_handler = get_excel_handler()
        if not excel_handler:
            return
        
        # Try with user_manager if available
        try:
            from utils.user_lookup import UserManager
            user_manager = UserManager()
            render_view_followups(excel_handler, user_manager)
        except:
            # Try without user_manager
            try:
                render_view_followups(excel_handler)
            except:
                # Create dummy user_manager
                class DummyUserManager:
                    def get_user_email(self, name):
                        return None
                render_view_followups(excel_handler, DummyUserManager())
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)

def show_manual_entry():
    """Display manual entry page"""
    try:
        from views.manual_entry import render_manual_entry
        
        excel_handler = get_excel_handler()
        if excel_handler:
            render_manual_entry(excel_handler)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)

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
        type=['xlsx', 'csv'],
        help="Upload Excel or CSV file with task information"
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
            else:
                st.error("Unsupported file type")
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
                    # Initialize ExcelHandler with correct path
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
                    else:
                        st.warning("No tasks were created.")
                
                except Exception as e:
                    st.error(f"❌ Error creating tasks: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


def show_send_reminders():
    """Display send reminders page"""
    st.header("📧 Send Task Reminders")
    st.markdown("Send email reminders to task owners for pending tasks.")
    
    st.markdown("---")
    
    if st.button("📤 Send Reminders Now", type="primary", use_container_width=True):
        with st.spinner("Sending reminders..."):
            try:
                import subprocess
                result = subprocess.run(
                    ['python3', str(BASE_DIR / 'run_reminders.py')],
                    capture_output=True,
                    text=True
                )
                
                st.text(result.stdout)
                
                if result.returncode == 0:
                    st.success("✅ Reminders sent successfully!")
                else:
                    st.error(f"❌ Error: {result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def show_settings():
    """Display settings page"""
    try:
        # Check if settings module exists in views
        settings_module = BASE_DIR / 'views' / 'settings_page.py'
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
    """Main app"""
    if not st.session_state.logged_in:
        show_login()
    else:
        page = show_sidebar()
        
        # Route to pages
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
