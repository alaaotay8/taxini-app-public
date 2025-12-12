#!/usr/bin/env python
"""
Create a predefined admin user with credentials.

This script creates an admin user in both the local database and 
Supabase Auth for administrative access to the Taxini backend.

Usage: 
    python create_admin.py
"""

import sys
import logging
from pathlib import Path
from sqlmodel import Session, select
from dotenv import load_dotenv

# Add parent directory to path to allow imports from src
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path is configured
from src.db.session import get_session
from src.models.user import User, Admin
from src.models.enums import UserRole
from src.services import supabase_client
from src.core.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get admin credentials from settings with fallback defaults
ADMIN_EMAIL = settings.admin_email or "admin@taxini.com"
ADMIN_PASSWORD = settings.admin_password or "Admin@123"
ADMIN_NAME = settings.admin_name or "Taxini Admin"
ADMIN_PHONE = settings.admin_phone or "+12345678900"

def create_admin_user():
    """Create a predefined admin user in both DB and Supabase Auth."""
    
    logger.info("Creating admin user...")
    
    # Get a database session
    session = next(get_session())
    
    try:
        # Check if admin already exists in our database
        existing_user = session.exec(
            select(User).where(
                User.email == ADMIN_EMAIL,
                User.role == UserRole.ADMIN.value
            )
        ).first()
        
        if existing_user:
            logger.info(f"Admin user already exists in database with ID: {existing_user.id}")
            admin_user = existing_user
        else:
            # Create admin user in our database
            admin_user = User(
                auth_id="admin_auth_id",  # Will be updated after Supabase creation
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                phone_number=ADMIN_PHONE,
                role=UserRole.ADMIN.value,
                auth_status="verified"
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            logger.info(f"Created admin user in database with ID: {admin_user.id}")
            
        # Check if admin profile exists
        existing_profile = session.exec(
            select(Admin).where(Admin.user_id == admin_user.id)
        ).first()
        
        if existing_profile:
            logger.info(f"Admin profile already exists, updating password...")
            existing_profile.test_column = ADMIN_PASSWORD
            session.add(existing_profile)
        else:
            # Create admin profile
            admin_profile = Admin(
                user_id=admin_user.id,
                test_column=ADMIN_PASSWORD  # Store password in test_column field
            )
            session.add(admin_profile)
            logger.info("Created admin profile with password")
            
        session.commit()
        
        # Create or update user in Supabase Auth
        client = supabase_client.ensure_supabase_client()
        
        try:
            # Try to get user from Supabase
            users = client.auth.admin.list_users()
            supabase_user = None
            
            for user in users:
                if user.email == ADMIN_EMAIL:
                    supabase_user = user
                    break
                    
            if supabase_user:
                logger.info(f"Admin user already exists in Supabase with ID: {supabase_user.id}")
                
                # Update admin_user.auth_id if needed
                if admin_user.auth_id != supabase_user.id:
                    admin_user.auth_id = supabase_user.id
                    session.add(admin_user)
                    session.commit()
                    logger.info(f"Updated admin user auth_id to: {supabase_user.id}")
            else:
                # Create user in Supabase
                logger.info("Creating admin user in Supabase Auth...")
                new_user = client.auth.admin.create_user({
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "email_confirm": True  # Auto-confirm email
                })
                
                if new_user:
                    logger.info(f"Created admin user in Supabase with ID: {new_user.id}")
                    
                    # Update auth_id in our database
                    admin_user.auth_id = new_user.id
                    session.add(admin_user)
                    session.commit()
                    logger.info(f"Updated admin user auth_id to: {new_user.id}")
                    
        except Exception as supabase_error:
            logger.error(f"Failed to create/verify Supabase user: {supabase_error}")
            logger.warning("Admin created only in local database, Supabase sync failed")
        
        logger.info("Admin user creation completed.")
        logger.info(f"Email: {ADMIN_EMAIL}")
        logger.info(f"Password: {ADMIN_PASSWORD}")
        logger.info("You can now login using these credentials at /api/v1/admin/login")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create admin user: {e}")
        sys.exit(1)
    
    finally:
        session.close()

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Show source of admin credentials
    logger.info("Admin credentials configuration:")
    logger.info(f"Email: {ADMIN_EMAIL} (from {'env' if settings.admin_email else 'default'})")
    logger.info(f"Password: {'[from env]' if settings.admin_password else ADMIN_PASSWORD}")
    logger.info(f"Name: {ADMIN_NAME} (from {'env' if settings.admin_name else 'default'})")
    logger.info(f"Phone: {ADMIN_PHONE} (from {'env' if settings.admin_phone else 'default'})")
    
    # Confirm to proceed
    try:
        input("Press Enter to continue with these credentials or Ctrl+C to cancel...")
        create_admin_user()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
