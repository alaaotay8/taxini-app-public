"""
Admin ticket management API endpoints.

Provides admin-only REST API for managing support tickets.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import logging
from typing import Optional

from src.schemas.ticket import (
    AdminTicketUpdateRequest,
    AdminTicketResponse,
    AdminTicketListResponse,
    TicketStatsResponse
)
from src.models.ticket import TicketStatus, TicketPriority
from src.services.ticket import TicketService
from src.models.user import User
from src.services.admin_auth import get_admin_user_dependency
from src.api.v1.admin import require_admin
from src.schemas.auth import CurrentUser
from src.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/tickets", tags=["Admin Tickets"])


@router.get("", response_model=AdminTicketListResponse)
async def list_all_tickets(
    page: int = 1,
    page_size: int = 10,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    user_id: Optional[str] = None,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    List all tickets (admin only).
    
    Args:
        page: Page number (starting from 1)
        page_size: Number of tickets per page
        status: Filter by ticket status
        priority: Filter by ticket priority
        user_id: Filter by user ID
        current_user: Authenticated admin user
        session: Database session
        
    Returns:
        List of tickets with pagination information
    """
    try:
        result = TicketService.list_all_tickets(
            session=session,
            page=page,
            page_size=page_size,
            status=status,
            priority=priority,
            user_id=user_id
        )
        
        # Enhance ticket responses with user information
        tickets_with_user_info = []
        for ticket in result["tickets"]:
            # Get user details for the ticket
            user = session.get(User, ticket.user_id)
            admin_ticket = {
                **ticket.dict(),
                "user_name": user.name if user else None,
                "user_email": user.email if user else None,
                "user_phone": user.phone_number if user else None
            }
            tickets_with_user_info.append(AdminTicketResponse(**admin_ticket))
            
        return AdminTicketListResponse(
            tickets=tickets_with_user_info,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"Failed to list tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list tickets")


@router.get("/stats", response_model=TicketStatsResponse)
async def get_ticket_stats(
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get ticket statistics (admin only).
    
    Args:
        current_user: Authenticated admin user
        session: Database session
        
    Returns:
        Ticket statistics
    """
    try:
        stats = TicketService.get_ticket_stats(session=session)
        return stats
    except Exception as e:
        logger.error(f"Failed to get ticket stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ticket statistics")


@router.get("/{ticket_id}", response_model=AdminTicketResponse)
async def get_ticket_admin(
    ticket_id: str,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get a specific ticket by ID (admin only).
    
    Args:
        ticket_id: ID of the ticket to retrieve
        current_user: Authenticated admin user
        session: Database session
        
    Returns:
        Ticket information with user details
    """
    try:
        result = TicketService.get_ticket(
            session=session,
            ticket_id=ticket_id,
            user_id=current_user.user_id,
            is_admin=True
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Ticket with ID {ticket_id} not found")
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["message"])
            
        # Get user details for the ticket
        user = session.get(User, result.user_id)
        admin_ticket = {
            **result.dict(),
            "user_name": user.name if user else None,
            "user_email": user.email if user else None,
            "user_phone": user.phone_number if user else None
        }
        
        return AdminTicketResponse(**admin_ticket)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ticket")


@router.patch("/{ticket_id}", response_model=AdminTicketResponse)
async def update_ticket_admin(
    ticket_id: str,
    request: AdminTicketUpdateRequest,
    current_user: CurrentUser = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Update a ticket (admin only).
    
    Args:
        ticket_id: ID of the ticket to update
        request: Update data
        current_user: Authenticated admin user
        session: Database session
        
    Returns:
        Updated ticket information
    """
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = request.dict(exclude_unset=True)
        
        result = TicketService.update_ticket(
            session=session,
            ticket_id=ticket_id,
            user_id=current_user.user_id,
            is_admin=True,
            update_data=update_data
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Ticket with ID {ticket_id} not found")
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["message"])
            
        # Get user details for the ticket
        user = session.get(User, result.user_id)
        admin_ticket = {
            **result.dict(),
            "user_name": user.name if user else None,
            "user_email": user.email if user else None,
            "user_phone": user.phone_number if user else None
        }
        
        return AdminTicketResponse(**admin_ticket)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update ticket")
