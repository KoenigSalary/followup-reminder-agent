#!/usr/bin/env python3
"""
Auto Follow-up Scheduler
Automatically runs reminder system at scheduled intervals

Usage:
    python3 auto_scheduler.py

Features:
    - Runs run_reminders.py on schedule
    - Configurable timing (daily, hourly, custom)
    - Logging and error handling
    - Graceful shutdown
"""

import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
REMINDER_SCRIPT = BASE_DIR / "run_reminders.py"
EMAIL_PROCESSOR = BASE_DIR / "process_emails.py"

def run_command(script_path, name):
    """Execute a Python script"""
    logger.info(f"⏰ Running {name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Log output
        if result.stdout:
            logger.info(result.stdout)
        
        # Check result
        if result.returncode == 0:
            logger.info(f"✅ {name} completed successfully")
        else:
            logger.error(f"❌ {name} failed with code {result.returncode}")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ {name} timed out after 5 minutes")
    except Exception as e:
        logger.error(f"❌ Failed to run {name}: {e}")
    
    logger.info("=" * 60)

def run_reminders():
    """Execute reminder script"""
    run_command(REMINDER_SCRIPT, "Task Reminders")

def process_emails():
    """Execute email processor"""
    run_command(EMAIL_PROCESSOR, "Email Processor")

def main():
    """Main scheduler loop"""
    print("=" * 80)
    print("🚀 AUTO FOLLOW-UP SCHEDULER")
    print("=" * 80)
    
    # ============================================================
    # SCHEDULE CONFIGURATION
    # ============================================================
    
    # Option 1: Daily at 9 AM (Recommended for production)
    schedule.every().day.at("09:00").do(run_reminders)
    logger.info("📅 Scheduled: Task reminders daily at 9:00 AM")
    
    # Option 2: Every 4 hours during work hours
    # for hour in [9, 13, 17]:
    #     schedule.every().day.at(f"{hour:02d}:00").do(run_reminders)
    # logger.info("📅 Scheduled: Task reminders at 9 AM, 1 PM, 5 PM")
    
    # Option 3: Every 2 hours (aggressive)
    # schedule.every(2).hours.do(run_reminders)
    # logger.info("📅 Scheduled: Task reminders every 2 hours")
    
    # Email processing (check replies every 30 minutes)
    # schedule.every(30).minutes.do(process_emails)
    # logger.info("📅 Scheduled: Email processing every 30 minutes")
    
    # ============================================================
    
    print("\n📊 Current Schedule:")
    for job in schedule.get_jobs():
        print(f"   • {job}")
    
    print("\n✅ Scheduler is running...")
    print("📝 Logs: scheduler.log")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("🛑 Scheduler stopped by user")
        print("=" * 80)
        sys.exit(0)

if __name__ == "__main__":
    # Check if reminder script exists
    if not REMINDER_SCRIPT.exists():
        logger.error(f"❌ Reminder script not found: {REMINDER_SCRIPT}")
        logger.error("Please make sure run_reminders.py is in the same directory")
        sys.exit(1)
    
    main()
