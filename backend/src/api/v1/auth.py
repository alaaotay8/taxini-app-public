"""
Authentication API endpoints.

Provides REST API for user authentication including OTP sending, verification, and user info.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import logging
from sqlmodel import Session, select

from src.services.auth import AuthService
from src.schemas.auth import CurrentUser
from src.models.user import User
from src.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SendOTPRequest(BaseModel):
    phone_number: str


class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str


@router.post("/send-otp")
async def send_otp(request: SendOTPRequest) -> dict:
    """
    Send OTP to phone number for authentication.
    
    In development mode, bypasses SMS sending and logs OTP to console.
    
    Args:
        request: Request containing phone number
        
    Returns:
        Success response
    """
    from src.core.settings import settings
    
    try:
        # Development mode: bypass SMS sending
        if settings.development_mode:
            logger.info(f"🔓 DEVELOPMENT MODE: OTP = 123456 for phone {request.phone_number}")
            return {
                "success": True,
                "message": "OTP sent successfully (development mode)"
            }
        
        # Production mode: use Supabase SMS
        result = AuthService.send_otp(request.phone_number)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest, response: Response) -> dict:
    """
    Verify OTP code and set HttpOnly authentication cookie.
    
    In development mode, accepts hardcoded OTP "123456".
    
    Args:
        request: Request containing phone number and OTP code
        response: FastAPI Response object to set cookies
        
    Returns:
        User info (token stored in HttpOnly cookie)
    """
    from src.core.settings import settings
    from src.db.session import get_session
    from sqlmodel import select
    from src.models.user import User
    import jwt
    from datetime import datetime, timedelta
    
    try:
        # Development mode: bypass Supabase OTP verification
        if settings.development_mode:
            if request.otp_code != "123456":
                raise HTTPException(status_code=400, detail="Invalid OTP code")
            
            logger.info(f"🔓 DEVELOPMENT MODE: OTP verified for phone {request.phone_number}")
            
            # Get or create user in database
            with next(get_session()) as session:
                user = session.exec(
                    select(User).where(User.phone_number == request.phone_number)
                ).first()
                
                if not user:
                    raise HTTPException(
                        status_code=404, 
                        detail="User not found. Please register first."
                    )
                
                # Generate JWT token
                token_data = {
                    "sub": user.id,
                    "phone": user.phone_number,
                    "role": user.role,
                    "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
                }
                access_token = jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
                
                # Set HttpOnly cookie
                # Development: secure=False, samesite=lax (localhost)
                # Production: secure=True, samesite=none (cross-origin HTTPS)
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=not settings.development_mode,
                    samesite="none" if not settings.development_mode else "lax",
                    max_age=settings.jwt_expiration_minutes * 60
                )
                
                return {
                    "success": True,
                    "message": "Phone number verified successfully",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "phone": user.phone_number,
                        "role": user.role
                    }
                }
        
        # Production mode: use Supabase verification
        result = AuthService.verify_otp(request.phone_number, request.otp_code)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_current_user(
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency),
    session: Session = Depends(get_session)
) -> dict:
    """
    Get current authenticated user information with full profile.
    
    Args:
        current_user: Current authenticated user from dependency
        session: Database session
        
    Returns:
        User information with name and full profile
    """
    try:
        from src.core.settings import settings
        
        # Fetch full user profile from database
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build user response with role-specific data
        user_data = {
            "auth_id": current_user.auth_id,
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone_number,
            "role": user.role,
            "auth_status": user.auth_status
        }
        
        # Add role-specific data (residence for riders)
        if user.role == "rider":
            from src.models.user import Rider
            rider_profile = session.exec(
                select(Rider).where(Rider.user_id == user.id)
            ).first()
            if rider_profile:
                user_data["residence"] = rider_profile.residence_place
                user_data["residence_place"] = rider_profile.residence_place
        
        return {
            "success": True,
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    role: str
    residence_place: Optional[str] = None
    taxi_number: Optional[str] = None


@router.post("/register")
async def register(request: RegisterRequest, response: Response) -> dict:
    """
    Register a new user (rider or driver).
    
    Creates a user account and role-specific profile, then sets HttpOnly cookie.
    In development mode, automatically logs in without OTP verification.
    
    Args:
        request: Registration data including name, email, phone, role, and role-specific fields
        response: FastAPI Response object to set cookies
        
    Returns:
        User info (token stored in HttpOnly cookie)
    """
    from src.core.settings import settings
    from src.db.session import get_session
    from sqlmodel import select
    from src.models.user import User
    import jwt
    from datetime import datetime, timedelta
    import uuid
    
    try:
        # Validate role
        if request.role not in ['rider', 'driver']:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'rider' or 'driver'")
        
        # Validate role-specific fields
        if request.role == 'rider' and not request.residence_place:
            raise HTTPException(status_code=400, detail="Residence place is required for riders")
        if request.role == 'driver' and not request.taxi_number:
            raise HTTPException(status_code=400, detail="Taxi number is required for drivers")
        
        with next(get_session()) as session:
            # Check if user already exists
            existing_user = session.exec(
                select(User).where(
                    (User.phone_number == request.phone) | (User.email == request.email)
                )
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="User with this phone number or email already exists"
                )
            
            # Create user
            user = User(
                id=str(uuid.uuid4()),
                name=request.name,
                email=request.email,
                phone_number=request.phone,
                role=request.role,
                auth_id=str(uuid.uuid4()),  # Generate dummy auth_id for development mode
                auth_status="verified"  # Skip verification in development
            )
            session.add(user)
            
            # Create role-specific profile
            if request.role == 'rider':
                from src.models.user import Rider
                rider = Rider(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    residence_place=request.residence_place
                )
                session.add(rider)
            else:  # driver
                from src.models.user import Driver, DriverAccountStatus
                driver = Driver(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    taxi_number=request.taxi_number,
                    account_status=DriverAccountStatus.LOCKED
                )
                session.add(driver)
            
            session.commit()
            session.refresh(user)
            
            logger.info(f"✅ New {request.role} registered: {user.name} ({user.phone_number})")
            
            # Generate JWT token for immediate login
            token_data = {
                "sub": user.id,
                "phone": user.phone_number,
                "role": user.role,
                "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
            }
            access_token = jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
            
            # Set HttpOnly cookie
            # Development: secure=False, samesite=lax (localhost)
            # Production: secure=True, samesite=none (cross-origin HTTPS)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=not settings.development_mode,
                samesite="none" if not settings.development_mode else "lax",
                max_age=settings.jwt_expiration_minutes * 60
            )
            
            return {
                "success": True,
                "message": "Registration successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone_number,
                    "role": user.role
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(response: Response) -> dict:
    """
    Logout user by clearing the HttpOnly authentication cookie.
    
    Returns:
        Success response
    """
    from src.core.settings import settings
    try:
        # Clear the HttpOnly cookie with matching settings
        response.delete_cookie(
            key="access_token",
            samesite="none" if not settings.development_mode else "lax"
        )
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error(f"Failed to logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
