# run_reminders.py - UPDATED WITH MULTI-OWNER SUPPORT
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date
import pandas as pd
import numpy as np
from pathlib import Path
import re

from dotenv import load_dotenv
load_dotenv()

# ========== IMPORT FROM CONFIG ==========
try:
    from config import HARDCODED_EMAILS, REMINDER_FREQUENCY_DAYS
    print("✅ Loaded settings from config.py")
except ImportError as e:
    print(f"⚠️ Could not import from config.py: {e}")
    # Fallback defaults
    HARDCODED_EMAILS = {}
    REMINDER_FREQUENCY_DAYS = {
        "URGENT": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 7,
    }

# Import based on your structure
try:
    from utils.excel_handler import ExcelHandler
except ImportError:
    # Fallback for direct testing
    class ExcelHandler:
        def __init__(self, filepath):
            self.filepath = filepath
        def load_data(self):
            return pd.read_excel(self.filepath)
        def save_data(self, df):
            df.to_excel(self.filepath, index=False)

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REGISTRY_FILE = DATA_DIR / "tasks_registry.xlsx"
TEAM_FILE = DATA_DIR / "Team_Directory.xlsx"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# -----------------------------
# Settings helper functions (from original code)
# -----------------------------
def _get_setting(key: str, default=None):
    """Read from OS env first, then Streamlit secrets (Cloud)."""
    val = os.getenv(key)
    if val is not None and str(val).strip() != "":
        return val

    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default

def _require_setting(key: str):
    val = _get_setting(key)
    if val is None or str(val).strip() == "":
        raise ValueError(
            f"Missing required setting: {key}. "
            f"Set it in Streamlit Secrets (Cloud) or .env (local)."
        )
    return val

# -----------------------------
# ENV CONFIG - FIXED VERSION
# -----------------------------
def get_env_config():
    """Get environment variables with fallbacks - Streamlit Cloud compatible."""
    import os
    
    # Initialize with defaults
    config = {
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587,
        "smtp_username": "",
        "smtp_password": "",
        "sender_name": "Follow-up Reminder Agent",
        "sender_email": "",
    }
    
    # Method 1: Try Streamlit secrets first (for Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            # Check each key in secrets
            if "SMTP_SERVER" in st.secrets:
                config["smtp_server"] = st.secrets["SMTP_SERVER"]
            if "SMTP_PORT" in st.secrets:
                config["smtp_port"] = int(st.secrets["SMTP_PORT"])
            if "SMTP_USERNAME" in st.secrets:
                config["smtp_username"] = st.secrets["SMTP_USERNAME"]
            if "CEO_AGENT_EMAIL_PASSWORD" in st.secrets:
                config["smtp_password"] = st.secrets["CEO_AGENT_EMAIL_PASSWORD"]
            if "AGENT_SENDER_NAME" in st.secrets:
                config["sender_name"] = st.secrets["AGENT_SENDER_NAME"]
            if "AGENT_SENDER_EMAIL" in st.secrets:
                config["sender_email"] = st.secrets["AGENT_SENDER_EMAIL"]
            
            # If we got username and password from secrets, use them
            if config["smtp_username"] and config["smtp_password"]:
                print("✅ Using Streamlit secrets for SMTP configuration")
                # Set sender email if not already set
                if not config["sender_email"]:
                    config["sender_email"] = config["smtp_username"]
                return config
    except Exception:
        pass  # Continue to .env file
    
    # Method 2: Try .env file (for local development)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        config["smtp_server"] = os.getenv("SMTP_SERVER", config["smtp_server"])
        config["smtp_port"] = int(os.getenv("SMTP_PORT", config["smtp_port"]))
        config["smtp_username"] = os.getenv("SMTP_USERNAME", config["smtp_username"])
        config["smtp_password"] = os.getenv("CEO_AGENT_EMAIL_PASSWORD", config["smtp_password"])
        config["sender_name"] = os.getenv("AGENT_SENDER_NAME", config["sender_name"])
        config["sender_email"] = os.getenv("AGENT_SENDER_EMAIL", config["sender_email"])
        
        # Set sender email if not already set
        if not config["sender_email"] and config["smtp_username"]:
            config["sender_email"] = config["smtp_username"]
            
        print("⚠️ Using .env file for SMTP configuration")
        return config
        
    except Exception as e:
        print(f"⚠️ Error loading .env: {e}")
        return config
# -----------------------------
# TEAM DIRECTORY
# -----------------------------
def load_team_directory():
    """Load team directory with proper matching for your structure."""
    if not TEAM_FILE.exists():
        print(f"⚠️ Team directory not found: {TEAM_FILE}")
        return {}
    
    try:
        df = pd.read_excel(TEAM_FILE, engine='openpyxl')
        print(f"✅ Loaded team directory with {len(df)} rows")
        
        # Your columns: username, full_name, email
        mapping = {}
        
        for _, row in df.iterrows():
            # Get values
            username = str(row.get('username', '')).strip().lower()
            full_name = str(row.get('full_name', '')).strip()
            email = str(row.get('email', '')).strip().lower()
            
            if not email or '@' not in email:
                continue
            
            # Add mappings
            
            # 1. Username
            if username:
                mapping[username] = email
            
            # 2. Full name
            if full_name:
                mapping[full_name.lower()] = email
                
                # First name only
                first_name = full_name.split()[0].lower() if ' ' in full_name else full_name.lower()
                mapping[first_name] = email
                
                # First name capitalized
                mapping[first_name.capitalize()] = email
        
        print(f"✅ Created {len(mapping)} email mappings")
        return mapping
        
    except Exception as e:
        print(f"❌ Error loading team directory: {e}")
        return {}
        
# -----------------------------
# EMAIL RESOLUTION - WITH MULTI-OWNER SUPPORT
# -----------------------------
def split_owners(owner_string):
    """
    Split owner string into individual owners.
    Handles: "Ajay,Vipin", "Ajay;Vipin", "Ajay & Vipin", "Ajay and Vipin"
    """
    if not owner_string or pd.isna(owner_string):
        return []
    
    owner_str = str(owner_string).strip()
    if not owner_str or owner_str.upper() == "UNASSIGNED":
        return []
    
    # Split by common delimiters
    # Handles: comma, semicolon, ampersand, "and", slash
    split_pattern = r'[,;&/\|]|\band\b'
    owners = re.split(split_pattern, owner_str)
    
    # Clean up each owner name
    cleaned_owners = []
    for owner in owners:
        owner_clean = owner.strip()
        if owner_clean and owner_clean.upper() != "UNASSIGNED":
            cleaned_owners.append(owner_clean)
    
    return cleaned_owners

def resolve_single_owner_email(owner_name: str, team_map: dict) -> str | None:
    """
    Resolve a single owner name to email.
    """
    if not owner_name:
        return None
    
    owner_clean = owner_name.strip().lower()
    
    # Try team map first
    # 1. Exact match (lowercase)
    if owner_clean in team_map:
        return team_map[owner_clean]
    
    # 2. Try first name (if owner has multiple parts)
    first_name = owner_clean.split()[0] if ' ' in owner_clean else owner_clean
    if first_name in team_map:
        return team_map[first_name]
    
    # 3. Try capitalized first name
    first_name_cap = first_name.capitalize()
    if first_name_cap in team_map:
        return team_map[first_name_cap]
    
    # 4. Try HARDCODED_EMAILS from config
    if owner_clean in HARDCODED_EMAILS:
        return HARDCODED_EMAILS[owner_clean]
    
    if first_name in HARDCODED_EMAILS:
        return HARDCODED_EMAILS[first_name]
    
    return None

def resolve_owner_emails(owner_string: str, team_map: dict) -> list:
    """
    Resolve multiple owners to their emails.
    Returns list of (owner_name, email) tuples.
    """
    owners = split_owners(owner_string)
    
    results = []
    seen_emails = set()  # Avoid duplicate emails
    
    for owner in owners:
        email = resolve_single_owner_email(owner, team_map)
        if email and email not in seen_emails:
            results.append((owner, email))
            seen_emails.add(email)
    
    return results

# -----------------------------
# DATE HANDLING
# -----------------------------
def safe_parse_date(date_val):
    """Safely parse date from various formats."""
    if pd.isna(date_val) or date_val is None:
        return None
    
    try:
        # Handle string dates
        if isinstance(date_val, str):
            date_val = date_val.strip()
            if not date_val or date_val.lower() in ['', 'nan', 'nat', 'null', 'none']:
                return None
        
        # Parse using pandas
        parsed = pd.to_datetime(date_val, errors='coerce')
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None

# -----------------------------
# REMINDER LOGIC
# -----------------------------
def should_send_reminder(task, force_first=False):
    """Determine if a reminder should be sent."""
    # Check status
    status = str(task.get('Status', '')).strip().upper()
    valid_statuses = ['OPEN', 'PENDING', 'IN PROGRESS', 'IN_PROGRESS']
    
    # More flexible status checking
    is_active = False
    for valid_status in valid_statuses:
        if valid_status in status:
            is_active = True
            break
    
    if not is_active:
        # Check if it's a completed status
        completed_statuses = ['DONE', 'COMPLETED', 'CLOSED', 'FINISHED', 'RESOLVED', 'DELETED']
        for completed in completed_statuses:
            if completed in status:
                return False, f"status_completed ({status})"
        return False, f"status_inactive ({status})"
    
    # Check owner - now accepts multiple owners
    owner = str(task.get('Owner', '')).strip()
    if not owner or owner.upper() == 'UNASSIGNED':
        return False, "unassigned_owner"
    
    # Get priority
    priority = str(task.get('Priority', 'MEDIUM')).strip().upper()
    freq = REMINDER_FREQUENCY_DAYS.get(priority, 3)
    
    # Check last reminder date
    last_reminder = task.get('Last Reminder Date') or task.get('Last Reminder On')
    last_date = safe_parse_date(last_reminder)
    today = date.today()
    
    # First reminder logic
    if last_date is None:
        # Check created date
        created_date = safe_parse_date(task.get('Created On'))
        if created_date is None or created_date <= today:
            return True, "first_reminder"
        return False, "future_created_date"
    
    # Force first reminder
    if force_first:
        return True, "force_first"
    
    # Regular schedule
    days_since = (today - last_date).days
    if days_since >= freq:
        return True, f"frequency_ok ({days_since}d >= {freq}d)"
    
    return False, f"frequency_not_due ({days_since}d < {freq}d)"

# -----------------------------
# EMAIL SENDING - UPDATED FOR MULTI-OWNER
# -----------------------------
def send_email(to_email, subject, html_body, debug=False):
    """Send email with error handling. If debug is True, just log and return True."""
    if debug:
        print(f"  [DEBUG] Would send email to {to_email}")
        print(f"  [DEBUG] Subject: {subject}")
        return True, None
    
    try:
        cfg = _smtp_config()
    except Exception as e:
        error_msg = f"❌ Failed to get SMTP config: {e}"
        print(error_msg)
        return False, error_msg
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f'{cfg["sender_name"]} <{cfg["sender_email"]}>'
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["smtp_username"], cfg["smtp_password"])
            server.sendmail(cfg["sender_email"], [to_email], msg.as_string())
        
        print(f"✅ Email sent successfully to {to_email}")
        return True, None
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"❌ SMTP Authentication failed: {e}"
        print(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"❌ SMTP error occurred: {e}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Failed to send email to {to_email}: {e}"
        print(error_msg)
        return False, error_msg
        
def build_email_html(task, specific_owner=None):
    """
    Build email HTML.
    If specific_owner is provided, use that name instead of task owner.
    """
    # Use specific owner if provided, otherwise use task owner
    if specific_owner:
        owner_display = specific_owner
    else:
        owner_display = task.get('Owner', 'Owner')
    
    subject = task.get('Subject', 'Task Update Required')
    due_date = task.get('Due Date', 'Not specified')
    priority = task.get('Priority', 'MEDIUM')
    status = task.get('Status', 'OPEN')
    remarks = task.get('Remarks', '')
    
    # If there are multiple owners, mention it in the email
    original_owner = task.get('Owner', '')
    multi_owner_note = ""
    if ',' in str(original_owner) or ';' in str(original_owner):
        multi_owner_note = f"<p><em>Note: This task is also assigned to: {original_owner}</em></p>"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #1f77b4; color: white; padding: 15px; border-radius: 5px;">
                <h2>📧 Task Reminder</h2>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9; border-radius: 5px; margin-top: 10px;">
                <p>Hi <strong>{owner_display}</strong>,</p>
                <p>This is a reminder for your pending task:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Subject</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{subject}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Due Date</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{due_date}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Priority</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{priority}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Status</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{status}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Remarks</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{remarks or 'No remarks'}</td></tr>
                </table>
                
                {multi_owner_note}
                
                <p>Please update the task status or take necessary action.</p>
                <p>Best regards,<br>
                <strong>Follow-up & Reminder Agent</strong><br>
                Koenig Solutions</p>
            </div>
            <div style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                <p>This is an automated reminder. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return f"Task Reminder: {subject}", html

# -----------------------------
# MAIN FUNCTION - WITH MULTI-OWNER SUPPORT
# -----------------------------
def send_reminders(force_first=False, debug=False):
    """Main function to send reminders with multi-owner support."""
    print(f"\n{'='*60}")
    print(f"🚀 Starting reminder process - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    # Check registry exists
    if not REGISTRY_FILE.exists():
        return f"❌ Registry file not found at {REGISTRY_FILE}"
    
    try:
        # Load data
        df = pd.read_excel(REGISTRY_FILE)
        print(f"📊 Loaded {len(df)} tasks from registry")
        
        # Show status distribution
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            print("\n📋 Task Status Distribution:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
        
        # Load team directory
        team_map = load_team_directory()
        print(f"📧 Loaded {len(team_map)} email mappings")
        
        sent_total = 0
        skipped = 0
        reasons = {}
        
        now_str = datetime.now().strftime("%Y-%m-%d")
        
        for idx, row in df.iterrows():
            task = row.to_dict()
            task_id = task.get('task_id', f"Row_{idx}")
            subject = task.get('Subject', 'No Subject')[:50]
            
            print(f"\n--- Processing: {subject} ---")
            
            # Check if should send
            should_send, reason = should_send_reminder(task, force_first)
            
            if not should_send:
                skipped += 1
                reasons[reason] = reasons.get(reason, 0) + 1
                print(f"  ❌ Skipped: {reason}")
                continue
            
            # Get ALL owners and their emails
            owner_string = str(task.get('Owner', '')).strip()
            owner_emails = resolve_owner_emails(owner_string, team_map)
            
            if not owner_emails:
                skipped += 1
                reasons['no_email'] = reasons.get('no_email', 0) + 1
                print(f"  ❌ No email found for owner(s): '{owner_string}'")
                
                # Show debug info
                if debug:
                    owners = split_owners(owner_string)
                    print(f"  🔍 Split owners: {owners}")
                    for owner in owners:
                        email = resolve_single_owner_email(owner, team_map)
                        print(f"    '{owner}' -> {email if email else '❌ Not found'}")
                
                continue
            
            print(f"  👥 Found {len(owner_emails)} owner(s): {[o for o, _ in owner_emails]}")
            
            # Send email to each owner
            emails_sent_for_task = 0
            task_updated = False
            
            for owner_name, email in owner_emails:
                try:
                    # Build email with specific owner name
                    subject_line, html = build_email_html(task, specific_owner=owner_name)
                    
                    if debug:
                        print(f"  ✅ Would send to {email}")
                        print(f"  Subject: {mail_subject}")
                        success = True  # Pretend success in debug mode
                        error_msg = None
                else:
                    success, error_msg = send_email(email, mail_subject, html)
                    else:
                        success = send_email(email, subject_line, html)
                    
                    if success:
                        emails_sent_for_task += 1
                        sent_total += 1
                        print(f"    ✅ Sent to {owner_name} <{email}>")
                    else:
                        reasons['send_error'] = reasons.get('send_error', 0) + 1
                        print(f"    ❌ Failed to send to {owner_name} <{email}>")
                        
                except Exception as e:
                    reasons['error'] = reasons.get('error', 0) + 1
                    print(f"    ❌ Error sending to {owner_name}: {e}")
            
            # Update task reminder date if at least one email was sent
            if emails_sent_for_task > 0 and not debug:
                df.at[idx, 'Last Reminder Date'] = now_str
                df.at[idx, 'Last Reminder On'] = now_str
                df.at[idx, 'Last Updated'] = now_str
                task_updated = True
                print(f"  ✅ Updated task reminder date")
            
            # Track reasons
            if emails_sent_for_task > 0:
                reasons[reason] = reasons.get(reason, 0) + 1
        
        # Save updates if any emails were sent
        if sent_total > 0 and not debug:
            df.to_excel(REGISTRY_FILE, index=False)
            print(f"\n💾 Updated {len(df[df['Last Reminder Date'] == now_str])} tasks in registry")
        
        # Build summary
        summary = [
            f"## 📊 Reminder Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Tasks Processed:** {len(df)}",
            f"**✅ Total Emails Sent:** {sent_total}",
            f"**⏭️ Tasks Skipped:** {skipped}",
            "",
            "### 📈 Breakdown:",
        ]
        
        for reason, count in sorted(reasons.items()):
            summary.append(f"- {reason}: {count}")
        
        # Add specific advice for common issues
        if 'no_email' in reasons and reasons['no_email'] > 0:
            summary.append(f"\n⚠️ **{reasons['no_email']} tasks had no email mapping**")
            summary.append("**Solution:** Check if owner names match between tasks and team directory")
        
        print(f"\n{'='*60}")
        print(f"✅ Process complete - Emails Sent: {sent_total}, Tasks Skipped: {skipped}")
        print(f"{'='*60}")
        
        return "\n".join(summary)
        
    except Exception as e:
        error_msg = f"❌ Error in reminder process: {str(e)}"
        print(error_msg)
        return error_msg

# -----------------------------
# TEST FUNCTIONS
# -----------------------------
def test_multi_owner():
    """Test multi-owner functionality."""
    print("🧪 Testing multi-owner handling...")
    
    # Test cases
    test_cases = [
        "Ajay,Vipin",
        "Ajay;Vipin",
        "Ajay & Vipin",
        "Ajay and Vipin",
        "Ajay, Vipin, Anurag",
        "Ajay",
        "",
        "UNASSIGNED",
        "Ajay,Vipin,Anurag,Praveen",
    ]
    
    # Load team directory
    team_map = load_team_directory()
    
    for test_str in test_cases:
        print(f"\n📝 Testing: '{test_str}'")
        owners = split_owners(test_str)
        print(f"  Split into: {owners}")
        
        emails = resolve_owner_emails(test_str, team_map)
        if emails:
            print(f"  ✅ Found emails:")
            for owner, email in emails:
                print(f"    {owner} -> {email}")
        else:
            print(f"  ❌ No emails found")

def test_smtp_connection():
    """Test SMTP connection and return result string."""
    cfg = get_env_config()
    
    if not cfg['smtp_username'] or not cfg['smtp_password']:
        return "❌ SMTP credentials missing in .env file"
    
    try:
        server = smtplib.SMTP(cfg['smtp_server'], cfg['smtp_port'], timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(cfg['smtp_username'], cfg['smtp_password'])
        
        # Try to send a test email to ourselves
        test_msg = MIMEMultipart('alternative')
        test_msg['From'] = f"{cfg['sender_name']} <{cfg['sender_email']}>"
        test_msg['To'] = cfg['smtp_username']
        test_msg['Subject'] = "Test email from Follow-up Agent"
        test_msg.attach(MIMEText("<h1>Test Email</h1><p>This is a test to verify SMTP settings.</p>", 'html'))
        
        server.send_message(test_msg)
        server.quit()
        
        return f"✅ SMTP test successful! Test email sent to {cfg['smtp_username']}"
        
    except smtplib.SMTPAuthenticationError as e:
        return f"❌ SMTP Authentication failed: {e}"
    except smtplib.SMTPException as e:
        return f"❌ SMTP error occurred: {e}"
    except Exception as e:
        return f"❌ Failed to test SMTP: {e}"

def fix_missing_mappings():
    """Create a mapping file for missing owners."""
    if not REGISTRY_FILE.exists():
        return "❌ Registry file not found"
    
    if not TEAM_FILE.exists():
        return "❌ Team directory not found"
    
    try:
        # Load data
        tasks_df = pd.read_excel(REGISTRY_FILE)
        team_df = pd.read_excel(TEAM_FILE)
        
        # Get unique active task owners
        active_statuses = ['OPEN', 'PENDING', 'IN PROGRESS']
        active_tasks = tasks_df[tasks_df['Status'].isin(active_statuses)]
        unique_owners = active_tasks['Owner'].dropna().unique()
        
        # Create mapping dictionary from team directory
        team_map = {}
        for _, row in team_df.iterrows():
            full_name = str(row.get('full_name', '')).strip()
            email = str(row.get('email', '')).strip().lower()
            
            if full_name and email:
                # Map by first name
                first_name = full_name.split()[0].lower()
                team_map[first_name] = email
                
                # Map by full name
                team_map[full_name.lower()] = email
        
        # Find missing mappings
        missing = []
        for owner in unique_owners:
            if not isinstance(owner, str):
                continue
                
            owner_clean = owner.strip().lower()
            if not owner_clean or owner_clean == 'unassigned':
                continue
            
            # Split multi-owners
            import re
            parts = re.split(r'[,;&]', owner_clean)
            
            for part in parts:
                part_clean = part.strip()
                if not part_clean:
                    continue
                
                # Check if owner exists in team_map
                found = False
                for key in team_map.keys():
                    if part_clean in key or key in part_clean:
                        found = True
                        break
                
                if not found and part_clean not in missing:
                    missing.append(part_clean)
        
        # Create fix file
        if missing:
            fix_data = []
            for owner in missing:
                # Try to guess email
                first_part = owner.split()[0].lower() if ' ' in owner else owner.lower()
                suggested_email = f"{first_part}@koenig-solutions.com"
                
                fix_data.append({
                    'task_owner': owner,
                    'suggested_full_name': owner.title(),
                    'suggested_email': suggested_email,
                    'actual_full_name': '',
                    'actual_email': '',
                    'notes': 'Add to Team_Directory.xlsx'
                })
            
            fix_df = pd.DataFrame(fix_data)
            fix_path = DATA_DIR / 'missing_mappings.xlsx'
            fix_df.to_excel(fix_path, index=False)
            
            return f"✅ Created fix file with {len(missing)} missing mappings: {fix_path}"
        else:
            return "✅ All owners have email mappings!"
        
    except Exception as e:
        return f"❌ Error: {e}"

# -----------------------------
# RUN IF EXECUTED DIRECTLY
# -----------------------------
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_multi_owner()
        elif sys.argv[1] == "send":
            result = send_reminders()
            print(result)
        elif sys.argv[1] == "debug":
            result = send_reminders(debug=True)
            print(result)
        else:
            print("Usage: python run_reminders.py [test|send|debug]")
    else:
        # Interactive mode
        print("Reminder System")
        print("1. Test multi-owner handling")
        print("2. Send reminders (debug mode)")
        print("3. Send reminders (actual)")
        choice = input("Select option (1-3): ")
        
        if choice == "1":
            test_multi_owner()
        elif choice == "2":
            result = send_reminders(debug=True)
            print(result)
        elif choice == "3":
            result = send_reminders()
            print(result)
        else:
            print("Invalid choice")
