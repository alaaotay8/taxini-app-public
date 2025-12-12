"""
Domain enums for the Taxini application.
"""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    DRIVER = "driver" 
    RIDER = "rider"
    
    def __str__(self):
        return self.value


class AuthStatus(str, Enum):
    """Authentication status enumeration."""
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    
    def __str__(self):
        return self.value


class DriverAccountStatus(str, Enum):
    """Driver account status enumeration."""
    LOCKED = "locked"      # Default - new accounts
    VERIFIED = "verified"  # After manual verification
    BANNED = "banned"      # Banned by admin
    
    def __str__(self):
        return self.value


class DriverStatus(str, Enum):
    """Driver status enumeration."""
    OFFLINE = "offline"    # Default - driver is offline
    ONLINE = "online"      # Driver is online and available
    ON_TRIP = "on_trip"    # Driver is currently on a trip
    
    def __str__(self):
        return self.value


class TripStatus(str, Enum):
    """Trip status enumeration."""
    REQUESTED = "requested"      # Trip requested by rider
    ASSIGNED = "assigned"        # Assigned to a driver
    ACCEPTED = "accepted"        # Driver accepted the trip
    STARTED = "started"          # Trip started (driver arrived)
    COMPLETED = "completed"      # Trip completed successfully
    CANCELLED = "cancelled"      # Trip cancelled
    
    def __str__(self):
        return self.value
