"""
User Management UI - Add to streamlit_app.py menu
Only visible to admin role
"""

# Add to sidebar menu (only for admin)
if st.session_state.permissions['manage_users']:
    menu_options.append("👥 User Management")

# Then in the menu section:

elif menu == "👥 User Management":
    st.subheader("👥 User Management")
    
    # Check admin permission
    if not st.session_state.permissions['manage_users']:
        st.error("❌ You don't have permission to manage users")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["📋 All Users", "➕ Add User", "⚙️ Manage Users"])
    
    # ========================================
    # TAB 1: List All Users
    # ========================================
    with tab1:
        st.markdown("### All Registered Users")
        
        users_df = user_manager.list_users()
        
        if not users_df.empty:
            # Style the dataframe
            st.dataframe(
                users_df,
                use_container_width=True,
                column_config={
                    "username": "Username",
                    "full_name": "Full Name",
                    "email": "Email",
                    "role": st.column_config.SelectboxColumn(
                        "Role",
                        options=["admin", "department_head", "team_member"]
                    ),
                    "department": "Department",
                    "is_active": st.column_config.CheckboxColumn("Active"),
                    "last_login": "Last Login"
                }
            )
            
            # Stats
            st.markdown("### 📊 User Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", len(users_df))
            
            with col2:
                active_count = users_df['is_active'].sum()
                st.metric("Active Users", active_count)
            
            with col3:
                admin_count = len(users_df[users_df['role'] == 'admin'])
                st.metric("Admins", admin_count)
            
            with col4:
                dept_heads = len(users_df[users_df['role'] == 'department_head'])
                st.metric("Dept Heads", dept_heads)
        else:
            st.info("No users found")
    
    # ========================================
    # TAB 2: Add New User
    # ========================================
    with tab2:
        st.markdown("### ➕ Create New User")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username *", placeholder="e.g., sarika")
                new_full_name = st.text_input("Full Name *", placeholder="e.g., Sarika Gupta")
                new_email = st.text_input("Email *", placeholder="e.g., sarika.gupta@koenig-solutions.com")
            
            with col2:
                new_password = st.text_input("Password *", type="password", placeholder="Minimum 6 characters")
                new_role = st.selectbox("Role *", ["team_member", "department_head", "admin"])
                new_department = st.selectbox(
                    "Department *",
                    ["A&F", "Operations", "COM EA Team", "HR", "Tax", "Finance", "Accounts", "IT"]
                )
            
            new_employee_id = st.text_input("Employee ID", placeholder="e.g., EMP3638 (leave empty for auto)")
            
            submitted = st.form_submit_button("➕ Create User", use_container_width=True)
            
            if submitted:
                if new_username and new_full_name and new_email and new_password:
                    if len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        # Auto-generate employee_id if not provided
                        if not new_employee_id:
                            # Get next available EMP number
                            from shoddy_manager import get_employee_info
                            import random
                            new_employee_id = f"EMP{random.randint(4000, 9999)}"
                        
                        success, msg = user_manager.create_user(
                            username=new_username,
                            password=new_password,
                            full_name=new_full_name,
                            email=new_email,
                            role=new_role,
                            department=new_department,
                            employee_id=new_employee_id
                        )
                        
                        if success:
                            st.success(f"✅ {msg}")
                            st.info(f"👤 Username: `{new_username}`")
                            st.info(f"🔑 Password: `{new_password}`")
                            st.warning("⚠️ Please share credentials securely with the user")
                        else:
                            st.error(f"❌ {msg}")
                else:
                    st.warning("⚠️ Please fill all required fields")
    
    # ========================================
    # TAB 3: Manage Existing Users
    # ========================================
    with tab3:
        st.markdown("### ⚙️ Manage Existing Users")
        
        users_df = user_manager.list_users()
        
        if not users_df.empty:
            selected_user = st.selectbox(
                "Select User",
                users_df['username'].tolist()
            )
            
            if selected_user:
                user_data = users_df[users_df['username'] == selected_user].iloc[0]
                
                st.markdown(f"**Full Name:** {user_data['full_name']}")
                st.markdown(f"**Email:** {user_data['email']}")
                st.markdown(f"**Role:** {user_data['role']}")
                st.markdown(f"**Department:** {user_data['department']}")
                st.markdown(f"**Status:** {'🟢 Active' if user_data['is_active'] else '🔴 Inactive'}")
                st.markdown(f"**Last Login:** {user_data['last_login'] or 'Never'}")
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if user_data['is_active']:
                        if st.button("🔴 Deactivate User", key="deactivate"):
                            user_manager.deactivate_user(selected_user)
                            st.success(f"User {selected_user} deactivated")
                            st.rerun()
                    else:
                        if st.button("🟢 Activate User", key="activate"):
                            user_manager.activate_user(selected_user)
                            st.success(f"User {selected_user} activated")
                            st.rerun()
                
                with col2:
                    with st.popover("🔑 Reset Password"):
                        new_pwd = st.text_input("New Password", type="password")
                        if st.button("Reset"):
                            if new_pwd and len(new_pwd) >= 6:
                                user_manager.change_password(selected_user, new_pwd)
                                st.success("Password reset successful")
                            else:
                                st.error("Password must be at least 6 characters")
        else:
            st.info("No users to manage")
