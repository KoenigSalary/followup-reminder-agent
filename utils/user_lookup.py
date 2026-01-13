"""
User Lookup Module - Final fixed version
"""
import pandas as pd
from pathlib import Path

# Use correct paths relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up from utils/ to project root
USERS_FILE = BASE_DIR / "data" / "users.xlsx"
TEAM_FILE = BASE_DIR / "data" / "Team_Directory.xlsx"

def find_user_email(name, team_df=None):
    """Find user email by name"""
    try:
        # Try users.xlsx first
        if USERS_FILE.exists():
            df = pd.read_excel(USERS_FILE)
            df.columns = df.columns.str.strip().str.lower()
            
            if 'name' in df.columns and 'email' in df.columns:
                user = df[df['name'].str.lower() == name.lower()]
                if not user.empty:
                    return user.iloc[0]['email']
        
        # Try Team_Directory.xlsx - use passed dataframe or load it
        if team_df is None and TEAM_FILE.exists():
            team_df = pd.read_excel(TEAM_FILE)
        
        if team_df is not None:
            # Normalize column names
            team_df.columns = team_df.columns.str.strip().str.lower()
            
            # Try different name column combinations
            name_cols = ['full_name', 'name', 'employee name', 'full name', 'username']
            email_cols = ['email', 'email address', 'email_address', 'e-mail']
            
            name_col = None
            email_col = None
            
            for col in name_cols:
                if col in team_df.columns:
                    name_col = col
                    break
            
            for col in email_cols:
                if col in team_df.columns:
                    email_col = col
                    break
            
            if name_col and email_col:
                # Try exact match first
                user = team_df[team_df[name_col].str.lower() == name.lower()]
                if not user.empty:
                    return user.iloc[0][email_col]
                
                # Try partial match
                user = team_df[team_df[name_col].str.lower().str.contains(name.lower(), na=False)]
                if not user.empty:
                    return user.iloc[0][email_col]
        
        return None
        
    except Exception as e:
        print(f"   ⚠️  Error finding email for {name}: {e}")
        return None

def find_user_info(name, team_df=None):
    """Find complete user info by name"""
    try:
        # Try users.xlsx first
        if USERS_FILE.exists():
            df = pd.read_excel(USERS_FILE)
            df.columns = df.columns.str.strip().str.lower()
            
            if 'name' in df.columns:
                user = df[df['name'].str.lower() == name.lower()]
                if not user.empty:
                    return user.iloc[0].to_dict()
        
        # Try Team_Directory
        if team_df is None and TEAM_FILE.exists():
            team_df = pd.read_excel(TEAM_FILE)
        
        if team_df is not None:
            team_df.columns = team_df.columns.str.strip().str.lower()
            
            name_cols = ['full_name', 'name', 'employee name', 'full name', 'username']
            name_col = None
            
            for col in name_cols:
                if col in team_df.columns:
                    name_col = col
                    break
            
            if name_col:
                # Try exact match
                user = team_df[team_df[name_col].str.lower() == name.lower()]
                if not user.empty:
                    return user.iloc[0].to_dict()
                
                # Try partial match
                user = team_df[team_df[name_col].str.lower().str.contains(name.lower(), na=False)]
                if not user.empty:
                    return user.iloc[0].to_dict()
        
        return None
        
    except Exception as e:
        print(f"   ⚠️  Error finding user info for {name}: {e}")
        return None

def load_users_dataframe():
    """Load users from file"""
    try:
        if USERS_FILE.exists():
            return pd.read_excel(USERS_FILE)
    except:
        pass
    
    try:
        if TEAM_FILE.exists():
            return pd.read_excel(TEAM_FILE)
    except:
        pass
    
    return pd.DataFrame()
