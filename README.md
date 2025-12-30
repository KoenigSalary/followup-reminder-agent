Follow-up & Reminder Agent

A lightweight internal automation tool to track follow-ups, MOM action items, and send reminder emails using Outlook 365.
Designed for structured, auditable follow-ups with minimal automation risk.

🚀 What This Agent Does (Q4 Scope)
✅ Core Capabilities

Parse MOM (Minutes of Meeting) emails into structured tasks

Auto-generate Task IDs and Meeting IDs

Track task status (OPEN / COMPLETED)

Send email reminders to task owners (alternate days)

Send polite acknowledgements when configured

Manual task entry via Streamlit UI

Full audit trail via Excel registry

Safe .env-based credential handling

❌ Out of Scope (Planned for Q1)

Auto-reply via Microsoft Graph

AI-based decision making

Inbox auto-monitoring

WhatsApp / Teams integration

Priority auto-escalation

🧠 Design Philosophy

No blind automation

Human-safe defaults

Explicit configuration

Email-first, not AI-first

Auditable over clever

If the agent is unsure → it does NOT act blindly.

📁 Project Structure
followup-reminder-agent/
│
├── assets/
│   └── koenig_logo.png
│
├── data/
│   ├── tasks_registry.xlsx
│   └── Team_Directory.xlsx
│
├── streamlit_app.py          # UI Dashboard
├── reminder_engine.py        # Reminder email logic
├── reminder_scheduler.py     # Scheduling rules
├── email_processor.py        # Email → task parsing
├── mom_parser.py             # MOM parsing logic
├── reply_engine.py           # Polite ACK replies
├── config.py                 # App configuration
├── requirements.txt
├── .env                      # Local secrets (ignored)
├── .gitignore
└── README.md

🛠️ One-Time Setup (New Machine)
git clone https://github.com/KoenigSalary/followup-reminder-agent.git
cd followup-reminder-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

🔐 Environment Setup (MANDATORY)

Create / edit .env in project root:

SMTP_USERNAME=praveen.chaudhary@koenig-solutions.com
CEO_AGENT_EMAIL_PASSWORD=OUTLOOK_APP_PASSWORD
AGENT_SENDER_NAME=Praveen Chaudhary
APP_TITLE=Follow-up & Reminder Agent


⚠️ .env is not committed to GitHub by design.

▶️ Running the App
streamlit run streamlit_app.py


Access via browser:

http://localhost:8501

🧾 How Tasks Are Created
Example MOM Email

Subject

MOM-001


Body

What is the status of Japan Entity formation? @Sarika
What is the status of 10% share transfer to Raahil? @Sunil
How much cost you have saved in Dubai? @Anurag

Result

1 Meeting ID auto-created

3 Tasks auto-generated

Each task routed to correct owner

Task IDs auto-assigned

⏰ Reminder Rules

Reminders are sent on alternate days

One consolidated email per owner

Skipped if last reminder is recent

Stops automatically when task is marked COMPLETED

✉️ Acknowledgement Rules

The agent acknowledges emails ONLY if configured.

Default ACK Template

Thanks for your email.
I’ve noted this and will get back to you shortly.


No auto-reply if:

Email is ambiguous

No task detected

Configuration disabled

🧑‍💼 Team Directory Format

data/Team_Directory.xlsx

Name	Email
Sunil	sunil.kushwaha@koenig-solutions.com

Sarika	sarika.gupta@koenig-solutions.com

Anurag	anurag.chauhan@koenig-solutions.com
✅ Do’s & ❌ Don’ts
✅ Do

Use Outlook App Password

Keep .env local only

Mark tasks completed via UI

Use clear MOM formatting

❌ Don’t

Commit .env

Hardcode passwords

Auto-reply without clarity

Let agent guess intent

🧩 Q1 Roadmap (Planned)

Microsoft Graph inbox monitoring

AI task interpretation

Priority-based escalation

SLA dashboards

Teams / WhatsApp integration

🏁 Status

Q4 Scope: Completed ✅

Production Ready: Yes

Security Review: Passed

GitHub Versioned: Yes

