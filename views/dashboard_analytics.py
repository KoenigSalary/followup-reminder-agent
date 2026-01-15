# -*- coding: utf-8 -*-
"""
Enhanced Dashboard Analytics for Follow-up Reminder Agent
Features:
- Real-time KPI metrics
- Interactive charts
- Trend analysis
- Performance insights
- Manager overview
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.task_normalizer import normalize_df

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ModuleNotFoundError:
    px = None
    go = None

def get_priority_emoji(priority):
    """Get emoji for priority level"""
    priority_map = {
        'URGENT': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }
    return priority_map.get(str(priority).upper(), '⚪')


def get_status_emoji(status):
    """Get emoji for status"""
    status_map = {
        'OPEN': '📋',
        'COMPLETED': '✅',
        'DONE': '✅',
        'BLOCKED': '🚨',
        'IN PROGRESS': '🔄',
        'DELETED': '🗑️'
    }
    return status_map.get(str(status).upper(), '❓')


def calculate_completion_rate(df):
    """Calculate task completion rate"""
    if df.empty:
        return 0
    total = len(df)
    completed = len(df[df['status'].isin(['DONE', 'COMPLETED'])])
    return round((completed / total) * 100, 1)


def get_overdue_tasks(df, today):
    """Get overdue tasks"""
    return df[
        (df['status'] == 'OPEN') &
        (df['due_date'].notna()) &
        (df['due_date'] < today)
    ]


def get_due_soon_tasks(df, today, days=3):
    """Get tasks due within specified days"""
    future_date = today + timedelta(days=days)
    return df[
        (df['status'] == 'OPEN') &
        (df['due_date'].notna()) &
        (df['due_date'] >= today) &
        (df['due_date'] <= future_date)
    ]


def render_kpi_cards(df, today):
    """Render KPI metric cards"""
    total = len(df)
    open_count = len(df[df['status'] == 'OPEN'])
    completed_count = len(df[df['status'].isin(['DONE', 'COMPLETED'])])
    overdue = get_overdue_tasks(df, today)
    due_today = df[(df['status'] == 'OPEN') & (df['due_date'] == today)]
    due_this_week = get_due_soon_tasks(df, today, days=7)
    
    completion_rate = calculate_completion_rate(df)
    
    # KPI Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Tasks",
            value=total,
            help="All tasks (excluding deleted)"
        )
    
    with col2:
        st.metric(
            label="📋 Open Tasks",
            value=open_count,
            delta=f"{open_count - completed_count} pending",
            delta_color="inverse",
            help="Tasks currently in progress"
        )
    
    with col3:
        st.metric(
            label="✅ Completed",
            value=completed_count,
            delta=f"{completion_rate}% rate",
            help="Successfully completed tasks"
        )
    
    with col4:
        st.metric(
            label="⚠️ Overdue",
            value=len(overdue),
            delta=f"{len(due_today)} due today" if len(due_today) > 0 else "0 due today",
            delta_color="off" if len(overdue) == 0 else "inverse",
            help="Tasks past their deadline"
        )
    
    # KPI Row 2
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        urgent_count = len(df[df['priority'] == 'URGENT'])
        st.metric(
            label="🔴 Urgent Tasks",
            value=urgent_count,
            help="High priority tasks requiring immediate attention"
        )
    
    with col6:
        blocked_count = len(df[df['status'] == 'BLOCKED'])
        st.metric(
            label="🚨 Blocked",
            value=blocked_count,
            delta="Need help" if blocked_count > 0 else "None",
            delta_color="inverse" if blocked_count > 0 else "off",
            help="Tasks waiting for assistance"
        )
    
    with col7:
        st.metric(
            label="📅 Due This Week",
            value=len(due_this_week),
            help="Tasks due within 7 days"
        )
    
    with col8:
        avg_days = calculate_avg_completion_time(df)
        st.metric(
            label="⏱️ Avg. Completion",
            value=f"{avg_days} days" if avg_days else "N/A",
            help="Average time to complete tasks"
        )


def calculate_avg_completion_time(df):
    """Calculate average completion time"""
    completed = df[df['status'].isin(['DONE', 'COMPLETED'])].copy()
    if completed.empty:
        return None
    
    # Try to calculate from created_on and completed date
    if 'created_on' in completed.columns and 'completed_date' in completed.columns:
        completed['created_on'] = pd.to_datetime(completed['created_on'], errors='coerce')
        completed['completed_date'] = pd.to_datetime(completed['completed_date'], errors='coerce')
        completed['days_to_complete'] = (completed['completed_date'] - completed['created_on']).dt.days
        avg = completed['days_to_complete'].mean()
        if pd.notna(avg):
            return round(avg, 1)
    
    return None


def render_priority_breakdown(df):
    """Render priority breakdown chart"""
    st.subheader("🎯 Tasks by Priority")
    
    priority_order = ['URGENT', 'HIGH', 'MEDIUM', 'LOW']
    priority_counts = df['priority'].value_counts().reindex(priority_order, fill_value=0)
    
    # Create interactive bar chart
    fig = px.bar(
        x=priority_counts.index,
        y=priority_counts.values,
        labels={'x': 'Priority', 'y': 'Number of Tasks'},
        color=priority_counts.index,
        color_discrete_map={
            'URGENT': '#FF4B4B',
            'HIGH': '#FF8C00',
            'MEDIUM': '#FFD700',
            'LOW': '#90EE90'
        }
    )
    
    fig.update_layout(
        showlegend=False,
        height=350,
        xaxis_title="Priority Level",
        yaxis_title="Task Count"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Priority details
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Priority Distribution:**")
        for priority in priority_order:
            count = priority_counts.get(priority, 0)
            emoji = get_priority_emoji(priority)
            percentage = (count / len(df) * 100) if len(df) > 0 else 0
            st.write(f"{emoji} **{priority}**: {count} ({percentage:.1f}%)")

        if px is None:
            st.warning("Plotly not installed. Showing basic chart.")
            st.bar_chart(status_counts)
            return

def render_status_breakdown(df):
    """Render status breakdown"""
    st.subheader("📊 Task Status Overview")

    status_counts = df['status'].value_counts()

    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        color=status_counts.index,
        color_discrete_map={
            'OPEN': '#FFA500',
            'COMPLETED': '#90EE90',
            'DONE': '#90EE90',
            'BLOCKED': '#FF4B4B',
            'IN PROGRESS': '#4169E1'
        }
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)

    if px is None:
        st.warning("Plotly not installed. Showing basic chart.")
        st.bar_chart(status_counts)
        return

def render_owner_workload(df):
    """Render owner workload analysis"""
    st.subheader("👥 Team Workload Distribution")
    
    owner_status = df.groupby(['owner', 'status']).size().unstack(fill_value=0)
    
    # Stacked bar chart
    fig = go.Figure()
    
    colors = {
        'OPEN': '#FFA500',
        'COMPLETED': '#90EE90',
        'DONE': '#90EE90',
        'BLOCKED': '#FF4B4B'
    }
    
    for status in owner_status.columns:
        fig.add_trace(go.Bar(
            name=status,
            x=owner_status.index,
            y=owner_status[status],
            marker_color=colors.get(status, '#808080')
        ))
    
    fig.update_layout(
        barmode='stack',
        height=400,
        xaxis_title="Team Member",
        yaxis_title="Number of Tasks",
        legend_title="Status"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Workload table
    st.markdown("**Individual Workload:**")
    workload_summary = df.groupby('owner').agg({
        'status': lambda x: (x == 'OPEN').sum(),
        'priority': lambda x: (x == 'URGENT').sum()
    }).rename(columns={'status': 'Open Tasks', 'priority': 'Urgent Tasks'})
    
    workload_summary = workload_summary.sort_values('Open Tasks', ascending=False)
    st.dataframe(workload_summary, use_container_width=True)     

def render_timeline_view(df, today):
    """Render timeline of tasks"""
    st.subheader("📅 Task Timeline")
    
    df_timeline = df[df['due_date'].notna()].copy()
    
    if df_timeline.empty:
        st.info("No tasks with due dates to display.")
        return
    
    df_timeline['status_display'] = df_timeline['status'].apply(lambda x: get_status_emoji(x) + ' ' + x)
    
    # Timeline chart
    fig = px.timeline(
        df_timeline,
        x_start='due_date',
        x_end='due_date',
        y='owner',
        color='priority',
        hover_data=['subject', 'status'],
        color_discrete_map={
            'URGENT': '#FF4B4B',
            'HIGH': '#FF8C00',
            'MEDIUM': '#FFD700',
            'LOW': '#90EE90'
        }
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_overdue_alerts(df, today):
    """Render overdue tasks alert"""
    overdue = get_overdue_tasks(df, today)
    
    if not overdue.empty:
        st.error(f"🚨 **{len(overdue)} Overdue Tasks Require Immediate Attention!**")
        
        with st.expander("📋 View Overdue Tasks", expanded=True):
            for idx, task in overdue.iterrows():
                days_overdue = (today - task['due_date']).days
                priority_emoji = get_priority_emoji(task['priority'])
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{task.get('subject', 'No subject')}**")
                    st.caption(f"Owner: {task.get('owner', 'Unknown')}")
                with col2:
                    st.markdown(f"{priority_emoji} {task['priority']}")
                with col3:
                    st.markdown(f"⏰ **{days_overdue}** days overdue")
                
                st.divider()


def render_upcoming_tasks(df, today):
    """Render upcoming tasks"""
    due_soon = get_due_soon_tasks(df, today, days=7)
    
    if not due_soon.empty:
        st.warning(f"📅 **{len(due_soon)} Tasks Due This Week**")
        
        with st.expander("📋 View Upcoming Tasks", expanded=False):
            due_soon_sorted = due_soon.sort_values('due_date')
            for idx, task in due_soon_sorted.iterrows():
                days_remaining = (task['due_date'] - today).days
                priority_emoji = get_priority_emoji(task['priority'])
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{task.get('subject', 'No subject')}**")
                    st.caption(f"Owner: {task.get('owner', 'Unknown')}")
                with col2:
                    st.markdown(f"{priority_emoji} {task['priority']}")
                with col3:
                    if days_remaining == 0:
                        st.markdown("📅 **Today**")
                    elif days_remaining == 1:
                        st.markdown("📅 **Tomorrow**")
                    else:
                        st.markdown(f"📅 **{days_remaining}** days")
                
                st.divider()


def render_performance_insights(df):
    """Render performance insights"""
    st.subheader("📈 Performance Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Completion Rate by Priority:**")
        for priority in ['URGENT', 'HIGH', 'MEDIUM', 'LOW']:
            priority_tasks = df[df['priority'] == priority]
            if not priority_tasks.empty:
                completed = len(priority_tasks[priority_tasks['status'].isin(['DONE', 'COMPLETED'])])
                total = len(priority_tasks)
                rate = (completed / total * 100) if total > 0 else 0
                emoji = get_priority_emoji(priority)
                st.progress(rate / 100, text=f"{emoji} {priority}: {rate:.1f}% ({completed}/{total})")
    
    with col2:
        st.markdown("**👥 Top Performers:**")
        completed_by_owner = df[df['status'].isin(['DONE', 'COMPLETED'])].groupby('owner').size().sort_values(ascending=False)
        
        if not completed_by_owner.empty:
            for i, (owner, count) in enumerate(completed_by_owner.head(5).items(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                st.write(f"{medal} **{owner}**: {count} tasks completed")
        else:
            st.info("No completed tasks yet.")


def render_dashboard(excel_handler):
    """Main dashboard rendering function"""
    st.title("📊 Dashboard Analytics")
    
    # Load and prepare data
    df = excel_handler.load_data()
    df = normalize_df(df)
    
    if df.empty:
        st.info("📭 No tasks available for analytics.")
        st.markdown("""
        ### Getting Started
        1. Create tasks via **✍️ Manual Entry**
        2. Upload MOM files via **📂 Bulk MOM Upload**
        3. Come back here to view analytics
        """)
        return
    
    # Data preparation
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Normalize column names
    rename_map = {
        "task_text": "subject",
        "due date": "due_date",
        "deadline": "due_date",
    }
    df.rename(columns={c: rename_map.get(c, c) for c in df.columns}, inplace=True)
    
    # Ensure required columns exist
    for col in ["subject", "owner", "priority", "status", "due_date"]:
        if col not in df.columns:
            df[col] = None
    
    # Normalize status
    df["status"] = df["status"].astype(str).str.upper().str.strip()
    
    # Filter out deleted tasks
    df = df[df["status"] != "DELETED"]
    
    if df.empty:
        st.warning("⚠️ No active tasks to analyze (all tasks are deleted).")
        return
    
    # Convert due_date to datetime
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
    
    # Normalize priority
    df["priority"] = df["priority"].astype(str).str.upper().str.strip()
    df["priority"] = df["priority"].replace({'NAN': 'MEDIUM', '': 'MEDIUM'})
    
    today = date.today()
    
    # Date filter in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Filters")
    
    date_filter = st.sidebar.radio(
        "Date Range:",
        ["All Time", "This Week", "This Month", "Custom"],
        index=0
    )
    
    if date_filter == "This Week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        df = df[(df['due_date'] >= start_date) & (df['due_date'] <= end_date)]
    elif date_filter == "This Month":
        start_date = today.replace(day=1)
        df = df[df['due_date'] >= start_date]
    elif date_filter == "Custom":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("From:", today - timedelta(days=30))
        with col2:
            end_date = st.date_input("To:", today)
        df = df[(df['due_date'] >= start_date) & (df['due_date'] <= end_date)]
    
    # Render dashboard sections
    render_kpi_cards(df, today)
    
    st.divider()
    
    # Alerts section
    render_overdue_alerts(df, today)
    render_upcoming_tasks(df, today)
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        render_priority_breakdown(df)
    
    with col2:
        render_status_breakdown(df)
    
    st.divider()
    
    render_owner_workload(df)
    
    st.divider()
    
    render_performance_insights(df)
    
    st.divider()
    
    render_timeline_view(df, today)
    
    # Export section
    st.divider()
    st.subheader("📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"task_analytics_{today}.csv",
            mime="text/csv"
        )
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Footer
    st.divider()
    st.caption(f"📊 Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption(f"📈 Showing {len(df)} active tasks")
