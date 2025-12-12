"""
Admin settings service for managing configurable platform parameters.

This service handles CRUD operations for application settings including
pricing rates, operational parameters, and other configurable values.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select

from src.models.settings import Settings, SettingsUpdate, DEFAULT_SETTINGS, SettingKeys
from src.schemas.admin import SettingSummary, UpdateSettingRequest

logger = logging.getLogger(__name__)


class AdminSettingsService:
    """Service for managing application settings."""
    
    @staticmethod
    def initialize_default_settings(session: Session) -> None:
        """
        Initialize default settings if they don't exist.
        
        Args:
            session: Database session
        """
        try:
            for default_setting in DEFAULT_SETTINGS:
                # Check if setting already exists
                existing = session.exec(
                    select(Settings).where(
                        Settings.setting_key == default_setting["setting_key"]
                    )
                ).first()
                
                if not existing:
                    setting = Settings(**default_setting)
                    session.add(setting)
            
            session.commit()
            logger.info("Default settings initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize default settings: {str(e)}")
            session.rollback()
            raise
    
    @staticmethod
    def get_all_settings(session: Session, category: Optional[str] = None) -> List[SettingSummary]:
        """
        Get all settings, optionally filtered by category.
        
        Args:
            session: Database session
            category: Optional category filter
            
        Returns:
            List of SettingSummary objects
        """
        try:
            query = select(Settings).where(Settings.is_active == True)
            
            if category:
                query = query.where(Settings.category == category)
                
            settings = session.exec(query.order_by(Settings.category, Settings.setting_key)).all()
            
            return [
                SettingSummary(
                    id=setting.id,
                    setting_key=setting.setting_key,
                    setting_value=setting.setting_value,
                    data_type=setting.data_type,
                    description=setting.description,
                    category=setting.category,
                    is_active=setting.is_active,
                    is_editable=setting.is_editable,
                    updated_at=setting.updated_at
                )
                for setting in settings
            ]
            
        except Exception as e:
            logger.error(f"Failed to get settings: {str(e)}")
            return []
    
    @staticmethod
    def get_setting_by_key(session: Session, setting_key: str) -> Optional[SettingSummary]:
        """
        Get a specific setting by its key.
        
        Args:
            session: Database session
            setting_key: The setting key to retrieve
            
        Returns:
            SettingSummary object if found, None otherwise
        """
        try:
            setting = session.exec(
                select(Settings).where(Settings.setting_key == setting_key)
            ).first()
            
            if not setting:
                return None
                
            return SettingSummary(
                id=setting.id,
                setting_key=setting.setting_key,
                setting_value=setting.setting_value,
                data_type=setting.data_type,
                description=setting.description,
                category=setting.category,
                is_active=setting.is_active,
                is_editable=setting.is_editable,
                updated_at=setting.updated_at
            )
            
        except Exception as e:
            logger.error(f"Failed to get setting by key {setting_key}: {str(e)}")
            return None
    
    @staticmethod
    def update_setting(
        session: Session,
        setting_key: str,
        update_request: UpdateSettingRequest
    ) -> Dict[str, Any]:
        """
        Update a setting value.
        
        Args:
            session: Database session
            setting_key: The setting key to update
            update_request: Update request with new values
            
        Returns:
            Dict with success status and updated setting data
        """
        try:
            setting = session.exec(
                select(Settings).where(Settings.setting_key == setting_key)
            ).first()
            
            if not setting:
                return {
                    "success": False,
                    "message": f"Setting with key '{setting_key}' not found"
                }
            
            if not setting.is_editable:
                return {
                    "success": False,
                    "message": f"Setting '{setting_key}' is not editable"
                }
            
            # Validate the new value based on data type
            validation_result = AdminSettingsService._validate_setting_value(
                update_request.setting_value,
                setting.data_type
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": validation_result["message"]
                }
            
            # Update the setting
            setting.setting_value = update_request.setting_value
            if update_request.description is not None:
                setting.description = update_request.description
            
            session.add(setting)
            session.commit()
            session.refresh(setting)
            
            # Return updated setting
            updated_setting = SettingSummary(
                id=setting.id,
                setting_key=setting.setting_key,
                setting_value=setting.setting_value,
                data_type=setting.data_type,
                description=setting.description,
                category=setting.category,
                is_active=setting.is_active,
                is_editable=setting.is_editable,
                updated_at=setting.updated_at
            )
            
            logger.info(f"Setting '{setting_key}' updated successfully")
            
            return {
                "success": True,
                "message": f"Setting '{setting_key}' updated successfully",
                "data": updated_setting
            }
            
        except Exception as e:
            logger.error(f"Failed to update setting {setting_key}: {str(e)}")
            session.rollback()
            return {
                "success": False,
                "message": f"Failed to update setting: {str(e)}"
            }
    
    @staticmethod
    def get_setting_value(session: Session, setting_key: str, default_value: Any = None) -> Any:
        """
        Get a setting value with type conversion.
        
        Args:
            session: Database session
            setting_key: The setting key to retrieve
            default_value: Default value if setting not found
            
        Returns:
            Setting value converted to appropriate type
        """
        try:
            setting = session.exec(
                select(Settings).where(
                    Settings.setting_key == setting_key,
                    Settings.is_active == True
                )
            ).first()
            
            if not setting:
                return default_value
            
            # Convert value based on data type
            if setting.data_type == "float":
                return float(setting.setting_value)
            elif setting.data_type == "int":
                return int(setting.setting_value)
            elif setting.data_type == "bool":
                return setting.setting_value.lower() in ("true", "1", "yes", "on")
            else:
                return setting.setting_value
                
        except Exception as e:
            logger.error(f"Failed to get setting value for {setting_key}: {str(e)}")
            return default_value
    
    @staticmethod
    def _validate_setting_value(value: str, data_type: str) -> Dict[str, Any]:
        """
        Validate a setting value based on its data type.
        
        Args:
            value: The value to validate
            data_type: Expected data type
            
        Returns:
            Dict with validation result
        """
        try:
            if data_type == "float":
                float_val = float(value)
                if float_val < 0:
                    return {
                        "valid": False,
                        "message": "Float values must be non-negative"
                    }
            elif data_type == "int":
                int_val = int(value)
                if int_val < 0:
                    return {
                        "valid": False,
                        "message": "Integer values must be non-negative"
                    }
            elif data_type == "bool":
                if value.lower() not in ("true", "false", "1", "0", "yes", "no", "on", "off"):
                    return {
                        "valid": False,
                        "message": "Boolean values must be true/false, 1/0, yes/no, or on/off"
                    }
            
            return {"valid": True, "message": "Valid"}
            
        except ValueError as e:
            return {
                "valid": False,
                "message": f"Invalid {data_type} value: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def get_pricing_settings(session: Session) -> Dict[str, float]:
        """
        Get all pricing-related settings as a dictionary.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with pricing settings
        """
        try:
            pricing_settings = session.exec(
                select(Settings).where(
                    Settings.category == "pricing",
                    Settings.is_active == True
                )
            ).all()
            
            result = {}
            for setting in pricing_settings:
                try:
                    result[setting.setting_key] = float(setting.setting_value)
                except ValueError:
                    logger.warning(f"Invalid float value for {setting.setting_key}: {setting.setting_value}")
                    result[setting.setting_key] = 0.0
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get pricing settings: {str(e)}")
            return {}
