with open('streamlit_app.py', 'r') as f:
    content = f.read()

# In Dashboard Analytics, force it to use lowercase 'status'
old_section = '''if menu == "📊 Dashboard Analytics":
    st.title("📊 Task Analytics Dashboard")
    
    # Load data
    df = excel_handler.load_data()'''

new_section = '''if menu == "📊 Dashboard Analytics":
    st.title("📊 Task Analytics Dashboard")
    
    # Load data
    df = excel_handler.load_data()
    
    # 🔧 FORCE: Rename uppercase columns to lowercase
    if 'Status' in df.columns:
        df = df.rename(columns={'Status': 'status'})
    if 'Owner' in df.columns:
        df = df.rename(columns={'Owner': 'owner'})
    if 'Subject' in df.columns:
        df = df.rename(columns={'Subject': 'task_text'})
    if 'Due Date' in df.columns:
        df = df.rename(columns={'Due Date': 'deadline'})'''

content = content.replace(old_section, new_section)

with open('streamlit_app.py', 'w') as f:
    f.write(content)

print("✅ Dashboard will now use lowercase columns")
