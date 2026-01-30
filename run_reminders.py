# run_reminders.py - UPDATED TO USE CONFIG
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, date
import pandas as pd
import numpy as np
from pathlib import Path

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
# =========================================

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
# ENV CONFIG
# -----------------------------
def get_env_config():
    """Get environment variables with fallbacks."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.office365.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", 587)),
        "smtp_username": os.getenv("SMTP_USERNAME", ""),
        "smtp_password": os.getenv("CEO_AGENT_EMAIL_PASSWORD", ""),
        "sender_name": os.getenv("AGENT_SENDER_NAME", "Follow-up Reminder Agent"),
        "sender_email": os.getenv("AGENT_SENDER_EMAIL", os.getenv("SMTP_USERNAME", "")),
    }

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
# EMAIL RESOLUTION - USING CONFIG
# -----------------------------
def resolve_owner_email(owner: str, team_map: dict) -> str | None:
    """
    Resolve owner name to email.
    Uses team_map first, then HARDCODED_EMAILS from config.
    """
    if not owner or pd.isna(owner):
        return None
    
    owner_str = str(owner).strip()
    if not owner_str or owner_str.upper() == "UNASSIGNED":
        return None
    
    # Try team map first
    # 1. Exact match (lowercase)
    if owner_str.lower() in team_map:
        return team_map[owner_str.lower()]
    
    # 2. Try first name
    first_name = owner_str.split()[0].lower() if ' ' in owner_str else owner_str.lower()
    if first_name in team_map:
        return team_map[first_name]
    
    # 3. Try HARDCODED_EMAILS from config
    if owner_str.lower() in HARDCODED_EMAILS:
        return HARDCODED_EMAILS[owner_str.lower()]
    
    if first_name in HARDCODED_EMAILS:
        return HARDCODED_EMAILS[first_name]
    
    print(f"⚠️ No email found for owner: '{owner_str}'")
    return None

def resolve_single_owner(owner_str: str, team_map: dict) -> str | None:
    """Resolve a single owner name to email."""
    
    # Clean the owner string
    owner_clean = owner_str.strip()
    
    # Try different variations
    variations = [
        # Exact match (case insensitive)
        owner_clean.lower(),
        
        # First letter capitalized (common in tasks)
        owner_clean.capitalize(),
        
        # Lowercase
        owner_clean.lower(),
        
        # Remove any trailing dots or special chars
        owner_clean.rstrip('. ').lower(),
        
        # Just first name if there are multiple words
        owner_clean.split()[0].lower() if ' ' in owner_clean else owner_clean.lower(),
        
        # Try with common Indian name variations
        # e.g., "Anurag" might be "Anurag Chauhan" in team directory
        # We'll handle this by checking if any key contains this name
    ]
    
    # Try direct matches first
    for variation in variations:
        if variation in team_map:
            print(f"  ✅ Direct match: '{variation}' -> {team_map[variation]}")
            return team_map[variation]
    
    # Strategy 3: Partial matching
    # Check if any key in team_map contains this owner name
    owner_lower = owner_clean.lower()
    for key in team_map.keys():
        if owner_lower in key.lower() or key.lower() in owner_lower:
            print(f"  ✅ Partial match: '{owner_clean}' found in '{key}' -> {team_map[key]}")
            return team_map[key]
    
    # Strategy 4: Check for common abbreviations
    # e.g., "Dimna" might be short for something
    # This is a fallback - you might want to add specific mappings
    
    print(f"  ❌ No match found for: '{owner_clean}'")
    return None

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
        completed_statuses = ['DONE', 'COMPLETED', 'CLOSED', 'FINISHED', 'RESOLVED']
        for completed in completed_statuses:
            if completed in status:
                return False, f"status_completed ({status})"
        return False, f"status_inactive ({status})"
    
    # Check owner
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
# EMAIL SENDING
# -----------------------------
def send_email(to_email, subject, html_body):
    """Send email with error handling."""
    cfg = get_env_config()
    
    # Validate config
    if not cfg['smtp_username'] or not cfg['smtp_password']:
        print("❌ SMTP credentials missing in .env file")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{cfg['sender_name']} <{cfg['sender_email']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(cfg['smtp_server'], cfg['smtp_port']) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(cfg['smtp_username'], cfg['smtp_password'])
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

def build_email_html(task):
    """Build email HTML."""
    owner = task.get('Owner', 'Owner')
    subject = task.get('Subject', 'Task Update Required')
    due_date = task.get('Due Date', 'Not specified')
    priority = task.get('Priority', 'MEDIUM')
    status = task.get('Status', 'OPEN')
    remarks = task.get('Remarks', '')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #1f77b4; color: white; padding: 15px; border-radius: 5px;">
                <h2>📧 Task Reminder</h2>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9; border-radius: 5px; margin-top: 10px;">
                <p>Hi <strong>{owner}</strong>,</p>
                <p>This is a reminder for your pending task:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Subject</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{subject}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Due Date</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{due_date}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Priority</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{priority}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Status</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{status}</td></tr>
                    <tr><th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Remarks</th><td style="padding: 8px; border-bottom: 1px solid #ddd;">{remarks or 'No remarks'}</td></tr>
                </table>
                
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
# MAIN FUNCTION - WITH BETTER DEBUGGING
# -----------------------------
def send_reminders(force_first=False, debug=False):
    """Main function to send reminders."""
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
        
        # Show sample mappings for debugging
        if debug:
            print("\n🔍 Sample team mappings:")
            for key in ['anurag', 'praveen', 'ajay', 'aditya', 'dimna']:
                if key in team_map:
                    print(f"  {key}: {team_map[key]}")
        
        sent = 0
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
            
            # Get owner email
            owner = str(task.get('Owner', '')).strip()
            email = resolve_owner_email(owner, team_map)
            
            if not email:
                skipped += 1
                reasons['no_email'] = reasons.get('no_email', 0) + 1
                print(f"  ❌ No email for owner '{owner}'")
                
                # Debug: Show what's in team_map for this owner
                if debug:
                    owner_lower = owner.lower()
                    print(f"  🔍 Debug - searching for '{owner_lower}' in team_map:")
                    found = False
                    for key in team_map.keys():
                        if owner_lower in key or key in owner_lower:
                            print(f"    Found similar: '{key}' -> {team_map[key]}")
                            found = True
                    if not found:
                        print(f"    No similar keys found in team_map")
                
                continue
            
            try:
                # Build and send email
                subject_line, html = build_email_html(task)
                
                if debug:
                    print(f"  ✅ Would send to {email}")
                    print(f"  Subject: {subject_line}")
                    success = True  # Pretend success in debug mode
                else:
                    success = send_email(email, subject_line, html)
                
                if success:
                    sent += 1
                    reasons[reason] = reasons.get(reason, 0) + 1
                    
                    # Update registry
                    df.at[idx, 'Last Reminder Date'] = now_str
                    df.at[idx, 'Last Reminder On'] = now_str
                    df.at[idx, 'Last Updated'] = now_str
                    
                    print(f"  ✅ Sent to {email}")
                else:
                    skipped += 1
                    reasons['send_error'] = reasons.get('send_error', 0) + 1
                    print(f"  ❌ Failed to send to {email}")
                    
            except Exception as e:
                skipped += 1
                reasons['error'] = reasons.get('error', 0) + 1
                print(f"  ❌ Error: {e}")
        
        # Save updates
        if sent > 0 and not debug:
            df.to_excel(REGISTRY_FILE, index=False)
            print(f"\n💾 Updated {sent} tasks in registry")
        
        # Build summary
        summary = [
            f"## 📊 Reminder Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Tasks Processed:** {len(df)}",
            f"**✅ Reminders Sent:** {sent}",
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
            
            # List unique owners that failed
            failed_owners = set()
            for idx, row in df.iterrows():
                if pd.isna(row.get('Owner')):
                    continue
                owner = str(row['Owner']).strip()
                if owner and owner.upper() != 'UNASSIGNED':
                    email = resolve_owner_email(owner, team_map)
                    if not email:
                        failed_owners.add(owner)
            
            if failed_owners:
                summary.append("**Owners needing mapping:**")
                for owner in sorted(failed_owners)[:10]:  # Show first 10
                    summary.append(f"  - {owner}")
                if len(failed_owners) > 10:
                    summary.append(f"  ... and {len(failed_owners) - 10} more")
        
        print(f"\n{'='*60}")
        print(f"✅ Process complete - Sent: {sent}, Skipped: {skipped}")
        print(f"{'='*60}")
        
        return "\n".join(summary)
        
    except Exception as e:
        error_msg = f"❌ Error in reminder process: {str(e)}"
        print(error_msg)
        return error_msg

# -----------------------------
# QUICK TEST FUNCTION
# -----------------------------
def test_email_matching():
    """Test email matching with your actual data."""
    print("🧪 Testing email matching with your data...")
    
    # Load team directory
    team_map = load_team_directory()
    
    # Test with common owner names from your tasks
    test_owners = [
        "Anurag",
        "Dimna",
        "Ajay,Vipin",
        "Aditya",
        "Praveen",
        "Rajesh",
        "Amit",
        "Sunil",
        "Sarika",
        "Ritika"
    ]
    
    print("\n🔍 Email Resolution Test:")
    for owner in test_owners:
        email = resolve_owner_email(owner, team_map)
        status = "✅ Found" if email else "❌ Not found"
        print(f"  {owner:15} -> {email if email else 'No email'} {status}")
    
    # Test with actual task owners
    if REGISTRY_FILE.exists():
        df = pd.read_excel(REGISTRY_FILE)
        unique_owners = df['Owner'].dropna().unique()
        
        print(f"\n📋 Actual task owners ({len(unique_owners)} unique):")
        found = 0
        not_found = []
        
        for owner in sorted(unique_owners)[:20]:  # Show first 20
            owner_str = str(owner).strip()
            if not owner_str or owner_str.upper() == 'UNASSIGNED':
                continue
                
            email = resolve_owner_email(owner_str, team_map)
            if email:
                found += 1
                print(f"  ✅ {owner_str:20} -> {email}")
            else:
                not_found.append(owner_str)
                print(f"  ❌ {owner_str:20} -> No email")
        
        print(f"\n📊 Summary: {found} found, {len(not_found)} not found")
        
        if not_found:
            print("\n❌ Owners not found in team directory:")
            for owner in not_found[:10]:
                print(f"  - {owner}")

# -----------------------------
# FIX MISSING MAPPINGS
# -----------------------------
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
            
            # Check if owner exists in team_map
            found = False
            for key in team_map.keys():
                if owner_clean in key or key in owner_clean:
                    found = True
                    break
            
            if not found:
                missing.append(owner)
        
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
            test_email_matching()
        elif sys.argv[1] == "fix":
            result = fix_missing_mappings()
            print(result)
        elif sys.argv[1] == "send":
            result = send_reminders()
            print(result)
        elif sys.argv[1] == "debug":
            result = send_reminders(debug=True)
            print(result)
        else:
            print("Usage: python run_reminders.py [test|fix|send|debug]")
    else:
        # Interactive mode
        print("Reminder System")
        print("1. Test email matching")
        print("2. Fix missing mappings")
        print("3. Send reminders (debug mode)")
        print("4. Send reminders (actual)")
        choice = input("Select option (1-4): ")
        
        if choice == "1":
            test_email_matching()
        elif choice == "2":
            result = fix_missing_mappings()
            print(result)
        elif choice == "3":
            result = send_reminders(debug=True)
            print(result)
        elif choice == "4":
            result = send_reminders()
            print(result)
        else:
            print("Invalid choice")
