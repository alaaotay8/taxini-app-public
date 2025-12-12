"""
Ticket-related schemas for API requests and responses.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from src.models.enums import UserRole
from src.models.ticket import TicketStatus, TicketPriority
import html


class TicketCreateRequest(BaseModel):
    """Request schema for creating a ticket."""
    title: str = Field(..., min_length=5, max_length=100, description="Brief description of the issue")
    content: str = Field(..., min_length=10, max_length=2000, description="Detailed description of the issue")
    priority: Optional[TicketPriority] = Field(default=TicketPriority.MEDIUM, description="Ticket priority level")
    issue_at: Optional[datetime] = Field(default=None, description="When the issue occurred")
    
    @field_validator('title', 'content')
    @classmethod
    def sanitize_text(cls, v):
        # Strip whitespace and escape HTML to prevent XSS
        v = html.escape(v.strip())
        return v


class TicketUpdateRequest(BaseModel):
    """Request schema for updating a ticket."""
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    content: Optional[str] = Field(None, min_length=10, max_length=2000)
    priority: Optional[TicketPriority] = None
    
    @field_validator('title', 'content')
    @classmethod
    def sanitize_text(cls, v):
        if v is not None:
            v = html.escape(v.strip())
        return v


class AdminTicketUpdateRequest(BaseModel):
    """Request schema for admin updating a ticket."""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    admin_notes: Optional[str] = Field(None, min_length=1)


class TicketResponse(BaseModel):
    """Response schema for ticket information."""
    id: str
    title: str
    content: str
    user_id: str
    user_role: UserRole
    status: TicketStatus
    priority: TicketPriority
    issue_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


class AdminTicketResponse(TicketResponse):
    """Admin response schema with additional fields."""
    admin_notes: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None


class TicketListResponse(BaseModel):
    """Response schema for listing tickets."""
    tickets: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminTicketListResponse(BaseModel):
    """Response schema for admin listing tickets."""
    tickets: List[AdminTicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TicketStatsResponse(BaseModel):
    """Response schema for ticket statistics."""
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
    high_priority: int
    urgent_priority: int
