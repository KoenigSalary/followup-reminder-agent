"""
User Lookup Utility
Supports matching by: full_name, username, email, employee_id, department
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "data" / "users.xlsx"
TEAM_FILE = BASE_DIR / "data" / "Team_Directory.xlsx"

class UserLookup:
    def __init__(self):
        """Initialize with users.xlsx as primary source"""
        try:
            self.users_df = pd.read_excel(USERS_FILE)
            print(f"✅ Loaded {len(self.users_df)} users from users.xlsx")
        except Exception as e:
            print(f"⚠️  Could not load users.xlsx: {e}")
            # Fallback to Team_Directory
            try:
                team_df = pd.read_excel(TEAM_FILE)
                # Convert Team_Directory format to users format
                self.users_df = pd.DataFrame({
                    'username': team_df.get('Name', team_df.get('username', [])),
                    'full_name': team_df.get('Name', []),
                    'email': team_df.get('Email', []),
                    'department': ['Unknown'] * len(team_df),
                    'employee_id': ['N/A'] * len(team_df)
                })
                print(f"⚠️  Fallback: Loaded {len(self.users_df)} from Team_Directory")
            except Exception as e2:
                print(f"❌ Could not load any user directory: {e2}")
                self.users_df = pd.DataFrame()
    
    def find_user(self, search_term: str) -> Optional[Dict]:
        """
        Find user by any identifier: full_name, username, email, employee_id
        
        Returns dict with: username, full_name, email, department, employee_id
        """
        if self.users_df.empty:
            return None
        
        search_lower = str(search_term).lower().strip()
        
        # Try 1: Exact username match
        match = self.users_df[self.users_df['username'].str.lower() == search_lower]
        if len(match) > 0:
            return self._format_user(match.iloc[0])
        
        # Try 2: Exact full_name match
        match = self.users_df[self.users_df['full_name'].str.lower() == search_lower]
        if len(match) > 0:
            return self._format_user(match.iloc[0])
        
        # Try 3: Contains in full_name (e.g., "Praveen" matches "Praveen Kumar")
        match = self.users_df[self.users_df['full_name'].str.lower().str.contains(search_lower, na=False)]
        if len(match) > 0:
            return self._format_user(match.iloc[0])
        
        # Try 4: Reverse contains (e.g., "Praveen Kumar" matches "Praveen")
        for idx, row in self.users_df.iterrows():
            full_name = str(row['full_name']).lower()
            if search_lower in full_name or full_name in search_lower:
                return self._format_user(row)
        
        # Try 5: First name match
        search_first = search_lower.split()[0] if ' ' in search_lower else search_lower
        for idx, row in self.users_df.iterrows():
            full_name = str(row['full_name']).lower()
            name_first = full_name.split()[0] if ' ' in full_name else full_name
            if search_first == name_first:
                return self._format_user(row)
        
        # Try 6: Email match
        match = self.users_df[self.users_df['email'].str.lower().str.contains(search_lower, na=False)]
        if len(match) > 0:
            return self._format_user(match.iloc[0])
        
        # Try 7: Employee ID match
        if 'employee_id' in self.users_df.columns:
            match = self.users_df[self.users_df['employee_id'].str.upper() == search_lower.upper()]
            if len(match) > 0:
                return self._format_user(match.iloc[0])
        
        return None
    
    def _format_user(self, row) -> Dict:
        """Format user row to standard dict"""
        return {
            'username': str(row.get('username', '')),
            'full_name': str(row.get('full_name', '')),
            'email': str(row.get('email', '')),
            'department': str(row.get('department', 'Unknown')),
            'employee_id': str(row.get('employee_id', 'N/A'))
        }
    
    def get_email(self, search_term: str) -> Optional[str]:
        """Quick helper to get just the email"""
        user = self.find_user(search_term)
        return user['email'] if user else None
    
    def get_by_department(self, department: str) -> list:
        """Get all users in a department"""
        if self.users_df.empty:
            return []
        
        dept_lower = department.lower()
        matches = self.users_df[self.users_df['department'].str.lower() == dept_lower]
        
        return [self._format_user(row) for _, row in matches.iterrows()]

# Global instance
_user_lookup = None

def get_user_lookup() -> UserLookup:
    """Get singleton UserLookup instance"""
    global _user_lookup
    if _user_lookup is None:
        _user_lookup = UserLookup()
    return _user_lookup

# Convenience functions
def find_user_email(name_or_username: str) -> Optional[str]:
    """Find user's email by name or username"""
    return get_user_lookup().get_email(name_or_username)

def find_user_info(name_or_username: str) -> Optional[Dict]:
    """Find complete user info"""
    return get_user_lookup().find_user(name_or_username)

if __name__ == "__main__":
    # Test the lookup
    lookup = UserLookup()
    
    test_names = ["Praveen", "Praveen Kumar", "praveen", "Jatin", "admin"]
    
    print("\n" + "=" * 80)
    print("🧪 USER LOOKUP TEST")
    print("=" * 80)
    
    for name in test_names:
        user = lookup.find_user(name)
        if user:
            print(f"\n✅ '{name}' found:")
            print(f"   Full Name: {user['full_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Dept: {user['department']}")
            print(f"   Emp ID: {user['employee_id']}")
        else:
            print(f"\n❌ '{name}' NOT FOUND")
