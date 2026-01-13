"""
Auto-Create Users from Team Directory
This script creates user accounts for all employees in the Team Directory
"""

import pandas as pd
from user_manager import UserManager

def auto_create_users_from_team_directory():
    """
    Automatically create user accounts from Team Directory
    """
    
    # Load Team Directory
    team_dir_file = "data/Team_Directory.xlsx"
    users_file = "data/users.xlsx"
    
    try:
        team_df = pd.read_excel(team_dir_file)
    except FileNotFoundError:
        print(f"❌ Team Directory not found at {team_dir_file}")
        return
    
    user_manager = UserManager(users_file)
    
    # Get existing users
    try:
        existing_users_df = pd.read_excel(users_file)
        existing_usernames = set(existing_users_df['username'].tolist())
    except:
        existing_usernames = set()
    
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*70)
    print("AUTO-CREATING USERS FROM TEAM DIRECTORY")
    print("="*70)
    
    for idx, row in team_df.iterrows():
        employee_id = row['Employee_ID']
        full_name = row['Name']
        email = row['Email']
        department = row['Department']
        emp_type = row['Type']
        
        # Skip department entries
        if emp_type == 'Department':
            continue
        
        # Generate username from email (part before @)
        username = email.split('@')[0].split('.')[0].lower()
        
        # Skip if user already exists
        if username in existing_usernames:
            print(f"⏭️  Skipping {full_name} - User '{username}' already exists")
            skipped_count += 1
            continue
        
        # Generate default password (first name + last 4 digits of employee_id)
        first_name = full_name.split()[0].lower()
        emp_digits = ''.join([c for c in employee_id if c.isdigit()])[-4:]
        default_password = f"{first_name}{emp_digits}"
        
        # Determine role based on department/position
        # You can customize this logic
        if 'head' in full_name.lower() or 'manager' in full_name.lower():
            role = 'department_head'
        else:
            role = 'team_member'
        
        # Create user
        success, msg = user_manager.create_user(
            username=username,
            password=default_password,
            full_name=full_name,
            email=email,
            role=role,
            department=department,
            employee_id=employee_id
        )
        
        if success:
            print(f"✅ Created: {full_name}")
            print(f"   Username: {username}")
            print(f"   Password: {default_password}")
            print(f"   Role: {role}")
            print(f"   Department: {department}")
            print()
            created_count += 1
        else:
            print(f"❌ Failed: {full_name} - {msg}")
    
    print("="*70)
    print(f"📊 SUMMARY:")
    print(f"   ✅ Created: {created_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print("="*70)
    
    # Generate credentials file
    if created_count > 0:
        print("\n📋 Generating credentials file...")
        
        users_df = pd.read_excel(users_file)
        
        # Create credentials export
        creds_df = users_df[['username', 'full_name', 'email', 'role', 'department', 'employee_id']].copy()
        creds_df['temp_password'] = '(sent separately)'
        
        creds_file = "data/user_credentials_export.xlsx"
        creds_df.to_excel(creds_file, index=False)
        
        print(f"✅ Credentials exported to: {creds_file}")
        print("\n⚠️  IMPORTANT: Share passwords securely with each user!")
        print("   Recommend: Email individually or use secure password manager")


if __name__ == "__main__":
    auto_create_users_from_team_directory()
