"""
Dashboard Analytics Component for Streamlit
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render_dashboard(excel_handler):
    """Render the complete analytics dashboard"""
    
    st.title("📊 Task Analytics Dashboard")
    
    # Load data
    df = excel_handler.load_data()
    
    # Normalize column names
    column_mapping = {
        'task_text': 'Subject',
        'deadline': 'Due Date',
        'owner': 'Owner',
        'status': 'Status',
        'priority': 'Priority',
        'created_on': 'Created On'
    }
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    if df.empty:
        st.info("📭 No tasks available for analysis")
        return
    
    # === KEY METRICS ROW ===
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(df)
    status_col = 'Status' if 'Status' in df.columns else 'status'
    open_tasks = len(df[df[status_col].str.upper() == 'OPEN'])
    completed_tasks = len(df[df[status_col].str.upper().isin(['COMPLETED', 'CLOSED'])])
    
    # Calculate overdue
    today = datetime.now().date()
    overdue_count = 0
    deadline_col = 'Due Date' if 'Due Date' in df.columns else 'deadline'
    
    for idx, row in df.iterrows():
        if row[status_col].upper() == 'OPEN' and pd.notna(row.get(deadline_col)):
            deadline = row[deadline_col]
            if isinstance(deadline, str):
                deadline = pd.to_datetime(deadline).date()
            elif hasattr(deadline, 'date'):
                deadline = deadline.date()
            if deadline < today:
                overdue_count += 1
    
    with col1:
        st.metric("📋 Total Tasks", total_tasks)
    with col2:
        st.metric("✅ Open Tasks", open_tasks)
    with col3:
        st.metric("🎉 Completed", completed_tasks)
    with col4:
        st.metric("⚠️ Overdue", overdue_count)
    
    st.divider()
    
    # === CHARTS ROW 1 ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Tasks by Priority")
        priority_col = 'Priority' if 'Priority' in df.columns else 'priority'
        
        if priority_col in df.columns:
            priority_counts = df[priority_col].value_counts()
            chart_data = pd.DataFrame({
                'Priority': priority_counts.index,
                'Count': priority_counts.values
            })
            
            # Add emojis
            priority_map = {
                'URGENT': '🔴 URGENT', 'urgent': '🔴 URGENT',
                'HIGH': '🟠 HIGH', 'high': '🟠 HIGH',
                'MEDIUM': '🟡 MEDIUM', 'medium': '🟡 MEDIUM',
                'LOW': '🟢 LOW', 'low': '🟢 LOW'
            }
            chart_data['Priority'] = chart_data['Priority'].map(lambda x: priority_map.get(x, str(x)))
            
            st.bar_chart(chart_data.set_index('Priority'))
        else:
            st.info("No priority data")
    
    with col2:
        st.subheader("📊 Task Status")
        
        if status_col in df.columns:
            status_counts = df[status_col].str.upper().value_counts()
            chart_data = pd.DataFrame({
                'Status': status_counts.index,
                'Count': status_counts.values
            })
            st.bar_chart(chart_data.set_index('Status'))
        else:
            st.info("No status data")
    
    st.divider()
    
    # === CHARTS ROW 2 ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Tasks by Owner")
        owner_col = 'Owner' if 'Owner' in df.columns else 'owner'
        
        if owner_col in df.columns:
            owner_counts = df[owner_col].value_counts().head(10)
            chart_data = pd.DataFrame({
                'Owner': owner_counts.index,
                'Count': owner_counts.values
            })
            st.bar_chart(chart_data.set_index('Owner'))
        else:
            st.info("No owner data")
    
    with col2:
        st.subheader("⏰ Upcoming Deadlines")
        
        open_df = df[df[status_col].str.upper() == 'OPEN'].copy()
        
        if len(open_df) > 0 and deadline_col in open_df.columns:
            upcoming = []
            for idx, row in open_df.iterrows():
                deadline = row[deadline_col]
                if pd.notna(deadline):
                    if isinstance(deadline, str):
                        deadline = pd.to_datetime(deadline).date()
                    elif hasattr(deadline, 'date'):
                        deadline = deadline.date()
                    
                    days_left = (deadline - today).days
                    subject_col = 'Subject' if 'Subject' in row.index else 'task_text'
                    task_name = str(row.get(subject_col, 'Unknown'))[:30]
                    
                    upcoming.append({
                        'Task': task_name,
                        'Days': days_left,
                        'Priority': row.get(priority_col, 'MEDIUM')
                    })
            
            if upcoming:
                upcoming_df = pd.DataFrame(upcoming).sort_values('Days').head(10)
                
                for _, row in upcoming_df.iterrows():
                    if row['Days'] < 0:
                        st.error(f"⚠️ {row['Task']} - **OVERDUE by {abs(row['Days'])} days**")
                    elif row['Days'] == 0:
                        st.warning(f"🔔 {row['Task']} - **DUE TODAY**")
                    elif row['Days'] <= 2:
                        st.warning(f"⏰ {row['Task']} - {row['Days']} days left")
                    else:
                        st.info(f"📅 {row['Task']} - {row['Days']} days left")
            else:
                st.success("✅ No upcoming deadlines")
        else:
            st.success("✅ No open tasks")
    
    st.divider()
    
    # === COMPLETION RATE ===
    st.subheader("📈 Completion Rate")
    
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.progress(completion_rate / 100)
            st.write(f"**{completion_rate:.1f}%** of tasks completed")
        
        with col2:
            st.metric("Completed", completed_tasks)
        
        with col3:
            st.metric("Remaining", open_tasks)
    
    st.divider()
    
    # === OVERDUE ALERT ===
    if overdue_count > 0:
        st.error(f"⚠️ **{overdue_count} Overdue Tasks Require Attention!**")
        
        with st.expander("📋 View Overdue Tasks"):
            overdue_tasks = []
            for idx, row in df.iterrows():
                if row[status_col].upper() == 'OPEN':
                    deadline = row.get(deadline_col)
                    if pd.notna(deadline):
                        if isinstance(deadline, str):
                            deadline = pd.to_datetime(deadline).date()
                        elif hasattr(deadline, 'date'):
                            deadline = deadline.date()
                        if deadline < today:
                            days_overdue = (today - deadline).days
                            subject_col = 'Subject' if 'Subject' in row.index else 'task_text'
                            overdue_tasks.append({
                                'Task': row.get(subject_col, 'Unknown'),
                                'Owner': row.get(owner_col, 'Unknown'),
                                'Deadline': deadline,
                                'Days Overdue': days_overdue,
                                'Priority': row.get(priority_col, 'MEDIUM')
                            })
            
            if overdue_tasks:
                overdue_df = pd.DataFrame(overdue_tasks).sort_values('Days Overdue', ascending=False)
                st.dataframe(overdue_df, use_container_width=True)
    else:
        st.success("✅ No overdue tasks - Great job!")
