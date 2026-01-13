#!/bin/bash
# Quick Setup Script for Auto Follow-up System

echo "=========================================="
echo "🚀 AUTO FOLLOW-UP SYSTEM SETUP"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo "1️⃣ Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Install schedule library
echo ""
echo "2️⃣ Installing required packages..."
pip3 install schedule --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ schedule library installed${NC}"
else
    echo -e "${YELLOW}⚠️ schedule library may already be installed${NC}"
fi

# Check environment variables
echo ""
echo "3️⃣ Checking environment variables..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
else
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env with:"
    echo "  CEO_AGENT_EMAIL_PASSWORD=your_password"
    echo "  EMAIL_SENDER=your_email@domain.com"
fi

# Test reminder script
echo ""
echo "4️⃣ Testing reminder script..."
if [ -f "run_reminders.py" ]; then
    echo -e "${GREEN}✅ run_reminders.py found${NC}"
else
    echo -e "${RED}❌ run_reminders.py not found${NC}"
    exit 1
fi

# Check Excel files
echo ""
echo "5️⃣ Checking data files..."
if [ -f "data/tasks_registry.xlsx" ]; then
    echo -e "${GREEN}✅ tasks_registry.xlsx found${NC}"
else
    echo -e "${RED}❌ tasks_registry.xlsx not found${NC}"
fi

if [ -f "data/Team_Directory.xlsx" ]; then
    echo -e "${GREEN}✅ Team_Directory.xlsx found${NC}"
else
    echo -e "${RED}❌ Team_Directory.xlsx not found${NC}"
fi

# Setup options
echo ""
echo "=========================================="
echo "📋 SETUP OPTIONS"
echo "=========================================="
echo ""
echo "Choose how to run auto follow-up:"
echo ""
echo "Option 1: Python Scheduler (Recommended)"
echo "  Command: python3 auto_scheduler.py"
echo "  - Runs in foreground"
echo "  - Easy to stop (Ctrl+C)"
echo "  - Good for testing"
echo ""
echo "Option 2: Python Scheduler (Background)"
echo "  Command: nohup python3 auto_scheduler.py > scheduler.log 2>&1 &"
echo "  - Runs in background"
echo "  - Survives terminal close"
echo "  - Check logs: tail -f scheduler.log"
echo "  - Stop: pkill -f auto_scheduler"
echo ""
echo "Option 3: Cron Job (Production)"
echo "  Command: crontab -e"
echo "  Then add:"
echo "  0 9 * * * cd $(pwd) && python3 run_reminders.py >> /tmp/reminders.log 2>&1"
echo "  - Runs even after reboot"
echo "  - Best for production"
echo ""
echo "=========================================="
echo ""

read -p "Do you want to start the scheduler now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting scheduler..."
    echo "📝 Logs will be saved to scheduler.log"
    echo "🛑 Press Ctrl+C to stop"
    echo ""
    python3 auto_scheduler.py
else
    echo ""
    echo "To start manually later, run:"
    echo "  python3 auto_scheduler.py"
    echo ""
fi
