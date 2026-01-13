"""
Enhanced CSS for Follow-up & Reminder Team
Improved logo alignment and spacing
"""

CUSTOM_CSS = """
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Login Page Styling */
    .login-container {
        max-width: 500px;
        margin: 50px auto;
        padding: 40px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .login-header img {
        display: block;
        margin: 0 auto 25px auto;
        max-width: 350px;
        height: auto;
    }
    
    .login-header h1 {
        font-size: 32px;
        font-weight: 600;
        color: #1f77b4;
        margin: 0;
        line-height: 1.2;
    }
    
    .login-header .subtitle {
        font-size: 18px;
        color: #666;
        margin-top: 10px;
    }
    
    /* Sidebar Logo */
    .sidebar-logo-container {
        text-align: center;
        padding: 15px 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .sidebar-logo-container img {
        max-width: 160px;
        height: auto;
        filter: brightness(0) invert(1);
    }
    
    /* Sidebar Title */
    .sidebar-title {
        text-align: center;
        font-size: 16px;
        font-weight: 600;
        color: #fff;
        margin-top: 10px;
        line-height: 1.3;
    }
    
    /* Main Content Header */
    .page-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
    }
    
    .page-header img {
        height: 50px;
        width: auto;
        filter: brightness(0) invert(1);
    }
    
    .page-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 600;
        color: white;
    }
    
    /* User Welcome */
    .user-welcome {
        background: #f0f7ff;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    .user-welcome strong {
        color: #1f77b4;
    }
    
    /* Navigation Section */
    .nav-section {
        margin: 20px 0;
    }
    
    .nav-section h3 {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* File Uploader */
    .uploadedFile {
        border: 2px dashed #1f77b4;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        border-top: 1px solid #eee;
        margin-top: 30px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .login-header h1 {
            font-size: 24px;
        }
        
        .page-header h1 {
            font-size: 20px;
        }
        
        .page-header img {
            height: 35px;
        }
    }
</style>
"""
