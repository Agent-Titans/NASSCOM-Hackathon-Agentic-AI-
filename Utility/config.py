"""
Configuration Management
"""
import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    """Application configuration"""
    
    # LLM Settings
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # System Settings
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    ESCALATION_ENABLED = os.getenv("ESCALATION_ENABLED", "true").lower() == "true"
    MAX_RESOLUTION_STEPS = int(os.getenv("MAX_RESOLUTION_STEPS", "10"))
    
    # Vector Database
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/knowledge_base")
    
    # Categories
    TICKET_CATEGORIES = os.getenv(
        "TICKET_CATEGORIES",
        "Hardware,Software,Network,Security,HR/IT Access,Other"
    ).split(",")
    
    # Departments
    DEPARTMENTS = os.getenv(
        "DEPARTMENTS",
        "Hardware Support,DevOps,Network Team,Security Team,IT Helpdesk"
    ).split(",")
    
    # Streamlit Settings
    STREAMLIT_THEME = "light"
    PAGE_LAYOUT = "wide"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY not set")
        return True


config = Config()
