"""
Ticket management service.

This service handles ticket creation, updates, and retrieval.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, func
from datetime import datetime

from src.models.ticket import Ticket, TicketStatus, TicketPriority
from src.models.user import User
from src.models.enums import UserRole

logger = logging.getLogger(__name__)


class TicketService:
    """Service for managing user support tickets."""
    
    @staticmethod
    def create_ticket(
        session: Session,
        user_id: str,
        title: str,
        content: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
        issue_at: Optional[datetime] = None
    ) -> Ticket:
        """
        Create a new support ticket.
        
        Args:
            session: Database session
            user_id: ID of the user creating the ticket
            title: Brief description of the issue
            content: Detailed description of the issue
            priority: Ticket priority level (default: MEDIUM)
            issue_at: When the issue occurred (default: None)
            
        Returns:
            The created ticket
            
        Raises:
            NotFoundException: If the user doesn't exist
        """
        # Check if user exists
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            logger.warning(f"Attempt to create ticket for non-existent user: {user_id}")
            return None
        
        # Create new ticket
        ticket = Ticket(
            title=title,
            content=content,
            user_id=user_id,
            user_role=user.role,
            priority=priority,
            issue_at=issue_at,
            status=TicketStatus.OPEN
        )
        
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        
        logger.info(f"Created ticket {ticket.id} for user {user_id}")
        return ticket
    
    @staticmethod
    def get_ticket(
        session: Session,
        ticket_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Ticket:
        """
        Get a specific ticket by ID.
        
        Args:
            session: Database session
            ticket_id: ID of the ticket to retrieve
            user_id: ID of the requesting user (for access control)
            is_admin: Whether the request is from an admin
            
        Returns:
            The requested ticket
            
        Raises:
            NotFoundException: If the ticket doesn't exist
            UnauthorizedException: If a non-admin user tries to access another user's ticket
        """
        ticket = session.exec(select(Ticket).where(Ticket.id == ticket_id)).first()
        if not ticket:
            logger.warning(f"Attempted to retrieve non-existent ticket: {ticket_id}")
            return None
        
        # Access control: only the ticket creator or admins can access a ticket
        if not is_admin and user_id != ticket.user_id:
            logger.warning(f"User {user_id} attempted unauthorized access to ticket {ticket_id}")
            return {"error": "unauthorized", "message": "You don't have permission to access this ticket"}
            
        return ticket
    
    @staticmethod
    def list_user_tickets(
        session: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        status: Optional[TicketStatus] = None
    ) -> Dict[str, Any]:
        """
        List tickets for a specific user.
        
        Args:
            session: Database session
            user_id: ID of the user whose tickets to list
            page: Page number (starting from 1)
            page_size: Number of tickets per page
            status: Filter by ticket status
            
        Returns:
            Dictionary containing tickets list and pagination info
        """
        query = select(Ticket).where(Ticket.user_id == user_id)
        
        if status:
            query = query.where(Ticket.status == status)
            
        # Get total count for pagination
        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        
        # Apply pagination
        tickets = session.exec(
            query.order_by(Ticket.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        
        return {
            "tickets": tickets,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    @staticmethod
    def list_all_tickets(
        session: Session,
        page: int = 1,
        page_size: int = 10,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all tickets (admin function).
        
        Args:
            session: Database session
            page: Page number (starting from 1)
            page_size: Number of tickets per page
            status: Filter by ticket status
            priority: Filter by ticket priority
            user_id: Filter by user ID
            
        Returns:
            Dictionary containing tickets list and pagination info
        """
        query = select(Ticket)
        
        # Apply filters if provided
        if status:
            query = query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
        if user_id:
            query = query.where(Ticket.user_id == user_id)
            
        # Get total count for pagination
        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        
        # Apply pagination
        tickets = session.exec(
            query.order_by(Ticket.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        
        return {
            "tickets": tickets,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    @staticmethod
    def update_ticket(
        session: Session,
        ticket_id: str,
        user_id: str,
        is_admin: bool,
        update_data: Dict[str, Any]
    ) -> Ticket:
        """
        Update a ticket.
        
        Args:
            session: Database session
            ticket_id: ID of the ticket to update
            user_id: ID of the requesting user
            is_admin: Whether the request is from an admin
            update_data: Dictionary with fields to update
            
        Returns:
            The updated ticket
            
        Raises:
            NotFoundException: If the ticket doesn't exist
            UnauthorizedException: If a non-admin user tries to update certain fields
        """
        ticket = TicketService.get_ticket(session, ticket_id, user_id, is_admin)
        
        # Regular users can only update title, content, and priority if ticket is still open
        if not is_admin:
            if ticket.status != TicketStatus.OPEN:
                return {"error": "unauthorized", "message": "You can only update open tickets"}
                
            allowed_fields = {"title", "content", "priority"}
            update_fields = set(update_data.keys())
            
            if not update_fields.issubset(allowed_fields):
                return {"error": "unauthorized", "message": "You can only update title, content and priority"}
        
        # Check if status is being changed to RESOLVED before applying updates
        changing_to_resolved = (
            is_admin and 
            "status" in update_data and 
            update_data["status"] == TicketStatus.RESOLVED and
            ticket.status != TicketStatus.RESOLVED
        )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(ticket, field, value)
            
        # If admin changed status to resolved, update resolved_at and resolved_by
        if changing_to_resolved:
            ticket.resolved_at = datetime.utcnow()
            ticket.resolved_by = user_id
            
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        
        return ticket
    
    @staticmethod
    def get_ticket_stats(session: Session) -> Dict[str, int]:
        """
        Get ticket statistics.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with ticket statistics
        """
        # Total count
        total = session.exec(select(func.count(Ticket.id))).one()
        
        # Count by status
        open_count = session.exec(
            select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.OPEN)
        ).one()
        
        in_progress_count = session.exec(
            select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.IN_PROGRESS)
        ).one()
        
        resolved_count = session.exec(
            select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.RESOLVED)
        ).one()
        
        closed_count = session.exec(
            select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.CLOSED)
        ).one()
        
        # Count by priority
        high_priority_count = session.exec(
            select(func.count(Ticket.id)).where(Ticket.priority == TicketPriority.HIGH)
        ).one()
        
        urgent_priority_count = session.exec(
            select(func.count(Ticket.id)).where(Ticket.priority == TicketPriority.URGENT)
        ).one()
        
        return {
            "total": total,
            "open": open_count,
            "in_progress": in_progress_count,
            "resolved": resolved_count,
            "closed": closed_count,
            "high_priority": high_priority_count,
            "urgent_priority": urgent_priority_count
        }
