# Follow-up Reminder Agent v2.0

## 🎉 New Features

### Dashboard Analytics
- Key metrics dashboard
- Priority/Status/Owner distribution charts
- Upcoming deadlines with alerts
- Completion rate tracking

### User Lookup System
- Integrated with users.xlsx
- Search by name, username, email, emp ID, department
- Enhanced email context

### Automated Reminders
- Daily cron job (9 AM)
- Priority-based intervals:
  - URGENT: Daily
  - HIGH: Every 2 days
  - MEDIUM: Every 3 days
  - LOW: Every 5 days

## 🚀 Setup

```bash
cat > README_UPDATE.md << 'EOF'
# Follow-up Reminder Agent v2.0

## 🎉 New Features

### Dashboard Analytics
- Key metrics dashboard
- Priority/Status/Owner distribution charts
- Upcoming deadlines with alerts
- Completion rate tracking

### User Lookup System
- Integrated with users.xlsx
- Search by name, username, email, emp ID, department
- Enhanced email context

### Automated Reminders
- Daily cron job (9 AM)
- Priority-based intervals:
  - URGENT: Daily
  - HIGH: Every 2 days
  - MEDIUM: Every 3 days
  - LOW: Every 5 days

## 🚀 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up cron for automated reminders
crontab -e
# Add: 0 9 * * * cd /path/to/project && python3 run_reminders.py >> logs/reminders.log 2>&1

# Run the app
streamlit run streamlit_app.py
📊 Usage
Bulk MOM Upload - Create tasks from meeting notes
Dashboard - View analytics and metrics
View Follow-ups - Manage all tasks
Automated Reminders - Runs daily at 9 AM
