from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """
    Application settings with environment-safe bootstrap.
    
    Supabase configuration is optional at import time to allow tests
    to run without environment variables. Clear errors are raised
    when Supabase functionality is actually needed.
    """
    # Supabase Config (optional at import time)
    supabase_url: Optional[str] = None
    supabase_api_key: Optional[str] = None
    supabase_storage_bucket: Optional[str] = "test"
    
    # Database Config (Supabase PostgreSQL)
    supabase_db_url: Optional[str] = None  # Direct Supabase PostgreSQL connection
    
    # API Security Config
    api_key: Optional[str] = None  # API key for request authentication
    
    # Admin credentials
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None
    admin_name: Optional[str] = None
    admin_phone: Optional[str] = None
    
    # Development mode (bypass SMS OTP for testing)
    development_mode: bool = False
    
    # JWT config - these must be provided in environment variables
    jwt_secret: str
    jwt_algorithm: str
    jwt_expiration_minutes: int
    
    # Security config
    allowed_origins: Optional[str] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60
    
    # Mapbox config
    mapbox_access_token: Optional[str] = None
    
    def get_allowed_origins(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(',')]
  

    class Config:
        env_prefix = "TAXINI_"
        env_file = ".env"
        
    def get_database_url(self) -> str:
        """Get the database URL, preferring supabase_db_url over database_url."""
        if self.supabase_db_url:
            return self.supabase_db_url
        
        raise ValueError("Either TAXINI_SUPABASE_DB_URL must be set")

settings = Settings()
