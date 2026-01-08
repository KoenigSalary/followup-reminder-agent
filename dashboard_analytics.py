import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def render_dashboard(excel_handler):
    """
    Renders the Dashboard Analytics section
    """
    st.header("📊 Dashboard Analytics")
    
    # Load data
    df = excel_handler.load_data()
    
    # File now has clean lowercase columns only - no normalization needed!
    
    if df.empty:
        st.info("📭 No tasks available for analysis")
        return
    
    # === KEY METRICS ROW ===
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(df)
    
    # Use lowercase columns directly
    status_col = 'status'
    open_tasks = len(df[df[status_col].astype(str).str.upper() == 'OPEN'])
    completed_tasks = len(df[df[status_col].astype(str).str.upper().isin(['COMPLETED', 'CLOSED'])])
    
    # Calculate overdue
    today = datetime.now().date()
    overdue_count = 0
    deadline_col = 'deadline'
    
    for idx, row in df.iterrows():
        if str(row[status_col]).upper() == 'OPEN' and pd.notna(row.get(deadline_col)):
            deadline = row[deadline_col]
            if isinstance(deadline, str):
                try:
                    deadline = pd.to_datetime(deadline).date()
                except:
                    continue
            elif hasattr(deadline, 'date'):
                deadline = deadline.date()
            
            if deadline < today:
                overdue_count += 1
    
    # Display metrics
    with col1:
        st.metric("📋 Total Tasks", total_tasks)
    
    with col2:
        st.metric("🟢 Open Tasks", open_tasks)
    
    with col3:
        st.metric("✅ Completed", completed_tasks)
    
    with col4:
        st.metric("🔴 Overdue", overdue_count)
    
    st.markdown("---")
    
    # === CHARTS ROW ===
    if total_tasks > 0:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("📊 Status Distribution")
            status_counts = df[status_col].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Tasks by Status"
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with chart_col2:
            st.subheader("👥 Tasks by Owner")
            owner_col = 'owner'
            if owner_col in df.columns:
                owner_counts = df[owner_col].value_counts().head(10)
                fig_owner = px.bar(
                    x=owner_counts.index,
                    y=owner_counts.values,
                    labels={'x': 'Owner', 'y': 'Task Count'},
                    title="Top 10 Task Owners"
                )
                st.plotly_chart(fig_owner, use_container_width=True)
        
        st.markdown("---")
        
        # === PRIORITY BREAKDOWN ===
        st.subheader("⚡ Priority Breakdown")
        priority_col = 'priority'
        if priority_col in df.columns:
            priority_counts = df[priority_col].value_counts()
            priority_chart_cols = st.columns(len(priority_counts))
            
            for idx, (priority, count) in enumerate(priority_counts.items()):
                with priority_chart_cols[idx]:
                    if str(priority).upper() == 'HIGH':
                        icon = "🔴"
                    elif str(priority).upper() == 'MEDIUM':
                        icon = "🟡"
                    elif str(priority).upper() == 'LOW':
                        icon = "🟢"
                    else:
                        icon = "⚪"
                    st.metric(f"{icon} {priority}", count)
