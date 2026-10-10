from fastapi import APIRouter, Depends, HTTPException, status
from ...core.security import get_current_user
from ...core.supabase import supabase_service_role

router = APIRouter()

@router.get("/me", response_model=dict)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    """
    Return the currently authenticated user's information.
    In a full implementation, we would fetch the user's profile from the database
    to get additional information like full_name, role, etc.
    For now, we return the user_id and email from the token.
    """
    user_id = current_user.get("user_id")
    email = current_user.get("email")
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user information in token",
        )
    return {"user_id": user_id, "email": email}

# Admin protected endpoint example (to be expanded)
async def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency to ensure the current user is an admin.
    This implementation fetches the user's profile from the database
    using the service role key to bypass RLS and check the role.
    If Supabase is not configured, it raises an exception indicating
    that admin functionality is unavailable.
    """
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