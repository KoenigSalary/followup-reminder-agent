import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Task Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .priority-boss {
        background-color: #ff4b4b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .priority-urgent {
        background-color: #ff8c00;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .priority-medium {
        background-color: #ffd700;
        color: black;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .priority-low {
        background-color: #90ee90;
        color: black;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .status-pending {
        color: #ff8c00;
        font-weight: bold;
    }
    .status-completed {
        color: #00cc00;
        font-weight: bold;
    }
    .alert-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data(ttl=60)  # Cache for 60 seconds (auto-refresh)
def load_data():
    """Load task data from Excel file"""
    try:
        # Read from OneDrive location
        excel_path = '/Users/praveenchaudhary/Library/CloudStorage/OneDrive-KoenigSolutionsLtd/KS_AutoTask.xlsx'
        df = pd.read_excel(excel_path, sheet_name='Tasks')
        
        # Convert date columns to datetime
        date_columns = ['CreatedDate', 'CompletionDate', 'LastUpdateDate', 'End Date', 'Created On']
        for col in date_columns:
            if col in df.columns:
                # Handle both ISO format and Excel serial numbers
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
        
        # Calculate Age_Days (days since creation)
        if 'CreatedDate' in df.columns:
            now = pd.Timestamp.now(tz='UTC')
            df['Age_Days'] = (now - df['CreatedDate']).dt.days
        else:
            df['Age_Days'] = 0
        
        # Calculate Days Until Due
        if 'End Date' in df.columns:
            now = pd.Timestamp.now(tz='UTC')
            df['Days_Until_Due'] = (df['End Date'] - now).dt.days
        else:
            df['Days_Until_Due'] = None
        
        # Ensure ReminderCount is numeric
        if 'ReminderCount' in df.columns:
            df['ReminderCount'] = pd.to_numeric(df['ReminderCount'], errors='coerce').fillna(0).astype(int)
        else:
            df['ReminderCount'] = 0
        
        return df
    except FileNotFoundError:
        st.error("❌ Excel file not found. Please check the file path.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame()

# Get next reminder subject
def get_next_reminder_subject(row):
    """Generate the next reminder subject based on ReminderCount"""
    count = int(row.get('ReminderCount', 0))
    priority = row.get('Priority', 'Unknown')
    meeting_id = row.get('MeetingID', 'Unknown')
    
    if count >= 3:
        return "❌ No more reminders (Max reached)"
    elif count == 0:
        return f"📧 Reminder: {priority} Task - {meeting_id}"
    elif count == 1:
        return f"📧 2nd Reminder: {priority} Task - {meeting_id} - Action Required"
    elif count >= 2:
        return f"📧 URGENT: Final Reminder - {priority} Task - {meeting_id}"
    else:
        return "N/A"

# Priority color mapping
def get_priority_color(priority):
    """Return color for priority badge"""
    colors = {
        'Boss MOM': '#ff4b4b',
        'Urgent': '#ff8c00',
        'Medium': '#ffd700',
        'Low': '#90ee90'
    }
    return colors.get(priority, '#cccccc')

# Main dashboard
def main():
    # Header
    st.markdown('<div class="main-header">🎯 TASK MANAGEMENT</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No data available. Please check your Excel file.")
        return
    
    # Sidebar - Logo
    logo_path = '/Users/praveenchaudhary/Downloads/TaskDashboard/assets/koenig_logo.png'
    try:
        st.sidebar.image(logo_path, use_container_width=True)
        st.sidebar.markdown("---")
    except:
        pass  # If logo not found, continue without it
    
    # Sidebar filters
    st.sidebar.header("🔍 FILTERS")
    
    # Priority filter
    priorities = ['All'] + sorted(df['Priority'].dropna().unique().tolist())
    selected_priorities = st.sidebar.multiselect(
        "Priority",
        options=priorities,
        default=['All']
    )
    
    # Status filter
    statuses = ['All'] + sorted(df['Status'].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("Status", options=statuses)
    
    # Search filter
    search_term = st.sidebar.text_input("🔎 Search (TaskID, Details, MeetingID)")
    
    # Date range filter
    st.sidebar.subheader("📅 Created Date Range")
    if 'CreatedDate' in df.columns and not df['CreatedDate'].isna().all():
        min_date = df['CreatedDate'].min().date()
        max_date = df['CreatedDate'].max().date()
        date_range = st.sidebar.date_input(
            "Select range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = None
    
    # Apply filters
    filtered_df = df.copy()
    
    # Priority filter
    if 'All' not in selected_priorities and selected_priorities:
        filtered_df = filtered_df[filtered_df['Priority'].isin(selected_priorities)]
    
    # Status filter
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    # Search filter
    if search_term:
        search_cols = ['TaskID', 'TaskDetails', 'MeetingID']
        mask = filtered_df[search_cols].apply(
            lambda x: x.astype(str).str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        filtered_df = filtered_df[mask]
    
    # Date range filter
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        if 'CreatedDate' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['CreatedDate'].dt.date >= start_date) &
                (filtered_df['CreatedDate'].dt.date <= end_date)
            ]
    
    # Calculate metrics
    total_tasks = len(filtered_df)
    pending_tasks = len(filtered_df[filtered_df['Status'] == 'Pending'])
    completed_tasks = len(filtered_df[filtered_df['Status'] == 'Completed'])
    
    # Overdue tasks (End Date passed and Status = Pending)
    if 'Days_Until_Due' in filtered_df.columns:
        overdue_tasks = len(filtered_df[
            (filtered_df['Status'] == 'Pending') & 
            (filtered_df['Days_Until_Due'] < 0)
        ])
    else:
        overdue_tasks = 0
    
    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 TOTAL TASKS", total_tasks)
    
    with col2:
        st.metric("⏳ PENDING", pending_tasks, delta=f"{(pending_tasks/total_tasks*100):.0f}%" if total_tasks > 0 else "0%")
    
    with col3:
        st.metric("✅ COMPLETED", completed_tasks, delta=f"{(completed_tasks/total_tasks*100):.0f}%" if total_tasks > 0 else "0%")
    
    with col4:
        st.metric("⚠️ OVERDUE", overdue_tasks, delta="🔴" if overdue_tasks > 0 else "✅")
    
    st.markdown("---")
    
    # CHARTS ROW
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        st.subheader("📊 Priority Distribution")
        if not filtered_df.empty and 'Priority' in filtered_df.columns:
            priority_counts = filtered_df['Priority'].value_counts()
            fig_priority = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                color=priority_counts.index,
                color_discrete_map={
                    'Boss MOM': '#ff4b4b',
                    'Urgent': '#ff8c00',
                    'Medium': '#ffd700',
                    'Low': '#90ee90'
                },
                hole=0.4
            )
            fig_priority.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_priority, use_container_width=True)
        else:
            st.info("No data available")
    
    with chart_col2:
        st.subheader("📅 Task Age Distribution")
        if not filtered_df.empty and 'Age_Days' in filtered_df.columns:
            # Create age bins
            filtered_df['Age_Bin'] = pd.cut(
                filtered_df['Age_Days'],
                bins=[-1, 2, 5, 10, 30, 1000],
                labels=['0-2 days', '3-5 days', '6-10 days', '11-30 days', '30+ days']
            )
            age_counts = filtered_df['Age_Bin'].value_counts().sort_index()
            fig_age = px.bar(
                x=age_counts.index,
                y=age_counts.values,
                labels={'x': 'Task Age', 'y': 'Count'},
                color=age_counts.values,
                color_continuous_scale='Reds'
            )
            fig_age.update_layout(height=300, margin=dict(t=0, b=0, l=20, r=20), showlegend=False)
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No data available")
    
    with chart_col3:
        st.subheader("📧 Reminder Count")
        if not filtered_df.empty and 'ReminderCount' in filtered_df.columns:
            reminder_counts = filtered_df['ReminderCount'].value_counts().sort_index()
            fig_reminder = px.bar(
                x=reminder_counts.index.astype(str),
                y=reminder_counts.values,
                labels={'x': 'Reminders Sent', 'y': 'Task Count'},
                color=reminder_counts.values,
                color_continuous_scale='Blues'
            )
            fig_reminder.update_layout(height=300, margin=dict(t=0, b=0, l=20, r=20), showlegend=False)
            st.plotly_chart(fig_reminder, use_container_width=True)
        else:
            st.info("No data available")
    
    st.markdown("---")
    
    # ALERTS SECTION
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        st.subheader("⚠️ OVERDUE TASKS")
        if 'Days_Until_Due' in filtered_df.columns:
            overdue_df = filtered_df[
                (filtered_df['Status'] == 'Pending') & 
                (filtered_df['Days_Until_Due'] < 0)
            ].copy()
            
            if not overdue_df.empty:
                overdue_display = overdue_df[['TaskID', 'Priority', 'TaskDetails', 'Days_Until_Due']].copy()
                overdue_display['Days Overdue'] = -overdue_display['Days_Until_Due']
                overdue_display = overdue_display.drop('Days_Until_Due', axis=1)
                overdue_display = overdue_display.sort_values('Days Overdue', ascending=False)
                st.dataframe(overdue_display, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No overdue tasks!")
        else:
            st.info("End Date not available")
    
    with alert_col2:
        st.subheader("🔥 HIGH PRIORITY ALERTS")
        high_priority_df = filtered_df[
            (filtered_df['Priority'].isin(['Boss MOM', 'Urgent'])) &
            (filtered_df['Status'] == 'Pending') &
            (filtered_df['Age_Days'] > 3)
        ].copy()
        
        if not high_priority_df.empty:
            alert_display = high_priority_df[['TaskID', 'Priority', 'Age_Days', 'ReminderCount']].copy()
            alert_display = alert_display.sort_values('Age_Days', ascending=False)
            st.dataframe(alert_display, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No high priority alerts!")
    
    st.markdown("---")
    
    # TASKS AT FINAL REMINDER
    st.subheader("🚨 TASKS AT FINAL REMINDER (ReminderCount = 2)")
    final_reminder_df = filtered_df[
        (filtered_df['ReminderCount'] == 2) &
        (filtered_df['Status'] == 'Pending')
    ].copy()
    
    if not final_reminder_df.empty:
        final_display = final_reminder_df[['TaskID', 'Priority', 'TaskDetails', 'AssignedTo', 'Age_Days']].copy()
        st.dataframe(final_display, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No tasks at final reminder stage")
    
    st.markdown("---")
    
    # MAIN TASK TABLE
    st.subheader("📋 ALL TASKS")
    
    # Add Next Reminder column
    filtered_df['Next Reminder'] = filtered_df.apply(get_next_reminder_subject, axis=1)
    
    # Prepare display dataframe
    display_cols = [
        'TaskID', 'MeetingID', 'Priority', 'Status', 'TaskDetails', 
        'AssignedTo', 'Age_Days', 'ReminderCount', 'Next Reminder'
    ]
    
    # Add End Date if available
    if 'End Date' in filtered_df.columns:
        filtered_df['End Date Display'] = filtered_df['End Date'].dt.strftime('%Y-%m-%d')
        display_cols.insert(7, 'End Date Display')
    
    # Filter to only existing columns
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    display_df = filtered_df[display_cols].copy()
    
    # Format display
    display_df = display_df.sort_values('Age_Days', ascending=False)
    
    # Display table with color coding
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # EXPORT SECTION
    st.markdown("---")
    st.subheader("📥 EXPORT DATA")
    
    export_col1, export_col2, export_col3 = st.columns([1, 1, 2])
    
    with export_col1:
        # Export to CSV
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with export_col2:
        # Export summary
        summary_data = {
            'Metric': ['Total Tasks', 'Pending', 'Completed', 'Overdue', 'Boss MOM', 'Urgent', 'Medium', 'Low'],
            'Count': [
                total_tasks,
                pending_tasks,
                completed_tasks,
                overdue_tasks,
                len(filtered_df[filtered_df['Priority'] == 'Boss MOM']),
                len(filtered_df[filtered_df['Priority'] == 'Urgent']),
                len(filtered_df[filtered_df['Priority'] == 'Medium']),
                len(filtered_df[filtered_df['Priority'] == 'Low'])
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download Summary",
            data=summary_csv,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with export_col3:
        st.info(f"ℹ️ Showing {len(display_df)} of {len(df)} total tasks")
    
    # FOOTER
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.caption(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with footer_col2:
        st.caption("🔄 Auto-refresh: Every 60 seconds")
    
    with footer_col3:
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    main()