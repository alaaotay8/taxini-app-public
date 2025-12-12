"""
User management service.
"""

from typing import Dict, Any, Optional, List
from sqlmodel import Session, select
from fastapi import UploadFile, HTTPException
import logging
from src.models.user import User, Rider, Driver
from src.models.enums import UserRole
from src.db.session import get_session
from src.core.settings import settings
from src.services.supabase_client import upload_file_to_bucket

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user profiles and operations."""

    @staticmethod
    def create_user_profile(
        session: Session,
        auth_id: str,
        name: Optional[str],
        email: Optional[str],
        phone_number: str,
        role: UserRole,
        role_specific_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete user profile with role-specific data.
        Auto-populates email and name from existing profiles if available.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            name: User's full name (optional if existing profile exists)
            email: User's email address (optional if existing profile exists)
            phone_number: User's phone number
            role: User role (driver, rider, admin)
            role_specific_data: Additional data based on role
            
        Returns:
            Dict containing created user information
        """
        try:
            # Check if user already has this specific role
            existing_user_with_role = session.exec(
                select(User).where(
                    User.auth_id == auth_id,
                    User.role == role.value
                )
            ).first()
            
            if existing_user_with_role:
                role_name = "driver" if role.value == "driver" else "rider"
                return {
                    "success": False,
                    "message": f"This number is already associated with a {role_name} profile",
                    "error": f"DUPLICATE_{role_name.upper()}_PROFILE"
                }
            
            # Check if trying to create admin profile (not allowed for regular users)
            if role.value == "admin":
                return {
                    "success": False,
                    "message": "Admin profiles cannot be created through this endpoint",
                    "error": "ADMIN_PROFILE_NOT_ALLOWED"
                }

            # Auto-populate email and name from existing profile if not provided
            if not name or not email:
                existing_data = UserService.get_existing_profile_data(session, auth_id)
                if existing_data:
                    name = name or existing_data["name"]
                    email = email or existing_data["email"]
                    logger.info(f"Auto-populated profile data for {auth_id}: email={email}, name={name}")
                elif not name or not email:
                    # If no existing profile and missing required data
                    missing_fields = []
                    if not name:
                        missing_fields.append("name")
                    if not email:
                        missing_fields.append("email")
                    return {
                        "success": False,
                        "message": f"Missing required fields: {', '.join(missing_fields)}. These are required for the first profile.",
                        "error": "MISSING_REQUIRED_FIELDS"
                    }

            # Create base user with string values for the database
            user = User(
                auth_id=auth_id,
                name=name,
                email=email,
                phone_number=phone_number,
                role=role.value,  # Use string value directly
                auth_status="verified"  # Use string value directly
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)

            # Create role-specific profile
            role_profile = None
            if role.value == "rider":
                rider_data = role_specific_data or {}
                role_profile = Rider(
                    user_id=user.id,
                    residence_place=rider_data.get("residence_place", "")
                )
                session.add(role_profile)
                
            elif role.value == "driver":
                driver_data = role_specific_data or {}
                role_profile = Driver(
                    user_id=user.id,
                    id_card=driver_data.get("id_card", ""),
                    driver_license=driver_data.get("driver_license", ""),
                    taxi_number=driver_data.get("taxi_number", ""),
                    account_status=driver_data.get("account_status", "locked"),  # Default to locked
                    driver_status=driver_data.get("driver_status", "offline")  # Default to offline
                )
                session.add(role_profile)
                
            elif role.value == "admin":
                admin_data = role_specific_data or {}
                role_profile = Admin(
                    user_id=user.id,
                    test_column=admin_data.get("test_column")
                )
                session.add(role_profile)

            session.commit()
            
            return {
                "success": True,
                "message": "User profile created successfully",
                "user": user,
                "role_profile": role_profile
            }
            
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to create user profile: {str(e)}",
                "error": str(e)
            }

    @staticmethod
    def get_user_by_auth_id(session: Session, auth_id: str) -> Optional[User]:
        """
        Get user by Supabase auth ID.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            
        Returns:
            User object if found, None otherwise
        """
        return session.exec(
            select(User).where(User.auth_id == auth_id)
        ).first()

    @staticmethod
    def get_user_profiles_by_auth_id(session: Session, auth_id: str) -> List[User]:
        """
        Get all user profiles by Supabase auth ID (for multi-role users).
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            
        Returns:
            List of User profiles for this auth_id
        """
        return session.exec(
            select(User).where(User.auth_id == auth_id)
        ).all()

    @staticmethod
    def get_user_by_auth_id_and_role(session: Session, auth_id: str, role: UserRole) -> Optional[User]:
        """
        Get specific user profile by auth ID and role.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            role: User role (rider/driver)
            
        Returns:
            User profile for the specified role, None if not found
        """
        return session.exec(
            select(User).where(User.auth_id == auth_id, User.role == role)
        ).first()

    @staticmethod
    def get_existing_profile_data(session: Session, auth_id: str) -> Optional[Dict[str, str]]:
        """
        Get email and name from any existing profile for this auth_id.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            
        Returns:
            Dict with email and name if found, None otherwise
        """
        existing_user = session.exec(
            select(User).where(User.auth_id == auth_id)
        ).first()
        
        if existing_user:
            return {
                "email": existing_user.email,
                "name": existing_user.name
            }
        return None

    @staticmethod
    def get_user_with_role_profile(session: Session, user_id: str) -> Dict[str, Any]:
        """
        Get user with their role-specific profile.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            Dict containing user and role profile information
        """
        try:
            user = session.get(User, user_id)
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }

            role_profile = None
            if user.role == "rider":
                role_profile = session.exec(
                    select(Rider).where(Rider.user_id == user_id)
                ).first()
            elif user.role == "driver":
                role_profile = session.exec(
                    select(Driver).where(Driver.user_id == user_id)
                ).first()
            elif user.role == "admin":
                role_profile = session.exec(
                    select(Admin).where(Admin.user_id == user_id)
                ).first()

            return {
                "success": True,
                "user": user,
                "role_profile": role_profile
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get user profile: {str(e)}",
                "error": str(e)
            }

    @staticmethod
    def update_user_profile(
        session: Session,
        user_id: str,
        user_data: Dict[str, Any],
        role_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update user profile and role-specific data.
        
        Args:
            session: Database session
            user_id: User ID
            user_data: Updated user fields
            role_data: Updated role-specific fields
            
        Returns:
            Dict containing update result
        """
        try:
            user = session.get(User, user_id)
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }

            # Update user fields
            for field, value in user_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            # Update role-specific profile if provided
            if role_data:
                if user.role == UserRole.RIDER:
                    rider = session.exec(
                        select(Rider).where(Rider.user_id == user_id)
                    ).first()
                    if rider:
                        for field, value in role_data.items():
                            if hasattr(rider, field):
                                setattr(rider, field, value)
                                
                elif user.role == UserRole.DRIVER:
                    driver = session.exec(
                        select(Driver).where(Driver.user_id == user_id)
                    ).first()
                    if driver:
                        for field, value in role_data.items():
                            if hasattr(driver, field):
                                setattr(driver, field, value)
                                
                elif user.role == UserRole.ADMIN:
                    admin = session.exec(
                        select(Admin).where(Admin.user_id == user_id)
                    ).first()
                    if admin:
                        for field, value in role_data.items():
                            if hasattr(admin, field):
                                setattr(admin, field, value)

            session.commit()
            
            return {
                "success": True,
                "message": "User profile updated successfully",
                "user": user
            }
            
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to update user profile: {str(e)}",
                "error": str(e)
            }

    @staticmethod
    def get_all_user_profiles_with_data(session: Session, auth_id: str) -> Dict[str, Any]:
        """
        Get all profiles (rider and driver) for a user by auth_id.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            
        Returns:
            Dict containing all user profiles
        """
        try:
            # Get all user records for this auth_id
            users = session.exec(
                select(User).where(User.auth_id == auth_id)
            ).all()
            
            if not users:
                return {
                    "success": True,
                    "profiles": [],
                    "total_profiles": 0,
                    "message": "No profiles found"
                }
            
            profiles = []
            for user in users:
                profile_data = {
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "auth_status": user.auth_status,
                    "created_at": user.created_at.isoformat(),
                    "role_specific_data": None
                }
                
                # Get role-specific data
                if user.role == "rider":
                    rider = session.exec(
                        select(Rider).where(Rider.user_id == user.id)
                    ).first()
                    if rider:
                        profile_data["role_specific_data"] = {
                            "residence_place": rider.residence_place
                        }
                elif user.role == "driver":
                    driver = session.exec(
                        select(Driver).where(Driver.user_id == user.id)
                    ).first()
                    if driver:
                        profile_data["role_specific_data"] = {
                            "id_card": driver.id_card,
                            "driver_license": driver.driver_license,
                            "taxi_number": driver.taxi_number,
                            "account_status": driver.account_status
                        }
                
                profiles.append(profile_data)
            
            return {
                "success": True,
                "profiles": profiles,
                "total_profiles": len(profiles)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get user profiles: {str(e)}",
                "error": str(e)
            }

    @staticmethod
    async def handle_file_upload(file: Optional[UploadFile], file_type: str) -> Optional[str]:
        """Handle file upload and return URL or raise error."""
        if not file:
            return None
            
        bucket = settings.supabase_storage_bucket
        logger.info(f"Uploading {file_type}: {file.filename}")
        
        content = await file.read()
        file_url = upload_file_to_bucket(bucket, content, file.filename)
        
        logger.info(f"{file_type} upload result: {file_url}")
        if not file_url:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to upload {file_type} file"
            )
        
        return file_url

    @staticmethod
    async def prepare_rider_data(residence_place: Optional[str]) -> Dict[str, Any]:
        """Prepare rider-specific profile data."""
        role_data = {}
        if residence_place:
            role_data["residence_place"] = residence_place
        
        logger.info(f"Rider profile data prepared: {role_data}")
        return role_data

    @staticmethod
    async def prepare_driver_data(
        taxi_number: Optional[str],
        account_status: Optional[str], 
        id_card_file: Optional[UploadFile],
        driver_license_file: Optional[UploadFile]
    ) -> Dict[str, Any]:
        """Prepare driver-specific profile data with file uploads."""
        role_data = {}
        
        # Handle file uploads
        id_card_url = await UserService.handle_file_upload(id_card_file, "id_card")
        if id_card_url:
            role_data["id_card"] = id_card_url
        
        driver_license_url = await UserService.handle_file_upload(driver_license_file, "driver_license")
        if driver_license_url:
            role_data["driver_license"] = driver_license_url
        
        # Handle text fields
        if taxi_number:
            role_data["taxi_number"] = taxi_number
        if account_status:
            role_data["account_status"] = account_status
        
        logger.info(f"Driver profile data prepared: {role_data}")
        return role_data

    @staticmethod
    def build_role_profile_dict(user: Any, role_profile: Any) -> Optional[Dict[str, Any]]:
        """Build role profile dictionary for API response."""
        if not role_profile:
            return None
            
        role_profile_dict = {
            "id": role_profile.id,
            "user_id": role_profile.user_id,
            "created_at": role_profile.created_at.isoformat(),
            "updated_at": role_profile.updated_at.isoformat() if role_profile.updated_at else None
        }
        
        # Add role-specific fields
        if user.role == UserRole.RIDER:
            role_profile_dict["residence_place"] = role_profile.residence_place
        elif user.role == UserRole.DRIVER:
            role_profile_dict.update({
                "id_card": role_profile.id_card,
                "driver_license": role_profile.driver_license,
                "taxi_number": role_profile.taxi_number
            })
        elif user.role == UserRole.ADMIN:
            role_profile_dict["test_column"] = role_profile.test_column
        
        return role_profile_dict

    @staticmethod
    def get_email_by_phone(session: Session, phone_number: str) -> Optional[str]:
        """
        Get user email by phone number for password reset.
        
        Since email is a shared field between profiles, we can get it from any user record
        with the matching phone number.
        
        Args:
            session: Database session
            phone_number: User's phone number
            
        Returns:
            Email address if found, None otherwise
        """
        try:
            logger.info(f"Looking up email for phone number: {phone_number}")
            
            # Find user by phone number (any profile will do since email is shared)
            user = session.exec(
                select(User).where(User.phone_number == phone_number)
            ).first()
            
            if user:
                logger.info(f"Found email for phone {phone_number}: {user.email}")
                return user.email
            else:
                logger.warning(f"No user found with phone number: {phone_number}")
                return None
                
        except Exception as e:
            logger.error(f"Error looking up email by phone: {e}")
            return None

    @staticmethod 
    def get_email_by_auth_id(session: Session, auth_id: str) -> Optional[str]:
        """
        Get user email by Supabase auth ID for password reset.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            
        Returns:
            Email address if found, None otherwise
        """
        try:
            logger.info(f"Looking up email for auth_id: {auth_id}")
            
            # Find user by auth_id (any profile will do since email is shared)
            user = session.exec(
                select(User).where(User.auth_id == auth_id)
            ).first()
            
            if user:
                logger.info(f"Found email for auth_id {auth_id}: {user.email}")
                return user.email
            else:
                logger.warning(f"No user found with auth_id: {auth_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error looking up email by auth_id: {e}")
            return None

    @staticmethod
    def update_shared_data_across_profiles(
        session: Session,
        auth_id: str,
        shared_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update shared data (name, email) across all profiles for a user.
        
        Args:
            session: Database session
            auth_id: Supabase auth user ID
            shared_data: Dict containing name and/or email to update
            
        Returns:
            Dict containing update result
        """
        try:
            # Get all user profiles for this auth_id
            user_profiles = session.exec(
                select(User).where(User.auth_id == auth_id)
            ).all()
            
            if not user_profiles:
                return {
                    "success": False,
                    "message": "No profiles found for this user"
                }
            
            updated_profiles = []
            
            # Update shared data across all profiles
            for user in user_profiles:
                for field, value in shared_data.items():
                    if hasattr(user, field) and field in ["name", "email"]:
                        setattr(user, field, value)
                        logger.info(f"Updated {field} to '{value}' for {user.role} profile (ID: {user.id})")
                
                updated_profiles.append(user.role)
            
            session.commit()
            
            return {
                "success": True,
                "message": f"Shared data updated across {len(updated_profiles)} profiles",
                "updated_profiles": updated_profiles
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating shared data: {e}")
            return {
                "success": False,
                "message": f"Failed to update shared data: {str(e)}"
            }

    @staticmethod
    def update_driver_status(
        session: Session,
        driver_id: str,
        new_status: str
    ) -> Dict[str, Any]:
        """
        Update driver status.
        
        Args:
            session: Database session
            driver_id: Driver user ID
            new_status: New driver status (offline, online, on_trip)
            
        Returns:
            Dict containing update result
        """
        try:
            # Get driver record
            stmt = select(Driver).join(User).where(User.id == driver_id)
            result = session.exec(stmt)
            driver = result.first()
            
            if not driver:
                return {
                    "success": False,
                    "message": "Driver not found"
                }
            
            # Store old status for response
            old_status = driver.driver_status
            
            # Update driver status
            driver.driver_status = new_status
            session.add(driver)
            session.commit()
            session.refresh(driver)
            
            logger.info(f"Updated driver {driver_id} status from {old_status} to {new_status}")
            
            return {
                "success": True,
                "message": f"Driver status updated to {new_status}",
                "old_status": old_status,
                "new_status": new_status,
                "driver_id": driver_id
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating driver status for {driver_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to update driver status: {str(e)}"
            }
