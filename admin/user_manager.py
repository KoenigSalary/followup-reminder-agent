"""
User Management & Authentication System
Multi-user support with role-based access control
"""

import pandas as pd
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

class UserManager:
    """
    Manages user authentication and access control
    """
    
    def __init__(self, users_file="data/users.xlsx"):
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist"""
        if not Path(self.users_file).exists():
            # Create default admin user
            default_users = [{
                'username': 'admin',
                'password_hash': self._hash_password('admin123'),  # Change this!
                'full_name': 'System Administrator',
                'email': 'admin@koenig-solutions.com',
                'role': 'admin',
                'department': 'ALL',
                'employee_id': 'ADMIN',
                'is_active': True,
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'last_login': None
            }]
            
            df = pd.DataFrame(default_users)
            Path("data").mkdir(exist_ok=True)
            df.to_excel(self.users_file, index=False)
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """
        Authenticate user and return user info
        
        Returns:
            dict: User info if authenticated, None otherwise
        """
        df = pd.read_excel(self.users_file)
        
        user_row = df[df['username'] == username]
        
        if user_row.empty:
            return None
        
        user = user_row.iloc[0]
        
        if not user['is_active']:
            return None
        
        password_hash = self._hash_password(password)
        
        if password_hash == user['password_hash']:
            # Update last login
            df.loc[df['username'] == username, 'last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.to_excel(self.users_file, index=False)
            
            return {
                'username': user['username'],
                'full_name': user['full_name'],
                'email': user['email'],
                'role': user['role'],
                'department': user['department'],
                'employee_id': user['employee_id']
            }
        
        return None
    
    def get_user_permissions(self, user_info):
        """
        Get user permissions based on role
        
        Returns:
            dict: Permissions
        """
        role = user_info['role']
        
        if role == 'admin':
            return {
                'view_all_tasks': True,
                'create_tasks': True,
                'edit_all_tasks': True,
                'delete_tasks': True,
                'manage_users': True,
                'view_all_departments': True,
                'send_reminders': True,
                'view_reports': True,
                'manage_shoddy': True
            }
        
        elif role == 'department_head':
            return {
                'view_all_tasks': False,  # Only their department
                'create_tasks': True,
                'edit_all_tasks': False,  # Only their department
                'delete_tasks': False,
                'manage_users': False,
                'view_all_departments': False,
                'send_reminders': True,  # To their team only
                'view_reports': True,  # Their department only
                'manage_shoddy': False
            }
        
        else:  # team_member
            return {
                'view_all_tasks': False,  # Only their own tasks
                'create_tasks': True,     # ✅ Can create tasks
                'edit_all_tasks': False,  # Only edit their own
                'delete_tasks': False,
                'manage_users': False,    # Only admin can manage users
                'view_all_departments': False,
                'send_reminders': True,   # ✅ Can send reminders
                'view_reports': True,     # ✅ Can view their reports
                'manage_shoddy': True     # ✅ Can use shoddy check
            }
    
    def filter_tasks_by_user(self, df, user_info):
        """
        Filter tasks based on user role and permissions
        
        Args:
            df: Tasks dataframe
            user_info: User information dict
        
        Returns:
            DataFrame: Filtered tasks
        """
        role = user_info['role']
        
        if role == 'admin':
            # Admin sees everything
            return df
        
        elif role == 'department_head':
            # Department head sees their department's tasks
            department = user_info['department']
            
            # Get all employees in this department from Team Directory
            from shoddy_manager import get_employee_info
            
            # Filter tasks where owner is in same department
            # For now, simple filter by department name match
            # You might need more sophisticated logic
            
            return df  # Implement department filtering logic
        
        else:  # team_member
            # Team member sees only their own tasks
            # Match by first name (owner field) or employee_id
            owner_first_name = user_info['full_name'].split()[0]
            
            return df[df['Owner'] == owner_first_name]
    
    def create_user(self, username, password, full_name, email, role, department, employee_id):
        """
        Create a new user
        
        Args:
            username: Login username
            password: Plain text password (will be hashed)
            full_name: Full name
            email: Email address
            role: admin, department_head, or team_member
            department: Department name
            employee_id: Employee ID from Team Directory
        
        Returns:
            bool: Success status
        """
        df = pd.read_excel(self.users_file)
        
        # Check if username already exists
        if username in df['username'].values:
            return False, "Username already exists"
        
        # Create new user
        new_user = {
            'username': username,
            'password_hash': self._hash_password(password),
            'full_name': full_name,
            'email': email,
            'role': role,
            'department': department,
            'employee_id': employee_id,
            'is_active': True,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'last_login': None
        }
        
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        df.to_excel(self.users_file, index=False)
        
        return True, "User created successfully"
    
    def list_users(self):
        """Get list of all users"""
        df = pd.read_excel(self.users_file)
        return df[['username', 'full_name', 'email', 'role', 'department', 'is_active', 'last_login']]
    
    def deactivate_user(self, username):
        """Deactivate a user account"""
        df = pd.read_excel(self.users_file)
        df.loc[df['username'] == username, 'is_active'] = False
        df.to_excel(self.users_file, index=False)
        return True
    
    def activate_user(self, username):
        """Activate a user account"""
        df = pd.read_excel(self.users_file)
        df.loc[df['username'] == username, 'is_active'] = True
        df.to_excel(self.users_file, index=False)
        return True
    
    def change_password(self, username, new_password):
        """Change user password"""
        df = pd.read_excel(self.users_file)
        df.loc[df['username'] == username, 'password_hash'] = self._hash_password(new_password)
        df.to_excel(self.users_file, index=False)
        return True


# Test function
if __name__ == "__main__":
    print("Testing User Management System...")
    
    um = UserManager()
    
    # Test authentication
    user = um.authenticate('admin', 'admin123')
    if user:
        print(f"✅ Authenticated: {user['full_name']}")
        perms = um.get_user_permissions(user)
        print(f"Permissions: {perms}")
    else:
        print("❌ Authentication failed")
    
    # Test user creation
    success, msg = um.create_user(
        username='sarika',
        password='sarika123',
        full_name='Sarika Gupta',
        email='sarika.gupta@koenig-solutions.com',
        role='team_member',
        department='A&F',
        employee_id='EMP3638'
    )
    print(f"\nUser creation: {msg}")
    
    # List users
    print("\n📋 All Users:")
    print(um.list_users())
