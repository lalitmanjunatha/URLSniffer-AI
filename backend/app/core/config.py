import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the backend root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # For JWT verification we use the Supabase-provided JWKS
    @property
    def SUPABASE_JWKS_URL(self) -> str:
        if self.SUPABASE_URL:
            return f"{self.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        return ""

    # Validate required settings
    def validate(self) -> list[str]:
        """Return list of missing required settings."""
        missing = []
        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not self.SUPABASE_ANON_KEY:
            missing.append("SUPABASE_ANON_KEY")
        return missing

settings = Settings()