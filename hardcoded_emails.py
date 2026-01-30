# add_hardcoded_emails.py
import os

def add_hardcoded_emails_to_file():
    """Add HARDCODED_EMAILS to run_reminders.py if missing."""
    
    file_path = "run_reminders.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if HARDCODED_EMAILS already exists
    if "HARDCODED_EMAILS" in content:
        print("✅ HARDCODED_EMAILS already exists in the file")
        return
    
    # Find where to insert (after REMINDER_FREQUENCY_DAYS)
    if "REMINDER_FREQUENCY_DAYS" in content:
        # Split content and insert after REMINDER_FREQUENCY_DAYS definition
        parts = content.split("REMINDER_FREQUENCY_DAYS = {")
        if len(parts) > 1:
            # Find the closing brace of the dictionary
            second_part = parts[1]
            brace_count = 1
            end_index = 0
            
            for i, char in enumerate(second_part):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                
                if brace_count == 0:
                    end_index = i + 1
                    break
            
            if end_index > 0:
                # Insert HARDCODED_EMAILS after the closing brace
                new_content = (
                    parts[0] + 
                    "REMINDER_FREQUENCY_DAYS = {" + 
                    second_part[:end_index] + 
                    "\n\n# Hardcoded fallback emails\nHARDCODED_EMAILS = {\n" +
                    '    "sunil": "sunilkumar.kushwaha@koenig-solutions.com",\n' +
                    '    "praveen": "praveen.chaudhary@koenig-solutions.com",\n' +
                    '    "rajesh": "rajesh@koenig-solutions.com",\n' +
                    '    "amit": "amit@koenig-solutions.com",\n' +
                    '    "anurag": "anurag.chauhan@koenig-solutions.com",\n' +
                    '    "ajay": "ajay.rawat@koenig-solutions.com",\n' +
                    '    "aditya": "aditya.singh@koenig-solutions.com",\n' +
                    '    "dimna": "dimna@koenig-solutions.com",\n' +
                    '    "vipin": "vipin.nautiyal@koenig-solutions.com",\n' +
                    '    "tamanna": "tamanna.alisha@koenig-solutions.com",\n' +
                    '    "nishant": "nishant.yash@koenig-solutions.com",\n' +
                    "}\n" +
                    second_part[end_index:]
                )
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                print("✅ Added HARDCODED_EMAILS to run_reminders.py")
                print("⚠️ Please update the email addresses with actual values!")
                return
    
    print("❌ Could not find appropriate location to add HARDCODED_EMAILS")
    print("💡 Manually add it after REMINDER_FREQUENCY_DAYS dictionary")

if __name__ == "__main__":
    add_hardcoded_emails_to_file()