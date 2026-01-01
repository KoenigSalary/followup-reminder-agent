# CEO Follow-up & Reminder Agent

A comprehensive task management and accountability system with automated reminders and shoddy notifications.

## Features

- 📋 **Task Management** - Track tasks with priorities and deadlines
- ⏰ **Automated Reminders** - Daily reminders at 9:00 AM
- ⚠️ **Shoddy Notifications** - Automatic HR notifications for overdue tasks
- 📊 **Analytics Dashboard** - View task statistics and shoddy logs
- 📧 **Email Integration** - Automated email notifications via Office 365
- 🔄 **Bulk MOM Upload** - Process meeting minutes and extract action items
- 📈 **Priority System** - URGENT, HIGH, MEDIUM, LOW task priorities

## System Architecture

```
Daily Workflow (Automated via Cron):
├─ 9:00 AM: Send task reminders
└─ 9:05 AM: Check overdue tasks & send shoddy notifications
```

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.13
- **Email**: SMTP (Office 365)
- **Storage**: Excel (tasks_registry.xlsx)
- **Authentication**: Microsoft Graph API (Azure)

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/followup-reminder-agent.git
cd followup-reminder-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file:
```env
# Azure (for Microsoft Graph API)
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# SMTP (Office 365)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your_email@koenig-solutions.com
CEO_AGENT_EMAIL_PASSWORD=your_password

# Agent Identity
AGENT_SENDER_NAME=Your Name
AGENT_SENDER_EMAIL=your_email@koenig-solutions.com
APP_TITLE=Follow-up & Reminder Agent
```

4. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub repository with your code
- Streamlit Cloud account (free)

### Steps

1. **Push to GitHub**:
```bash
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository
   - Set main file: `streamlit_app.py`
   - Add secrets in Advanced settings

3. **Configure Secrets**:
In Streamlit Cloud dashboard → Settings → Secrets, add:
```toml
# Azure Credentials
AZURE_TENANT_ID = "your_tenant_id"
AZURE_CLIENT_ID = "your_client_id"
AZURE_CLIENT_SECRET = "your_client_secret"

# SMTP Configuration
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = "587"
SMTP_USERNAME = "your_email@koenig-solutions.com"
CEO_AGENT_EMAIL_PASSWORD = "your_password"

# Agent Identity
AGENT_SENDER_NAME = "Your Name"
AGENT_SENDER_EMAIL = "your_email@koenig-solutions.com"
APP_TITLE = "Follow-up & Reminder Agent"
```

## Project Structure

```
followup-reminder-agent/
├── streamlit_app.py              # Main Streamlit application
├── config.py                     # Configuration settings
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore file
├── README.md                     # This file
├── data/                         # Data directory
│   ├── tasks_registry.xlsx       # Task database
│   ├── auto_reply_sent.xlsx      # Email tracking
│   ├── shoddy_log.xlsx          # Shoddy incident log
│   └── Team_Directory.xlsx       # Team contact info
├── utils/                        # Utility modules
│   ├── excel_handler.py          # Excel operations
│   ├── email_handler.py          # Email utilities
│   └── document_handler.py       # Document processing
├── bulk_mom_processor.py         # MOM parsing logic
├── shoddy_manager.py            # Shoddy notification system
├── reminder_scheduler.py         # Reminder scheduling
├── email_processor.py            # Email processing
├── manual_processor.py           # Manual task entry
├── run_shoddy_check.py          # Shoddy check script
├── run_reminders.py             # Reminder script
└── migrate_columns.py            # Database migration

Cron Jobs (Local only):
├── run_reminders.py              # Daily at 9:00 AM
└── run_shoddy_check.py          # Daily at 9:05 AM
```

## Usage

### Streamlit Interface

1. **📥 View Follow-ups** - View and manage all tasks
2. **📧 Process Emails** - Process incoming emails for action items
3. **⏰ Run Reminder Scheduler** - Manually trigger reminders
4. **✍️ Manual Entry** - Add tasks manually
5. **📄 Bulk MOM Upload** - Upload meeting minutes
6. **📊 Logs / Status** - View system logs and status

### Command Line

```bash
# Run shoddy check manually
python3 run_shoddy_check.py

# Run reminders manually
python3 run_reminders.py

# Migrate database (add new columns)
python3 migrate_columns.py

# Verify environment configuration
python3 verify_env.py

# Create test overdue task
python3 create_test_task.py

# Remove test tasks
python3 remove_test_task.py
```

## Automated Daily Workflow

### Cron Jobs (Local/Server)

Add to crontab (`crontab -e`):

```cron
# Send reminders - Daily at 9:00 AM
0 9 * * * /path/to/venv/bin/python /path/to/run_reminders.py >> /path/to/cron.log 2>&1

# Check overdue tasks - Daily at 9:05 AM
5 9 * * * cd /path/to/followup-reminder-agent && /path/to/venv/bin/python run_shoddy_check.py >> /path/to/shoddy_cron.log 2>&1
```

**Note**: Cron jobs only work on local servers, not on Streamlit Cloud.

## Features in Detail

### Priority System
- **URGENT** - Critical tasks (1 day deadline)
- **HIGH** - Important tasks (3 days deadline)
- **MEDIUM** - Regular tasks (7 days deadline)
- **LOW** - Routine tasks (14 days deadline)

### Shoddy Notification System
When tasks become overdue:
1. System detects overdue tasks daily at 9:05 AM
2. Sends email to hr@koenig-solutions.com
3. Logs incident to shoddy_log.xlsx
4. Tracks days overdue and owner

### Email Template (Shoddy)
```
Subject: ⚠️ Shoddy Marked - [Employee Name]

Dear HR Team,

Please mark shoddy against the following person for missing task deadline:

EMPLOYEE DETAILS
Name: [Employee Name]

TASK DETAILS
Task ID: [Task ID]
Task: [Task Description]
Priority: [Priority Level]
Deadline: [Original Deadline]
Days Overdue: [Number] days

This is an automated notification from the Task Followup System.
```

## Database Schema

### tasks_registry.xlsx
- `task_id` - Unique task identifier
- `meeting_id` - Source meeting identifier
- `owner` - Task assignee
- `task_text` - Task description
- `status` - OPEN/COMPLETED
- `created_on` - Creation timestamp
- `priority` - URGENT/HIGH/MEDIUM/LOW
- `deadline` - Due date
- `completed_date` - Completion timestamp
- `days_taken` - Days to complete
- `performance_rating` - Performance score

### shoddy_log.xlsx
- `date` - Incident timestamp
- `task_id` - Task identifier
- `owner` - Employee name
- `task_text` - Task description
- `priority` - Task priority
- `deadline` - Original deadline
- `days_overdue` - Days past deadline
- `meeting_id` - Source meeting

## Monitoring & Logs

```bash
# View shoddy check logs
tail -f shoddy_cron.log

# View reminder logs
tail -f cron.log

# Check all shoddy incidents
python3 -c "import pandas as pd; print(pd.read_excel('data/shoddy_log.xlsx'))"

# Count shoddy by owner
python3 -c "import pandas as pd; df = pd.read_excel('data/shoddy_log.xlsx'); print(df['owner'].value_counts())"
```

## Troubleshooting

### Email Not Sending
1. Check password in .env or Streamlit secrets
2. Verify SMTP_USERNAME matches your email
3. Test SMTP connection:
```python
import smtplib
server = smtplib.SMTP('smtp.office365.com', 587)
server.starttls()
server.quit()
```

### Missing Columns Error
Run migration:
```bash
python3 migrate_columns.py
```

### Cron Jobs Not Running
1. Check crontab: `crontab -l`
2. Verify paths are absolute
3. Check logs for errors
4. Test manually first

## Security

- Never commit `.env` file to Git
- Use Streamlit secrets for deployment
- Rotate passwords regularly
- Use app-specific passwords for Office 365

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

Proprietary - Koenig Solutions Ltd.

## Support

For issues or questions:
- Email: praveen.chaudhary@koenig-solutions.com
- Internal: Contact IT Department

## Changelog

### Version 1.0.0 (2025-12-31)
- ✅ Initial release
- ✅ Task management with priorities
- ✅ Automated reminders
- ✅ Shoddy notification system
- ✅ Bulk MOM upload
- ✅ Email integration
- ✅ Streamlit UI

## Roadmap

### Future Enhancements
- [ ] Analytics dashboard
- [ ] Performance acknowledgement emails
- [ ] Automatic priority assignment
- [ ] Task delegation workflow
- [ ] Mobile app
- [ ] Slack/Teams integration
- [ ] Advanced reporting

---

**Built with ❤️ by Praveen Chaudhary @ Koenig Solutions**
