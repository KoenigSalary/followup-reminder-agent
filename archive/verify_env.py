"""
Verify .env Configuration
--------------------------
Check if all required credentials are loaded from .env
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def verify_env():
    """Verify .env file and credentials"""
    
    print("=" * 60)
    print("🔐 VERIFYING .ENV CONFIGURATION")
    print("=" * 60)
    
    # Check if .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        print("\n❌ .env file not found!")
        print("   Expected location: .env")
        print("\n📝 Create .env file with:")
        print("   CEO_AGENT_EMAIL_PASSWORD=your_password_here")
        print("   SMTP_USERNAME=praveen.chaudhary@koenig-solutions.com")
        print("   AGENT_SENDER_NAME=Task Followup Agent")
        return False
    
    print(f"\n✅ .env file found: {env_path.absolute()}")
    
    # Load .env
    load_dotenv()
    print("✅ .env file loaded")
    
    # Check required variables
    print("\n📋 Checking Required Variables:")
    print("-" * 60)
    
    required_vars = {
        "CEO_AGENT_EMAIL_PASSWORD": "Email password for sending notifications",
        "SMTP_USERNAME": "SMTP username (email address)",
        "AGENT_SENDER_NAME": "Sender name for emails"
    }
    
    all_ok = True
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        
        if value:
            # Mask password
            if "PASSWORD" in var_name:
                display_value = "*" * min(len(value), 8)
            else:
                display_value = value
            
            print(f"✅ {var_name}")
            print(f"   Value: {display_value}")
            print(f"   Description: {description}")
        else:
            print(f"❌ {var_name}")
            print(f"   Status: NOT SET")
            print(f"   Description: {description}")
            all_ok = False
        
        print()
    
    print("=" * 60)
    
    if all_ok:
        print("✅ ALL CREDENTIALS CONFIGURED!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("   1. Replace your shoddy_manager.py with the new version")
        print("   2. Run: python3 create_test_task.py")
        print("   3. Run: python3 run_shoddy_check.py")
        print("   4. Check email inbox for shoddy notification")
        print()
        return True
    else:
        print("⚠️  SOME CREDENTIALS MISSING")
        print("=" * 60)
        print("\n📝 Add missing variables to .env file")
        print()
        return False


if __name__ == "__main__":
    verify_env()
