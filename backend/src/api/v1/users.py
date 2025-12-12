"""
User management API endpoints with improved naming and structured logging.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from sqlmodel import Session
from typing import Optional, Dict, Any
import logging
from src.schemas.user import (
    UpdateProfileRequest,
    CompleteUserProfileResponse,
    UserResponse,
    RiderResponse,
    DriverResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    DriverStatusUpdate,
    DriverStatusResponse
)
from src.core.settings import settings
from src.services.users import UserService
from src.services.auth import AuthService
from src.services.realtime_location import RealtimeLocationService
from src.db.session import get_session
from src.schemas.auth import CurrentUser
from src.models.enums import UserRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["User Management"])




@router.post("/create-profile", response_model=CompleteUserProfileResponse)
async def create_profile(
    role: UserRole = Form(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    taxi_number: Optional[str] = Form(None),
    account_status: Optional[str] = Form(None),
    residence_place: Optional[str] = Form(None),
    id_card_file: Optional[UploadFile] = File(None),
    driver_license_file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
):
    """
    Complete user profile after phone verification.
    
    This endpoint should be called after successful OTP verification
    to create the user's complete profile with role-specific information.
    
    For users creating their first profile, name and email are required.
    For users creating a second profile (different role), name and email 
    will be auto-populated from their existing profile if not provided.
    """
    # Validate phone number
    if not current_user.phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number not found. Please verify your phone first."
        )
    
    logger.info(f"Creating profile for user {current_user.auth_id} with role {role}")
    
    # Prepare role-specific data based on role
    role_specific_data = {}
    
    if role == UserRole.RIDER:
        role_specific_data = await UserService.prepare_rider_data(residence_place)
    elif role == UserRole.DRIVER:
        role_specific_data = await UserService.prepare_driver_data(
            taxi_number, account_status, id_card_file, driver_license_file
        )
    else:
        logger.warning(f"No handler for role: {role}")

    # Create user profile
    result = UserService.create_user_profile(
        session=session,
        auth_id=current_user.auth_id,
        name=name,
        email=email,
        phone_number=current_user.phone,
        role=role,
        role_specific_data=role_specific_data or None
    )
    
    if not result["success"]:
        logger.error(f"Profile creation failed: {result['message']}")
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    logger.info(f"Profile created successfully for user {current_user.auth_id}")
    
    # Build response
    user = result["user"]
    role_profile = result.get("role_profile")
    role_profile_dict = UserService.build_role_profile_dict(user, role_profile)
    
    user_response = UserResponse(
        id=user.id,
        auth_id=user.auth_id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        auth_status=user.auth_status,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat() if user.updated_at else None
    )
    
    return CompleteUserProfileResponse(
        success=True,
        message="Profile completed successfully",
        user=user_response,
        role_profile=role_profile_dict
    )


@router.get("/get-profile", response_model=CompleteUserProfileResponse)
async def get_profile(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
):
    """
    Get current user's complete profile.
    
    Returns the user's basic information along with role-specific data.
    """
    # Get user from database
    user = UserService.get_user_by_auth_id(session, current_user.auth_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User profile not found. Please complete your profile first."
        )
    
    # Get complete profile with role data
    result = UserService.get_user_with_role_profile(session, user.id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    user = result["user"]
    role_profile = result.get("role_profile")
    role_profile_dict = UserService.build_role_profile_dict(user, role_profile)
    
    user_response = UserResponse(
        id=user.id,
        auth_id=user.auth_id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        auth_status=user.auth_status,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat() if user.updated_at else None
    )
    
    return CompleteUserProfileResponse(
        success=True,
        message="Profile retrieved successfully",
        user=user_response,
        role_profile=role_profile_dict
    )


@router.get("/existing-profile-data")
async def get_existing_profile_data(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
):
    """
    Get existing profile data (email and name) for auto-population when creating a second profile.
    
    Returns existing email and name if user has any profile, null values if first-time user.
    """
    existing_data = UserService.get_existing_profile_data(session, current_user.auth_id)
    
    if existing_data:
        return {
            "success": True,
            "message": "Existing profile data found",
            "data": existing_data
        }
    else:
        return {
            "success": True,
            "message": "No existing profile found",
            "data": {"email": None, "name": None}
        }


@router.post("/update-profile", response_model=CompleteUserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
):
    """
    Update user profile - Simplified General API.
    
    - name/email: Updates across ALL profiles for this user
    - residence_place: Updates only the rider profile (if exists)
    - Driver-specific fields (id_card, driver_license, taxi_number, account_status): NOT ALLOWED for security
    
    No need to specify 'acting_as' - this is a general account-wide update API.
    """
    logger.info(f"Update profile request for user: {current_user.auth_id}")
    
    # Get all user profiles for this auth_id
    user_profiles = UserService.get_user_profiles_by_auth_id(session, current_user.auth_id)
    if not user_profiles:
        raise HTTPException(
            status_code=404,
            detail="User profile not found"
        )
    
    # Handle shared data updates (name, email) - propagate across ALL profiles
    shared_data = {}
    if request.name:
        shared_data["name"] = request.name
        logger.info(f"Will update name to: {request.name} across all profiles")
    if request.email:
        shared_data["email"] = request.email
        logger.info(f"Will update email to: {request.email} across all profiles")
    
    # Update shared data across all profiles if any shared fields are being updated
    if shared_data:
        shared_result = UserService.update_shared_data_across_profiles(
            session, current_user.auth_id, shared_data
        )
        if not shared_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=shared_result["message"]
            )
        logger.info(f"Shared data updated: {shared_result['message']}")
    
    # Handle residence_place update (rider-specific)
    rider_profile = None
    if request.role_specific_data and "residence_place" in request.role_specific_data:
        # Find rider profile to update residence_place
        for user in user_profiles:
            if user.role == "rider":
                rider_profile = user
                break
        
        if rider_profile:
            # Update only residence_place
            rider_data = {"residence_place": request.role_specific_data["residence_place"]}
            result = UserService.update_user_profile(
                session=session,
                user_id=rider_profile.id,
                user_data={},  # Shared data already updated above
                role_data=rider_data
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail=result["message"]
                )
            logger.info(f"Rider residence_place updated: {rider_data}")
        else:
            logger.warning("residence_place update requested but no rider profile found")
    
    # Check for any restricted fields
    if request.role_specific_data:
        restricted_fields = {"id_card", "driver_license", "taxi_number", "account_status"}
        requested_fields = set(request.role_specific_data.keys())
        invalid_fields = requested_fields.intersection(restricted_fields)
        
        if invalid_fields:
            logger.warning(f"Attempted to update restricted fields: {invalid_fields}")
            raise HTTPException(
                status_code=403,
                detail=f"These fields cannot be updated for security reasons: {', '.join(invalid_fields)}. Contact support to modify driver-specific data."
            )
        
        # Check for unknown fields (not residence_place)
        allowed_fields = {"residence_place"}
        unknown_fields = requested_fields - allowed_fields - restricted_fields
        if unknown_fields:
            logger.warning(f"Unknown fields in request: {unknown_fields}")
            raise HTTPException(
                status_code=400,
                detail=f"Unknown fields: {', '.join(unknown_fields)}. Only 'residence_place' is allowed in role_specific_data."
            )
    
    # Get any profile for response (prefer rider if exists, otherwise first profile)
    response_user = rider_profile if rider_profile else user_profiles[0]
    profile_result = UserService.get_user_with_role_profile(session, response_user.id)
    
    user = profile_result["user"]
    role_profile = profile_result.get("role_profile")
    role_profile_dict = UserService.build_role_profile_dict(user, role_profile)
    
    user_response = UserResponse(
        id=user.id,
        auth_id=user.auth_id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        auth_status=user.auth_status,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat() if user.updated_at else None
    )
    
    return CompleteUserProfileResponse(
        success=True,
        message="Profile updated successfully. Shared data (name/email) updated across all profiles.",
        user=user_response,
        role_profile=role_profile_dict
    )


@router.get("/get-profiles")
async def get_user_profiles(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
):
    """
    Get all profiles (rider and driver) for the current user.
    
    This endpoint returns all profiles associated with the user's phone number.
    A user can have maximum 2 profiles: one rider and one driver.
    """
    result = UserService.get_all_user_profiles_with_data(
        session=session,
        auth_id=current_user.auth_id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    total_profiles = result.get("total_profiles", 0)
    
    return {
        "success": True,
        "profiles": result["profiles"],
        "total_profiles": total_profiles,
        "message": f"Found {total_profiles} profile(s)"
    }


# ====================================
@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: PasswordResetRequest,
    session: Session = Depends(get_session)
):
    """
    Reset user password using phone number.
    
    This endpoint:
    1. Takes a phone number from the request
    2. Looks up the email address from the users table (shared field between profiles)
    3. Triggers Supabase's built-in password reset functionality
    4. Sends reset email to the found email address
    
    Note: Email is stored in our users table as a shared field between rider/driver profiles,
    not in Supabase's auth table, so we need to retrieve it first.
    """
    logger.info(f"Password reset requested for phone: {request.phone_number}")
    
    # Look up email by phone number from our users table
    email = UserService.get_email_by_phone(session, request.phone_number)
    
    if not email:
        logger.warning(f"No email found for phone number: {request.phone_number}")
        raise HTTPException(
            status_code=404,
            detail="No account found with this phone number"
        )
    
    # Trigger password reset using enhanced method that handles auth table issues
    result = AuthService.reset_password_with_fallback(email)
    
    if not result["success"]:
        logger.error(f"Password reset failed: {result['message']}")
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    logger.info(f"Password reset email sent successfully to: {email}")
    return PasswordResetResponse(
        success=True,
        message="Password reset email sent successfully. Please check your email for instructions."
    )


