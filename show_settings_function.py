def show_settings():
    """Display settings page with full functionality"""
    try:
        # Try to import from views folder
        import sys
        from pathlib import Path
        
        BASE_DIR = Path(__file__).resolve().parent
        views_path = BASE_DIR / 'views'
        
        # Check if settings_page.py exists in views folder
        if (views_path / 'settings_page.py').exists():
            sys.path.insert(0, str(views_path))
            from settings_page import render_settings
            render_settings()
        else:
            # Fallback: inline implementation
            import streamlit as st
            import pandas as pd
            import os
            from dotenv import load_dotenv
            
            st.header("⚙️ System Settings")
            st.markdown("Configure and manage your Follow-up & Reminder Team system")
            
            st.markdown("---")
            
            # Create tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Settings", "👥 Team Directory", "🔔 Reminder Rules", "📊 System Info"])
            
            # TAB 1: EMAIL SETTINGS
            with tab1:
                st.subheader("📧 Email Configuration")
                
                load_dotenv(BASE_DIR / '.env')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### SMTP Settings")
                    st.text_input("SMTP Server", value=os.getenv('SMTP_SERVER', 'smtp.office365.com'), disabled=True)
                    st.text_input("SMTP Port", value=os.getenv('SMTP_PORT', '587'), disabled=True)
                    st.text_input("SMTP Username", value=os.getenv('SMTP_USERNAME', ''), disabled=True)
                    st.info("💡 To change settings, edit `.env` file")
                
                with col2:
                    st.markdown("### Email Identity")
                    st.text_input("Sender Name", value=os.getenv('AGENT_SENDER_NAME', 'Follow-up Team'), disabled=True)
                    st.text_input("Sender Email", value=os.getenv('AGENT_SENDER_EMAIL', ''), disabled=True)
                    
                    if os.getenv('SMTP_USERNAME') and os.getenv('CEO_AGENT_EMAIL_PASSWORD'):
                        st.success("✅ Email configured")
                    else:
                        st.error("❌ Missing credentials")
            
            # TAB 2: TEAM DIRECTORY
            with tab2:
                st.subheader("👥 Team Directory Management")
                
                team_file = BASE_DIR / "data" / "Team_Directory.xlsx"
                
                if team_file.exists():
                    df = pd.read_excel(team_file)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Users", len(df))
                    with col2:
                        active = len(df[df['is_active'] == True]) if 'is_active' in df.columns else len(df)
                        st.metric("Active", active)
                    with col3:
                        admins = len(df[df['role'] == 'admin']) if 'role' in df.columns else 0
                        st.metric("Admins", admins)
                    with col4:
                        depts = df['department'].nunique() if 'department' in df.columns else 0
                        st.metric("Departments", depts)
                    
                    st.markdown("---")
                    st.markdown("### 📋 Team Members")
                    
                    display_cols = ['full_name', 'email', 'role', 'department', 'is_active']
                    available = [c for c in display_cols if c in df.columns]
                    
                    if available:
                        st.dataframe(df[available], use_container_width=True, height=400)
                    else:
                        st.dataframe(df, use_container_width=True, height=400)
                else:
                    st.warning("⚠️ Team Directory not found")
            
            # TAB 3: REMINDER RULES
            with tab3:
                st.subheader("🔔 Reminder Frequency Rules")
                
                rules = {
                    'Priority': ['🔴 URGENT', '🟠 HIGH', '🟡 MEDIUM', '🟢 LOW'],
                    'Frequency': ['Every 1 day', 'Every 2 days', 'Every 3 days', 'Every 5 days'],
                    'Description': [
                        'Critical - immediate attention',
                        'Important - near-term deadlines',
                        'Regular - moderate importance',
                        'Low - flexible timelines'
                    ]
                }
                
                st.dataframe(pd.DataFrame(rules), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### 📅 Schedule")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**Automated**: Daily at 9:00 AM")
                with col2:
                    st.info("**Manual**: On-demand via UI")
            
            # TAB 4: SYSTEM INFO
            with tab4:
                st.subheader("📊 System Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📂 Data Files")
                    
                    registry = BASE_DIR / "data" / "tasks_registry.xlsx"
                    if registry.exists():
                        df = pd.read_excel(registry)
                        st.metric("Total Tasks", len(df))
                        st.metric("OPEN", len(df[df['Status'].str.upper() == 'OPEN']))
                        st.metric("COMPLETED", len(df[df['Status'].str.upper() == 'COMPLETED']))
                
                with col2:
                    st.markdown("### 🔧 Version")
                    st.info("""
                    **Follow-up & Reminder Team**
                    - Version: 2.0
                    - Platform: Streamlit
                    - Database: Excel
                    """)
                
                st.markdown("---")
                st.markdown("### 🏥 System Health")
                
                checks = []
                
                if registry.exists():
                    checks.append(("✅", "Tasks Registry", "OK"))
                else:
                    checks.append(("❌", "Tasks Registry", "Not found"))
                
                if team_file.exists():
                    checks.append(("✅", "Team Directory", "OK"))
                else:
                    checks.append(("❌", "Team Directory", "Not found"))
                
                if os.getenv('SMTP_USERNAME'):
                    checks.append(("✅", "Email Config", "OK"))
                else:
                    checks.append(("❌", "Email Config", "Missing"))
                
                st.dataframe(pd.DataFrame(checks, columns=['Status', 'Component', 'Message']), 
                           use_container_width=True, hide_index=True)
                
                if all(c[0] == "✅" for c in checks):
                    st.success("🎉 All systems operational!")
                else:
                    st.warning("⚠️ Some issues detected")
    
    except Exception as e:
        st.error(f"❌ Settings error: {e}")
        st.exception(e)
