"""FastAPI dependencies for authentication and authorization."""
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from core.auth import JWT, JWTPayload
from core.models.user import User


# Required authentication - raises 401 if not authenticated
async def require_auth(jwt: JWTPayload) -> dict:
    """
    Require authentication for an endpoint.
    
    Returns the decoded JWT payload if valid.
    Raises 401 if authentication fails.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: Annotated[dict, Depends(require_auth)]):
            return {"user_id": user.get("sub"), "email": user.get("email")}
    """
    if not jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return jwt


# Optional authentication - returns None if not authenticated
async def optional_auth(jwt: JWTPayload) -> Optional[dict]:
    """
    Optional authentication for an endpoint.
    
    Returns the decoded JWT payload if valid, None otherwise.
    Does not raise exceptions.
    
    Usage:
        @app.get("/maybe-protected")
        async def route(user: Annotated[Optional[dict], Depends(optional_auth)]):
            if user:
                return {"message": f"Hello {user.get('email')}"}
            return {"message": "Hello guest"}
    """
    return jwt if jwt else None


async def get_current_user(jwt: JWTPayload) -> User:
    """
    Get the current authenticated user from the database.
    
    This dependency:
    - Extracts user ID from JWT token
    - Fetches the User object from the database
    - Verifies the user exists and is active
    - Returns the User object for use in controllers
    
    This ensures we don't trust the frontend - we always verify the user
    exists in the database and is active.
    
    Usage:
        @router.post("/chat")
        async def chat(user: CurrentUser, ...):
            # user is the User object from database
            # Use user.id, user.email, etc. safely
            conversation = await create_conversation(user_id=user.id, ...)
    
    Raises:
        HTTPException 401: If user ID is missing, user not found, or user is inactive
    """
    # Extract user ID from JWT (NextAuth typically uses "sub" or "id")
    user_id_str = jwt.get("sub") or jwt.get("id")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    # Convert to int (JWT typically has string IDs)
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: invalid user ID format"
        )
    
    # Fetch user from database
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Verify user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return user


# Type alias for easy use in controllers
CurrentUser = Annotated[User, Depends(get_current_user)]

