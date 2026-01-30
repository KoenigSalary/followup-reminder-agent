# fix_utils.py
import pandas as pd
from pathlib import Path
import re

def check_and_fix_missing_owners():
    """Check for missing owners and provide fix."""
    
    registry_path = Path("data/tasks_registry.xlsx")
    team_path = Path("data/Team_Directory.xlsx")
    
    if not registry_path.exists():
        return "❌ Registry file not found"
    
    if not team_path.exists():
        return "❌ Team directory not found"
    
    try:
        # Load data
        tasks_df = pd.read_excel(registry_path)
        team_df = pd.read_excel(team_path)
        
        # Get all task owners (including inactive for mapping)
        all_owners = tasks_df['Owner'].dropna().unique()
        
        # Create team mapping
        team_map = {}
        for _, row in team_df.iterrows():
            username = str(row.get('username', '')).strip().lower()
            full_name = str(row.get('full_name', '')).strip()
            email = str(row.get('email', '')).strip().lower()
            
            if email and '@' in email:
                if username:
                    team_map[username] = email
                if full_name:
                    team_map[full_name.lower()] = email
                    first_name = full_name.split()[0].lower()
                    team_map[first_name] = email
        
        # Check each owner
        missing = []
        for owner in all_owners:
            if not isinstance(owner, str):
                continue
                
            owner_clean = owner.strip()
            if not owner_clean or owner_clean.upper() == 'UNASSIGNED':
                continue
            
            # Split multiple owners
            parts = re.split(r'[,;&]', owner_clean)
            
            for part in parts:
                part_clean = part.strip().lower()
                if not part_clean:
                    continue
                
                # Check if exists
                if part_clean not in team_map:
                    # Check variations
                    found = False
                    for key in team_map.keys():
                        if part_clean in key or key in part_clean:
                            found = True
                            break
                    
                    if not found and part_clean not in missing:
                        missing.append(part_clean)
        
        if missing:
            # Create suggestions
            suggestions = []
            for owner in missing:
                suggestions.append({
                    'Task Owner Name': owner,
                    'Suggested Email': f"{owner.split()[0].lower() if ' ' in owner else owner.lower()}@koenig-solutions.com",
                    'Action': 'Add to Team_Directory.xlsx'
                })
            
            df = pd.DataFrame(suggestions)
            output_path = Path("data/missing_owners_suggestions.xlsx")
            df.to_excel(output_path, index=False)
            
            # Show summary
            summary = [
                f"⚠️ Found {len(missing)} missing owners:",
                "",
                "Missing owners:"
            ]
            for owner in missing:
                summary.append(f"  - {owner}")
            
            summary.append("")
            summary.append(f"📁 Created suggestion file: {output_path}")
            summary.append("💡 Add these to your Team_Directory.xlsx with correct emails")
            
            return "\n".join(summary)
        else:
            return "✅ All owners are mapped in team directory!"
        
    except Exception as e:
        return f"❌ Error: {e}"