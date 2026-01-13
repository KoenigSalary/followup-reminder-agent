"""
Settings Page Module for Follow-up & Reminder Team
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

def render_settings():
    """Render the settings page"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    st.header("⚙️ System Settings")
    st.markdown("Configure and manage your Follow-up & Reminder Team system")
    
    st.markdown("---")
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Settings", "👥 Team Directory", "🔔 Reminder Rules", "📊 System Info"])
    
    # =====================================
    # TAB 1: EMAIL SETTINGS
    # =====================================
    with tab1:
        st.subheader("📧 Email Configuration")
        
        # Load current settings
        load_dotenv(BASE_DIR / '.env')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### SMTP Settings")
            smtp_server = st.text_input("SMTP Server", value=os.getenv('SMTP_SERVER', 'smtp.office365.com'), disabled=True)
            smtp_port = st.text_input("SMTP Port", value=os.getenv('SMTP_PORT', '587'), disabled=True)
            smtp_user = st.text_input("SMTP Username", value=os.getenv('SMTP_USERNAME', ''), disabled=True)
            
            st.info("💡 To change email settings, edit the `.env` file in the project root")
        
        with col2:
            st.markdown("### Email Identity")
            sender_name = st.text_input("Sender Name", value=os.getenv('AGENT_SENDER_NAME', 'Follow-up Team'), disabled=True)
            sender_email = st.text_input("Sender Email", value=os.getenv('AGENT_SENDER_EMAIL', ''), disabled=True)
            
            st.markdown("### Status")
            if os.getenv('SMTP_USERNAME') and os.getenv('CEO_AGENT_EMAIL_PASSWORD'):
                st.success("✅ Email configuration is complete")
            else:
                st.error("❌ Email credentials missing in .env file")
        
        st.markdown("---")
        
        # Test email button
        st.markdown("### 🧪 Test Email Configuration")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            test_email = st.text_input("Send test email to:", placeholder="your.email@example.com")
            if st.button("📤 Send Test Email", use_container_width=True, type="primary"):
                if test_email and '@' in test_email:
                    with st.spinner("Sending test email..."):
                        try:
                            import smtplib
                            from email.mime.text import MIMEText
                            from email.mime.multipart import MIMEMultipart
                            
                            smtp_username = os.getenv('SMTP_USERNAME')
                            smtp_password = os.getenv('CEO_AGENT_EMAIL_PASSWORD')
                            
                            if not smtp_username or not smtp_password:
                                st.error("❌ Email credentials not configured")
                            else:
                                msg = MIMEMultipart()
                                msg['From'] = smtp_username
                                msg['To'] = test_email
                                msg['Subject'] = "Test Email - Follow-up & Reminder Team"
                                
                                body = """
                                <html>
                                <body>
                                    <h2>✅ Test Email Successful!</h2>
                                    <p>This is a test email from your Follow-up & Reminder Team system.</p>
                                    <p>If you received this email, your email configuration is working correctly.</p>
                                    <hr>
                                    <p style="color: #666; font-size: 12px;">© 2026 Koenig Solutions</p>
                                </body>
                                </html>
                                """
                                
                                msg.attach(MIMEText(body, 'html'))
                                
                                with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                                    server.starttls()
                                    server.login(smtp_username, smtp_password)
                                    server.sendmail(smtp_username, test_email, msg.as_string())
                                
                                st.success(f"✅ Test email sent successfully to {test_email}")
                                st.balloons()
                        except Exception as e:
                            st.error(f"❌ Failed to send test email: {e}")
                else:
                    st.warning("⚠️ Please enter a valid email address")
    
    # =====================================
    # TAB 2: TEAM DIRECTORY
    # =====================================
    with tab2:
        st.subheader("👥 Team Directory Management")
        
        team_file = BASE_DIR / "data" / "Team_Directory.xlsx"
        
        if team_file.exists():
            try:
                df = pd.read_excel(team_file)
                
                # Summary stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Users", len(df))
                with col2:
                    active_users = len(df[df['is_active'] == True]) if 'is_active' in df.columns else len(df)
                    st.metric("Active Users", active_users)
                with col3:
                    admins = len(df[df['role'] == 'admin']) if 'role' in df.columns else 0
                    st.metric("Admins", admins)
                with col4:
                    departments = df['department'].nunique() if 'department' in df.columns else 0
                    st.metric("Departments", departments)
                
                st.markdown("---")
                
                # Display team directory
                st.markdown("### 📋 Current Team Members")
                
                # Select columns to display
                display_cols = ['full_name', 'email', 'role', 'department', 'employee_id', 'is_active']
                available_cols = [col for col in display_cols if col in df.columns]
                
                if available_cols:
                    display_df = df[available_cols].copy()
                    
                    # Rename for better display
                    rename_map = {
                        'full_name': 'Name',
                        'email': 'Email',
                        'role': 'Role',
                        'department': 'Department',
                        'employee_id': 'Employee ID',
                        'is_active': 'Active'
                    }
                    display_df.rename(columns=rename_map, inplace=True)
                    
                    st.dataframe(display_df, use_container_width=True, height=400)
                else:
                    st.dataframe(df, use_container_width=True, height=400)
                
                st.markdown("---")
                
                # Download button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Team Directory (CSV)",
                        data=csv,
                        file_name="team_directory.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"❌ Error loading team directory: {e}")
        else:
            st.warning("⚠️ Team Directory file not found")
            st.info(f"Expected location: {team_file}")
    
    # =====================================
    # TAB 3: REMINDER RULES
    # =====================================
    with tab3:
        st.subheader("🔔 Reminder Frequency Rules")
        
        st.markdown("""
        Configure how often reminders are sent based on task priority.
        """)
        
        st.markdown("---")
        
        # Current rules
        st.markdown("### 📋 Current Rules")
        
        rules_data = {
            'Priority': ['🔴 URGENT', '🟠 HIGH', '🟡 MEDIUM', '🟢 LOW'],
            'Frequency': ['Every 1 day', 'Every 2 days', 'Every 3 days', 'Every 5 days'],
            'Description': [
                'Critical tasks requiring immediate attention',
                'Important tasks with near-term deadlines',
                'Regular tasks with moderate importance',
                'Low-priority tasks with flexible timelines'
            ]
        }
        
        rules_df = pd.DataFrame(rules_data)
        st.dataframe(rules_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Reminder schedule
        st.markdown("### 📅 Reminder Schedule")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Automated Reminders")
            st.info("""
            **Current Schedule:**
            - Daily at 9:00 AM
            - Checks all OPEN tasks
            - Sends emails based on priority rules
            - Updates Last Reminder Date
            """)
        
        with col2:
            st.markdown("#### Manual Reminders")
            st.info("""
            **On-Demand:**
            - Click "Send Task Reminders"
            - Review tasks before sending
            - Override frequency rules
            - Immediate delivery
            """)
        
        st.markdown("---")
        
        # Cron job status
        st.markdown("### ⚙️ Automation Status")
        
        import subprocess
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if 'run_reminders.py' in result.stdout:
                st.success("✅ Automated reminders are configured (cron job active)")
                with st.expander("View cron configuration"):
                    st.code(result.stdout, language='bash')
            else:
                st.warning("⚠️ No automated reminders configured")
                st.info("💡 Set up a cron job to run `python3 run_reminders.py` daily")
        except Exception as e:
            st.info("ℹ️ Could not check cron status")
    
    # =====================================
    # TAB 4: SYSTEM INFO
    # =====================================
    with tab4:
        st.subheader("📊 System Information")
        
        # System stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📂 Data Files")
            
            registry_file = BASE_DIR / "data" / "tasks_registry.xlsx"
            team_file = BASE_DIR / "data" / "Team_Directory.xlsx"
            
            if registry_file.exists():
                df = pd.read_excel(registry_file)
                st.metric("Tasks in Registry", len(df))
                st.metric("OPEN Tasks", len(df[df['Status'].str.upper() == 'OPEN']))
                st.metric("COMPLETED Tasks", len(df[df['Status'].str.upper() == 'COMPLETED']))
            else:
                st.error("❌ Tasks registry not found")
            
            st.markdown("---")
            
            st.markdown("### 📍 File Locations")
            st.code(f"""
Registry: {registry_file}
Team Dir: {team_file}
Logs: {BASE_DIR / 'logs'}
            """)
        
        with col2:
            st.markdown("### 🔧 System Version")
            st.info("""
            **Follow-up & Reminder Team**
            - Version: 2.0
            - Release Date: January 2026
            - Platform: Streamlit
            - Database: Excel (XLSX)
            """)
            
            st.markdown("---")
            
            st.markdown("### 📦 Dependencies")
            st.code("""
Python 3.x
streamlit
pandas
openpyxl
python-dotenv
smtplib (built-in)
            """)
        
        st.markdown("---")
        
        # System health check
        st.markdown("### 🏥 System Health Check")
        
        health_checks = []
        
        # Check registry file
        if registry_file.exists():
            health_checks.append(("✅", "Tasks Registry", "File exists and readable"))
        else:
            health_checks.append(("❌", "Tasks Registry", "File not found"))
        
        # Check team directory
        if team_file.exists():
            health_checks.append(("✅", "Team Directory", "File exists and readable"))
        else:
            health_checks.append(("❌", "Team Directory", "File not found"))
        
        # Check email config
        if os.getenv('SMTP_USERNAME') and os.getenv('CEO_AGENT_EMAIL_PASSWORD'):
            health_checks.append(("✅", "Email Config", "Credentials configured"))
        else:
            health_checks.append(("❌", "Email Config", "Credentials missing"))
        
        # Check logs directory
        logs_dir = BASE_DIR / "logs"
        if logs_dir.exists():
            health_checks.append(("✅", "Logs Directory", "Directory exists"))
        else:
            health_checks.append(("⚠️", "Logs Directory", "Directory not found"))
        
        # Display health checks
        health_df = pd.DataFrame(health_checks, columns=['Status', 'Component', 'Message'])
        st.dataframe(health_df, use_container_width=True, hide_index=True)
        
        # Overall status
        if all(check[0] == "✅" for check in health_checks):
            st.success("🎉 All systems operational!")
        else:
            st.warning("⚠️ Some components need attention")

if __name__ == "__main__":
    render_settings()
