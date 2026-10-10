import time
import json
import requests
from functools import lru_cache
from typing import Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# Supabase JWT verification
# Supabase uses RS256 and publishes JWKS at:
# {SUPABASE_URL}/auth/v1/.well-known/jwks.json

# Cache the JWKS for 5 minutes to avoid fetching on every request
@lru_cache(maxsize=1)
def _get_jwks() -> Dict[str, Any]:
    jwks_url = settings.SUPABASE_JWKS_URL
    if not jwks_url:
        raise RuntimeError("SUPABASE_URL is not set")
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch JWKS: {str(e)}")

# Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)

def _get_jwk_key(token: str) -> Dict[str, Any]:
    """Retrieve the appropriate JWK key for the given token."""
    # Get the token header without verification to get the kid
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token header missing kid",
        )

    try:
        jwks = _get_jwks()
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
        )
    except RuntimeError:
        # Re-raise RuntimeError from _get_jwks
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to verify token: {str(e)}",
        )

def verify_token(token: str) -> Dict[str, Any]:
    """Verify the Supabase JWT and return the payload."""
    try:
        jwk_key = _get_jwk_key(token)
        # Construct the public key from the JWK
        # For RS256, we need to convert the JWK to a PEM string or use the raw values.
        # python-jose supports verifying with a JWK dict directly.
        payload = jwt.decode(
            token,
            jwk_key,
            algorithms=["RS256"],
            audience="authenticated",  # Supabase uses this audience
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )
    except RuntimeError:
        # Re-raise RuntimeError from _get_jwks or _get_jwk_key
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to verify token: {str(e)}",
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    Returns a dictionary with user information from the token.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)

    # Return the relevant user information
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        # Note: Supabase JWT doesn't contain role by default.
        # Role should be fetched from the profiles table if needed.
    }

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any] | None:
    """
    Dependency to get the current authenticated user (optional).
    Returns None if not authenticated, otherwise user info.
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
        }
    except (HTTPException, RuntimeError):
        # Return None for any authentication/verification errors
        return None

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure the current user is an admin.
    Fetches the user's profile from the database to check role.
    """
    # Import here to avoid circular dependencies
    from ..core.supabase import supabase_service_role

    if supabase_service_role is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin functionality is not available because Supabase is not configured",
        )

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify user",
        )

    # Fetch the profile using the service role key
    try:
        profile_response = supabase_service_role.table("profiles").select("role").eq("id", user_id).single().execute()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch user profile",
        )

    profile = profile_response.data
    if not profile or profile.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    return current_user

# Optional: dependency to get the user profile from the database
# This would require a database connection and is left for later implementation.
async def get_current_user_profile(user_id: str = Depends(get_current_user)):
    # Placeholder: in a real implementation, you would fetch the profile from the database
    # using the user_id and return the profile.
    # For now, we just return the user_id.
    return {"user_id": user_id.get("user_id") if isinstance(user_id, dict) else user_id}