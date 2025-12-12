"""
Authentication API endpoints.

Provides REST API for user authentication including OTP sending, verification, and user info.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from src.services.auth import AuthService
from src.schemas.auth import CurrentUser

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
async def verify_otp(request: VerifyOTPRequest) -> dict:
    """
    Verify OTP code and return authentication tokens.
    
    In development mode, accepts hardcoded OTP "123456".
    
    Args:
        request: Request containing phone number and OTP code
        
    Returns:
        Authentication tokens and user info
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
                
                return {
                    "success": True,
                    "message": "Phone number verified successfully",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "phone": user.phone_number,
                        "role": user.role
                    },
                    "session": {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "expires_in": settings.jwt_expiration_minutes * 60
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
async def get_current_user(current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)) -> dict:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from dependency
        
    Returns:
        User information
    """
    try:
        return {
            "success": True,
            "user": current_user
        }
        
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
async def register(request: RegisterRequest) -> dict:
    """
    Register a new user (rider or driver).
    
    Creates a user account and role-specific profile, then returns JWT token.
    In development mode, automatically logs in without OTP verification.
    
    Args:
        request: Registration data including name, email, phone, role, and role-specific fields
        
    Returns:
        Authentication tokens and user info
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
            
            return {
                "success": True,
                "message": "Registration successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone_number,
                    "role": user.role
                },
                "session": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": settings.jwt_expiration_minutes * 60
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
