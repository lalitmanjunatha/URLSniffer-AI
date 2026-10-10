import os
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the backend root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client for user-level operations (uses anon key, respects RLS)
supabase_anon: Client = None
# Client for privileged operations (uses service role key, bypasses RLS)
supabase_service_role: Client = None

if SUPABASE_URL and SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        supabase_service_role = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print(f"Warning: Failed to create Supabase client: {e}")
        supabase_anon = None
        supabase_service_role = None
else:
    print("Warning: Supabase environment variables not set. Supabase clients are disabled.")