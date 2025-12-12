"""
Ticket API endpoints for user support tickets.

Provides REST API for creating and managing support tickets.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
import logging
from typing import Optional

from src.schemas.ticket import (
    TicketCreateRequest,
    TicketUpdateRequest,
    TicketResponse,
    TicketListResponse
)
from src.models.ticket import TicketStatus, TicketPriority
from src.services.ticket import TicketService
from src.services.auth import AuthService
from src.schemas.auth import CurrentUser
from src.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse)
async def create_ticket(
    request: TicketCreateRequest,
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency),
    session: Session = Depends(get_session)
):
    """
    Create a new support ticket.
    
    Args:
        request: Ticket creation details
        current_user: Authenticated user info
        session: Database session
        
    Returns:
        Created ticket information
    """
    try:
        ticket = TicketService.create_ticket(
            session=session,
            user_id=current_user.user_id,
            title=request.title,
            content=request.content,
            priority=request.priority,
            issue_at=request.issue_at
        )
        
        if ticket is None:
            raise HTTPException(status_code=404, detail=f"User with ID {current_user.user_id} not found")
        
        return ticket
    except Exception as e:
        logger.error(f"Failed to create ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")


@router.get("", response_model=TicketListResponse)
async def list_user_tickets(
    page: int = 1,
    page_size: int = 10,
    status: Optional[TicketStatus] = None,
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency),
    session: Session = Depends(get_session)
):
    """
    List tickets for the authenticated user.
    
    Args:
        page: Page number (starting from 1)
        page_size: Number of tickets per page
        status: Filter tickets by status
        current_user: Authenticated user info
        session: Database session
        
    Returns:
        List of tickets with pagination information
    """
    try:
        result = TicketService.list_user_tickets(
            session=session,
            user_id=current_user.user_id,
            page=page,
            page_size=page_size,
            status=status
        )
        
        return TicketListResponse(
            tickets=result["tickets"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        logger.error(f"Failed to list tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list tickets")


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency),
    session: Session = Depends(get_session)
):
    """
    Get a specific ticket by ID.
    
    Args:
        ticket_id: ID of the ticket to retrieve
        current_user: Authenticated user info
        session: Database session
        
    Returns:
        Ticket information
    """
    try:
        result = TicketService.get_ticket(
            session=session,
            ticket_id=ticket_id,
            user_id=current_user.user_id,
            is_admin=current_user.role == "admin"
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Ticket with ID {ticket_id} not found")
        
        if isinstance(result, dict) and "error" in result:
            if result["error"] == "unauthorized":
                raise HTTPException(status_code=403, detail=result["message"])
            else:
                raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ticket")


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    request: TicketUpdateRequest,
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency),
    session: Session = Depends(get_session)
):
    """
    Update a ticket.
    
    Args:
        ticket_id: ID of the ticket to update
        request: Update data
        current_user: Authenticated user info
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
            is_admin=current_user.role == "admin",
            update_data=update_data
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Ticket with ID {ticket_id} not found")
        
        if isinstance(result, dict) and "error" in result:
            if result["error"] == "unauthorized":
                raise HTTPException(status_code=403, detail=result["message"])
            else:
                raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update ticket")
