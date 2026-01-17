import os
from pathlib import Path

class Config:
    """Centralized configuration management."""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Load configuration from various sources."""
        # Try Streamlit secrets first
        try:
            import streamlit as st
            self.SMTP_SERVER = st.secrets.get("SMTP_SERVER", "smtp.office365.com")
            self.SMTP_PORT = int(st.secrets.get("SMTP_PORT", 587))
            self.EMAIL_SENDER = st.secrets.get("EMAIL_SENDER_EMAIL", "")
            self.EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD_ENV_KEY", "")
        except Exception:
            # Fallback to environment variables
            self.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
            self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
            self.EMAIL_SENDER = os.getenv("EMAIL_SENDER_EMAIL", "")
            self.EMAIL_PASSWORD = os.getenv("CEO_AGENT_EMAIL_PASSWORD", "")
        
        # Paths
        self.BASE_DIR = Path(__file__).resolve().parent if '__file__' in globals() else Path(os.getcwd())
        self.DATA_DIR = self.BASE_DIR / "data"
        self.REGISTRY_FILE = self.DATA_DIR / "tasks_registry.xlsx"
        
    def validate(self):
        """Validate required configuration."""
        if not self.EMAIL_PASSWORD:
            raise ValueError("Email password not configured")
        if not self.EMAIL_SENDER:
            raise ValueError("Email sender not configured")

config = Config()
