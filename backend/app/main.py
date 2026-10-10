from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from .core.security import get_current_user
from .api.routes import health, users, scan, model

app = FastAPI(
    title="URLSniffer API",
    description="Backend API for URLSniffer with Supabase authentication",
    version="0.1.0",
)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS setup
def get_cors_origins():
    origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if origins_env.strip() == "":
        # Development mode - allow all origins
        return ["*"]
    else:
        # Production mode - parse comma-separated origins
        origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
        return origins if origins else ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")
app.include_router(model.router, prefix="/api/v1")