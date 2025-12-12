"""
Admin authentication service using Supabase Auth.
"""

import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, Depends, Header
from gotrue.errors import AuthError

from src.models.user import User, Admin
from src.core.settings import settings
from src.schemas.auth import CurrentUser
from src.services import supabase_client

logger = logging.getLogger(__name__)

def authenticate_admin(session: Session, email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate admin user with email and password using Supabase Auth.
    
    Args:
        session: Database session
        email: Admin email
        password: Admin password
        
    Returns:
        Dict with authentication result
    """
    try:
        # First find the admin user in our database to verify they have admin role
        user = session.exec(
            select(User).where(
                User.email == email,
                User.role == "admin"
            )
        ).first()
        
        if not user:
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        
        # Get admin profile to check password
        admin = session.exec(
            select(Admin).where(Admin.user_id == user.id)
        ).first()
        
        if not admin:
            return {
                "success": False,
                "message": "Admin profile not found"
            }
        
        # Check password with stored value in admin.test_column
        # Use constant-time comparison to prevent timing attacks
        stored_password = admin.test_column if admin.test_column else ""
        if not secrets.compare_digest(stored_password, password):
            return {
                "success": False,
                "message": "Invalid email or password"
            }
            
        # We'll use a simple JWT token approach that doesn't require Supabase auth
        import jwt
        from datetime import datetime, timedelta
        from src.core.settings import settings
        
        # Get JWT settings from application settings
        JWT_SECRET = settings.jwt_secret
        JWT_ALGORITHM = settings.jwt_algorithm
        JWT_EXPIRATION_MINUTES = settings.jwt_expiration_minutes
        
        # Create token payload
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        }
        
        # Generate the token
        try:
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            return {
                "success": True,
                "message": "Login successful",
                "access_token": token,
                "admin_id": user.id,
                "name": user.name,
                "email": user.email
            }
        except Exception as token_error:
            logger.error(f"Failed to generate token: {str(token_error)}")
            return {
                "success": False,
                "message": "Failed to generate authentication token"
            }
    except Exception as e:
        logger.error(f"Admin authentication error: {str(e)}")
        return {
            "success": False,
            "message": f"Authentication error: {str(e)}"
        }


def verify_admin_token(token: str) -> Dict[str, Any]:
    """
    Verify admin JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dict with token verification result
    """
    try:
        import jwt
        from src.core.settings import settings
        
        # Use the same secret as in authenticate_admin
        JWT_SECRET = settings.jwt_secret
        JWT_ALGORITHM = settings.jwt_algorithm
        
        # Decode and verify the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if token is for admin role
        if payload.get("role") != "admin":
            return {
                "success": False,
                "message": "Invalid admin token"
            }
        
        return {
            "success": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email")
        }
        
    except jwt.ExpiredSignatureError:
        return {
            "success": False,
            "message": "Token expired"
        }
    except jwt.InvalidTokenError:
        return {
            "success": False,
            "message": "Invalid token"
        }
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return {
            "success": False,
            "message": f"Token verification error: {str(e)}"
        }


def get_admin_user_dependency(authorization: Optional[str] = Header(None)) -> CurrentUser:
    """
    FastAPI dependency to get admin user from JWT token.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        CurrentUser instance with admin user information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Admin authorization header required"
        )

    token = authorization.replace("Bearer ", "")
    result = verify_admin_token(token)

    if not result["success"]:
        raise HTTPException(
            status_code=401,
            detail=result["message"]
        )

    # Return CurrentUser for compatibility with existing code
    # Make sure we're using the email as auth_id if user_id is not available
    # (since our JWT implementation might store it differently than Supabase)
    auth_id = result.get("user_id") or result.get("email")
    return CurrentUser(
        auth_id=auth_id,
        email=result["email"]
    )
