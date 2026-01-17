import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pandas as pd

# Import Smart Reply Processor and Acknowledgement Manager
from smart_reply_processor import SmartReplyProcessor
from acknowledgement_manager import evaluate_performance, send_acknowledgement

from config import (
    EMAIL_SENDER,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_PASSWORD_ENV_KEY
)

load_dotenv()  # harmless locally, ignored in cloud

def _get_smtp_password():
    """Get SMTP password from environment or Streamlit secrets."""
    try:
        import streamlit as st
        password = st.secrets.get("EMAIL_PASSWORD_ENV_KEY")
        if password:
            return password
    except Exception:
        pass
    
    password = os.getenv("CEO_AGENT_EMAIL_PASSWORD")
    if not password:
        raise EnvironmentError(
            "Email password not configured. Please set 'CEO_AGENT_EMAIL_PASSWORD' "
            "environment variable or configure in Streamlit secrets."
        )
    return password

# Call this function when needed, not at module import
SMTP_PASSWORD = None  # Initialize as None

class EmailProcessor:
    def __init__(self):
        self.password = os.getenv(EMAIL_PASSWORD_ENV_KEY)

        if not self.password:
            raise EnvironmentError(
                f"Environment variable '{EMAIL_PASSWORD_ENV_KEY}' not set"
            )
        
        # Initialize smart processor
        self.smart_processor = SmartReplyProcessor()

    # -------------------------------------------------
    # Send generic email
    # -------------------------------------------------
    def send_email(self, subject, body, to_email=None):
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email or EMAIL_SENDER
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, self.password)
            server.send_message(msg)

    # -------------------------------------------------
    # SAFE AUTO-REPLY (Standard acknowledgment)
    # -------------------------------------------------
    def send_auto_reply(self, to_email, subject):
        reply_subject = f"Re: {subject}"
        body = (
            "Noted.\n\n"
            "This task is being tracked and reminder notifications are active until completion.\n\n"
            "Best regards,\n"
            "Task Follow-up Team"
        )

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = reply_subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, self.password)
            server.send_message(msg)
        
        print(f"📧 Standard auto-reply sent to {to_email}")

    # -------------------------------------------------
    # SMART ACKNOWLEDGMENT (With task summary)
    # -------------------------------------------------
    def send_smart_acknowledgment(self, to_email, subject, body):
        """
        Send smart acknowledgment email with task summary
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_SENDER
            msg["To"] = to_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, self.password)
                server.send_message(msg)
            
            print(f"✅ Smart acknowledgment sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send smart acknowledgment: {e}")
            return False

    # -------------------------------------------------
    # SEND PERFORMANCE ACKNOWLEDGEMENT (For completed tasks)
    # -------------------------------------------------
    def send_performance_feedback(self, completed_tasks):
        """
        Send performance-based acknowledgement for completed tasks
        """
        from pathlib import Path
        
        # Load Team Directory for email addresses
        team_file = Path("data/Team_Directory.xlsx")
        if not team_file.exists():
            print("⚠️ Team Directory not found, skipping performance emails")
            return
        
        team_df = pd.read_excel(team_file)
        
        for task in completed_tasks:
            try:
                # Find owner's email
                owner = task.get('owner', '')
                owner_row = team_df[
                    team_df['Name'].str.contains(owner, case=False, na=False) |
                    team_df['Email'].str.contains(owner, case=False, na=False)
                ]
                
                if len(owner_row) == 0:
                    print(f"⚠️ No email found for {owner}")
                    continue
                
                owner_email = owner_row.iloc[0]['Email']
                owner_full_name = owner_row.iloc[0]['Name']
                
                # Evaluate performance
                deadline = pd.to_datetime(task.get('deadline'))
                completed_date = pd.to_datetime(task.get('completed_date', datetime.now()))
                priority = task.get('priority', 'medium')
                
                performance = evaluate_performance(
                    deadline=deadline,
                    completed_date=completed_date,
                    priority=priority
                )
                
                # Prepare task dict for acknowledgement
                task_info = {
                    'task_id': task.get('task_id', ''),
                    'task_text': task.get('task_text', '')[:100],
                    'priority': priority,
                    'deadline': deadline.strftime('%Y-%m-%d'),
                    'completed_date': completed_date.strftime('%Y-%m-%d'),
                    'meeting_id': task.get('meeting_id', 'N/A')
                }
                
                # Send acknowledgement
                send_acknowledgement(
                    owner=owner_full_name,
                    owner_email=owner_email,
                    task=task_info,
                    performance=performance
                )
                
            except Exception as e:
                print(f"❌ Failed to send performance feedback for {task.get('task_id')}: {e}")

    # -------------------------------------------------
    # Process emails & update Excel (FULL AUTOMATION)
    # -------------------------------------------------
    def process_and_update(self, excel_handler):
        """
        FULLY AUTOMATED version with smart reply processing:
        1. Checks for employee replies to reminder emails
        2. Auto-processes COMPLETED/PENDING status updates
        3. Sends acknowledgment with summary
        4. Sends performance feedback for completed tasks
        5. Sends auto-reply for new emails
        """
        
        df = excel_handler.load_data()
        sent_count = 0
        
        for idx, row in df.iterrows():
            auto_reply = str(row.get("Auto Reply Sent", "")).strip().lower()
            
            if auto_reply != "yes":
                subject = row.get("Subject", "CEO Follow-up Task")
                email_body = row.get("Body", "")
                from_email = row.get("From", "")
                
                # Check if this is a REPLY to a reminder email
                is_reply = subject.startswith("Re: ⏰") or "Re:" in subject
                
                if is_reply and email_body:
                    # This is a reply - process it smartly
                    try:
                        # Extract employee name from email
                        if from_email and '@' in from_email:
                            employee_name = from_email.split('@')[0].replace('.', ' ').title()
                        else:
                            employee_name = "Team Member"
                        
                        print(f"\n🔍 Processing reply from {from_email}...")
                        
                        # Process the reply and update tasks
                        result = self.smart_processor.process_reply_and_update_tasks(
                            email_body=email_body,
                            from_email=from_email
                        )
                        
                        if result['success'] and (result['completed'] or result['pending']):
                            # Generate acknowledgment email
                            ack_body = self.smart_processor.generate_acknowledgment_email(
                                process_result=result,
                                to_name=employee_name
                            )
                            
                            # Send acknowledgment
                            reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
                            self.send_smart_acknowledgment(
                                to_email=from_email,
                                subject=reply_subject,
                                body=ack_body
                            )
                            
                            # 🌟 NEW: Send performance feedback for completed tasks
                            if result['completed']:
                                print(f"\n🎉 Sending performance feedback for {len(result['completed'])} completed tasks...")
                                self.send_performance_feedback(result['completed'])
                            
                            # Mark as processed
                            df.at[idx, "Auto Reply Sent"] = "Yes"
                            if "Processed Date" in df.columns:
                                df.at[idx, "Processed Date"] = datetime.now()
                            
                            sent_count += 1
                            
                            print(f"✅ Smart processed reply from {from_email}")
                            print(f"   Completed: {len(result['completed'])} tasks")
                            print(f"   Pending: {len(result['pending'])} tasks")
                            print(f"   Performance emails: {len(result['completed'])} sent")
                        else:
                            # Reply didn't contain task updates - send standard acknowledgment
                            print(f"ℹ️  No task updates found, sending standard reply")
                            self.send_auto_reply(
                                to_email=from_email,
                                subject=subject
                            )
                            df.at[idx, "Auto Reply Sent"] = "Yes"
                            sent_count += 1
                            
                    except Exception as e:
                        print(f"❌ Error processing smart reply: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fallback to standard auto-reply
                        self.send_auto_reply(
                            to_email=from_email if from_email else EMAIL_SENDER,
                            subject=subject
                        )
                        df.at[idx, "Auto Reply Sent"] = "Yes"
                        sent_count += 1
                else:
                    # New email (not a reply) - send standard auto-reply
                    self.send_auto_reply(
                        to_email=from_email if from_email else EMAIL_SENDER,
                        subject=subject
                    )
                    df.at[idx, "Auto Reply Sent"] = "Yes"
                    sent_count += 1
                
                break  # ONLY one email per run
        
        excel_handler.save_data(df)
        return sent_count
