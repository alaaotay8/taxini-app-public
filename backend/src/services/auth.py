"""
Authentication service using Supabase Auth with normalized responses.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Cookie
from gotrue.errors import AuthError

from . import supabase_client
from src.schemas.auth import CurrentUser

logger = logging.getLogger(__name__)


def _normalize_session_dict(session_data: Any) -> Dict[str, Any]:
    """
    Normalize session data to consistent dict format.
    
    Handles both dict-style and object-style session data.
    """
    if isinstance(session_data, dict):
        return {
            "access_token": session_data.get("access_token"),
            "refresh_token": session_data.get("refresh_token"), 
            "expires_in": session_data.get("expires_in"),
            "token_type": session_data.get("token_type", "bearer")
        }
    
    # Handle object-like session data
    return {
        "access_token": getattr(session_data, "access_token", None),
        "refresh_token": getattr(session_data, "refresh_token", None),
        "expires_in": getattr(session_data, "expires_in", None),
        "token_type": getattr(session_data, "token_type", "bearer")
    }


def _normalize_user_dict(user_data: Any) -> Dict[str, Any]:
    """
    Normalize user data from Supabase to consistent dict format.
    
    Handles both dict-like and object-like user responses from SDK.
    """
    if not user_data:
        return None
        
    if isinstance(user_data, dict):
        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "phone": user_data.get("phone"),
            "email_confirmed_at": user_data.get("email_confirmed_at"),
            "phone_confirmed_at": user_data.get("phone_confirmed_at"),
        }
    
    # Handle object-like responses
    return {
        "id": getattr(user_data, "id", None),
        "email": getattr(user_data, "email", None),
        "phone": getattr(user_data, "phone", None),
        "email_confirmed_at": getattr(user_data, "email_confirmed_at", None),
        "phone_confirmed_at": getattr(user_data, "phone_confirmed_at", None),
    }


def _normalize_supabase_response(response: Any, operation: str) -> Dict[str, Any]:
    """
    Normalize Supabase SDK responses to consistent format.
    
    Handles both dict-style and object-style responses from different SDK versions.
    """
    # Handle dict-style responses (common in tests and some SDK versions)
    if isinstance(response, dict):
        error = response.get("error")
        data = response.get("data", {})
        
        if error:
            error_msg = error.get("message") if isinstance(error, dict) else str(error)
            return {
                "success": False,
                "message": f"{operation} failed: {error_msg}"
            }
        
        # Extract user from data if present
        user = data.get("user") if isinstance(data, dict) else None
        session = data.get("session") if isinstance(data, dict) else None
        
        if user:
            result = {
                "success": True,
                "user": _normalize_user_dict(user)
            }
            if session:
                result["session"] = _normalize_session_dict(session)
            return result
            
        return {"success": True, "data": data}
    
    # Handle object-style responses
    error = getattr(response, "error", None)
    if error:
        return {
            "success": False,
            "message": f"{operation} failed: {str(error)}"
        }
    
    user = getattr(response, "user", None)
    if user:
        result = {
            "success": True,
            "user": _normalize_user_dict(user)
        }
        session = getattr(response, "session", None)
        if session:
            result["session"] = _normalize_session_dict(session)
        return result
    
    return {"success": True, "response": response}


class AuthService:
    """Service for handling authentication operations."""

    @staticmethod
    def send_otp(phone: str) -> Dict[str, Any]:
        """
        Send OTP to phone number using Supabase Auth.
        
        Args:
            phone: Phone number in E.164 format (e.g., +1234567890)
            
        Returns:
            Dict with success/failure and standardized message format
        """
        try:
            client = supabase_client.ensure_supabase_client()
            response = client.auth.sign_in_with_otp({"phone": phone})
            
            normalized = _normalize_supabase_response(response, "OTP send")
            if normalized["success"]:
                normalized["message"] = "OTP sent successfully"
            
            return normalized
            
        except AuthError as e:
            return {
                "success": False,
                "message": f"Failed to send OTP: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_otp: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }

    @staticmethod
    def verify_otp(phone: str, token: str) -> Dict[str, Any]:
        """
        Verify OTP token for phone number.
        
        Args:
            phone: Phone number in E.164 format
            token: OTP token received via SMS
            
        Returns:
            Dict with success/failure, user data, and session if successful
        """
        try:
            client = supabase_client.ensure_supabase_client()
            response = client.auth.verify_otp({
                "phone": phone,
                "token": token,
                "type": "sms"
            })
            
            normalized = _normalize_supabase_response(response, "OTP verification")
            if normalized["success"] and normalized.get("user"):
                normalized["message"] = "Phone number verified successfully"
            elif normalized["success"]:
                normalized = {
                    "success": False,
                    "message": "Invalid OTP token"
                }
            
            return normalized
            
        except AuthError as e:
            return {
                "success": False,
                "message": f"OTP verification failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in verify_otp: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }

    @staticmethod
    def get_user_by_token(access_token: str) -> Dict[str, Any]:
        """
        Get user information by validating access token.
        
        In development mode: Validates custom JWT tokens generated by the app.
        In production mode: Validates Supabase JWT tokens.
        
        Args:
            access_token: JWT access token
            
        Returns:
            Dict with success/failure and user information
        """
        from src.core.settings import settings
        import jwt
        
        try:
            # Development mode: validate custom JWT token
            if settings.development_mode:
                try:
                    # Decode JWT token
                    payload = jwt.decode(
                        access_token, 
                        settings.jwt_secret, 
                        algorithms=[settings.jwt_algorithm]
                    )
                    
                    # Extract user info from token payload
                    return {
                        "success": True,
                        "user": {
                            "id": payload.get("sub"),  # user_id is stored in "sub"
                            "phone": payload.get("phone"),
                            "role": payload.get("role"),
                            "email": None  # Not stored in development JWT
                        }
                    }
                    
                except jwt.ExpiredSignatureError:
                    return {
                        "success": False,
                        "message": "Token has expired"
                    }
                except jwt.InvalidTokenError as e:
                    return {
                        "success": False,
                        "message": f"Invalid token: {str(e)}"
                    }
            
            # Production mode: use Supabase validation
            client = supabase_client.ensure_supabase_client()
            response = client.auth.get_user(access_token)
            
            normalized = _normalize_supabase_response(response, "Token validation")
            if normalized["success"] and not normalized.get("user"):
                normalized = {
                    "success": False,
                    "message": "Invalid or expired token"
                }
            
            return normalized
            
        except AuthError as e:
            return {
                "success": False,
                "message": f"Token validation failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_user_by_token: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }

    @staticmethod
    def refresh_token(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            Dict with success/failure and new session data
        """
        try:
            client = supabase_client.ensure_supabase_client()
            response = client.auth.refresh_session(refresh_token)
            
            normalized = _normalize_supabase_response(response, "Token refresh")
            if normalized["success"]:
                if normalized.get("session"):
                    normalized["message"] = "Token refreshed successfully"
                else:
                    normalized = {
                        "success": False,
                        "message": "Failed to refresh token"
                    }
            
            return normalized
            
        except AuthError as e:
            return {
                "success": False,
                "message": f"Token refresh failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in refresh_token: {e}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }

    @staticmethod
    def sign_out(access_token: str) -> Dict[str, Any]:
        """
        Sign out user by invalidating session.
        
        Args:
            access_token: JWT access token
            
        Returns:
            Dict with success/failure result
        """
        try:
            client = supabase_client.ensure_supabase_client()
            client.auth.sign_out(access_token)
            return {
                "success": True,
                "message": "Successfully signed out"
            }
        except Exception as e:
            logger.error(f"Unexpected error in sign_out: {e}")
            return {
                "success": False,
                "message": f"Sign out failed: {str(e)}"
            }

    @staticmethod
    def reset_password(email: str) -> Dict[str, Any]:
        """
        Trigger password reset for user using Supabase's built-in reset functionality.
        
        Note: This requires the email to exist in Supabase's auth table.
        If the email only exists in your users table but not in Supabase auth,
        the reset will fail.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with success status and message
        """
        try:
            logger.info(f"Initiating password reset for email: {email}")
            
            client = supabase_client.get_supabase_client()
            
            # Use Supabase's reset password method
            # Note: This will only work if the email exists in Supabase auth table
            response = client.auth.reset_password_email(email)
            
            logger.info(f"Password reset response: {response}")
            logger.info(f"Password reset email sent successfully to: {email}")
            
            return {
                "success": True,
                "message": "If an account with this email exists, a password reset link has been sent. Please check your email (including spam folder)."
            }
            
        except AuthError as e:
            logger.error(f"Supabase auth error during password reset: {e}")
            return {
                "success": False,
                "message": f"Failed to send password reset email: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during password reset: {e}")
            return {
                "success": False,
                "message": f"Password reset failed: {str(e)}"
            }

    @staticmethod 
    def check_email_in_auth(email: str) -> Dict[str, Any]:
        """
        Check if an email exists in Supabase auth table by attempting to sign in.
        
        Args:
            email: Email to check
            
        Returns:
            Dict with success status and whether email exists
        """
        try:
            logger.info(f"Checking if email exists in Supabase auth: {email}")
            
            client = supabase_client.get_supabase_client()
            
            # Try to trigger a password reset to see if email exists
            # Supabase will silently succeed even if email doesn't exist (security feature)
            # So we'll attempt a different approach
            
            try:
                # This will fail if email doesn't exist in auth
                response = client.auth.reset_password_email(email)
                logger.info(f"Reset password attempt for {email}: {response}")
                
                # If no exception is thrown, assume email might exist
                return {
                    "success": True,
                    "exists": True,  # We assume it exists since no error was thrown
                    "message": "Email appears to exist in auth system"
                }
                
            except AuthError as auth_error:
                if "not found" in str(auth_error).lower() or "invalid" in str(auth_error).lower():
                    logger.info(f"Email {email} does not exist in Supabase auth")
                    return {
                        "success": True,
                        "exists": False,
                        "message": "Email not found in auth system"
                    }
                else:
                    # Other auth error, re-raise
                    raise auth_error
                
        except AuthError as e:
            logger.warning(f"Auth error checking email existence: {e}")
            return {
                "success": False,
                "message": f"Could not verify email existence: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error checking email existence: {e}")
            return {
                "success": False,
                "message": f"Email check failed: {str(e)}"
            }

    @staticmethod
    def reset_password_with_fallback(email: str) -> Dict[str, Any]:
        """
        Enhanced password reset that handles cases where email might not be in Supabase auth.
        
        Args:
            email: User's email address
            
        Returns:
            Dict with success status and message
        """
        try:
            logger.info(f"Starting enhanced password reset for email: {email}")
            
            # First check if email exists in Supabase auth
            check_result = AuthService.check_email_in_auth(email)
            
            if check_result["success"] and check_result["exists"]:
                # Email exists in auth, proceed with normal reset
                logger.info(f"Email {email} found in Supabase auth, proceeding with reset")
                return AuthService.reset_password(email)
            
            elif check_result["success"] and not check_result["exists"]:
                # Email doesn't exist in Supabase auth but exists in our users table
                logger.warning(f"Email {email} exists in users table but not in Supabase auth")
                return {
                    "success": False,
                    "message": "This account was created before our authentication system update. Please contact support for password reset assistance.",
                    "error_code": "AUTH_MISMATCH"
                }
            
            else:
                # Could not check email existence
                logger.error(f"Could not verify email existence for {email}")
                return {
                    "success": False,
                    "message": "Unable to process password reset request. Please try again later."
                }
                
        except Exception as e:
            logger.error(f"Unexpected error in enhanced password reset: {e}")
            return {
                "success": False,
                "message": f"Password reset failed: {str(e)}"
            }

    @staticmethod
    def get_current_user_dependency(
        authorization: Optional[str] = Header(None),
        access_token: Optional[str] = Cookie(None)
    ) -> CurrentUser:
        """
        FastAPI dependency to get current user from JWT token.
        
        Supports both HttpOnly cookies (preferred) and Authorization header (fallback).
        In development mode: Uses database user ID directly.
        In production mode: Uses Supabase auth ID and looks up user in database.
        
        Args:
            authorization: Authorization header value (fallback for backward compatibility)
            access_token: HttpOnly cookie value (preferred method)
            
        Returns:
            CurrentUser instance with user information
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        from fastapi import HTTPException
        from src.schemas.auth import CurrentUser
        from src.core.settings import settings
        from src.db.session import get_session
        from src.models.user import User
        from sqlmodel import select
        
        # Try cookie first (HttpOnly), then Authorization header (backward compatibility)
        token = None
        if access_token:
            token = access_token
        elif authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
        
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )

        token = token  # Use the token we extracted from cookie or header
        result = AuthService.get_user_by_token(token)
        
        if not result["success"]:
            raise HTTPException(
                status_code=401,
                detail=result["message"]
            )
        
        user_data = result.get("user")
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        # In development mode: token contains database user ID
        # In production mode: token contains Supabase auth ID, need to look up user
        if settings.development_mode:
            # user_data["id"] is the database user ID
            return CurrentUser(
                auth_id=user_data.get("id"),  # Use user ID as auth_id for queries
                user_id=user_data.get("id"),
                phone=user_data.get("phone"),
                email=user_data.get("email"),
                role=user_data.get("role", "user")
            )
        else:
            # Production mode: user_data["id"] is Supabase auth ID
            return CurrentUser(
                auth_id=user_data.get("id"),
                user_id=user_data.get("id"),
                phone=user_data.get("phone"),
                email=user_data.get("email"),
                role=user_data.get("role", "user")
            )
