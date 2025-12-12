"""
Tests for ticket functionality.
"""

import pytest
from sqlmodel import Session
from datetime import datetime
from unittest.mock import patch

from src.services.ticket import TicketService
from src.models.ticket import Ticket, TicketStatus, TicketPriority
from src.models.user import User
from src.models.enums import UserRole
from src.schemas.ticket import (
    TicketCreateRequest,
    TicketUpdateRequest,
    AdminTicketUpdateRequest
)


class TestTicketService:
    """Test cases for TicketService class."""
    
    @pytest.fixture
    def test_user(self, session: Session):
        """Create a test user."""
        user = User(
            id="test_user_id",
            name="Test User",
            email="test@example.com",
            phone_number="+1234567890",
            role=UserRole.RIDER,
            auth_id="test_auth_id",
            auth_status="verified"
        )
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture
    def test_admin(self, session: Session):
        """Create a test admin user."""
        admin = User(
            id="test_admin_id",
            name="Admin User",
            email="admin@example.com",
            phone_number="+9876543210",
            role=UserRole.ADMIN,
            auth_id="admin_auth_id",
            auth_status="verified"
        )
        session.add(admin)
        session.commit()
        return admin
    
    @pytest.fixture
    def test_ticket(self, session: Session, test_user):
        """Create a test ticket."""
        ticket = Ticket(
            id="test_ticket_id",
            title="Test Ticket",
            content="This is a test ticket content",
            user_id=test_user.id,
            user_role=test_user.role,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            created_at=datetime.utcnow()
        )
        session.add(ticket)
        session.commit()
        return ticket

    def test_create_ticket(self, session: Session, test_user):
        """Test creating a ticket."""
        # Arrange
        title = "Test Ticket"
        content = "This is a test ticket"
        priority = TicketPriority.HIGH
        
        # Act
        ticket = TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title=title,
            content=content,
            priority=priority
        )
        
        # Assert
        assert ticket is not None
        assert ticket.title == title
        assert ticket.content == content
        assert ticket.priority == priority
        assert ticket.status == TicketStatus.OPEN
        assert ticket.user_id == test_user.id
    
    def test_create_ticket_nonexistent_user(self, session: Session):
        """Test creating a ticket for a non-existent user."""
        # Act
        ticket = TicketService.create_ticket(
            session=session,
            user_id="non_existent_user_id",
            title="Test Ticket",
            content="Test Content",
            priority=TicketPriority.MEDIUM
        )
        
        # Assert
        assert ticket is None
    
    def test_get_ticket(self, session: Session, test_ticket, test_user):
        """Test retrieving a ticket."""
        # Act
        ticket = TicketService.get_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_user.id
        )
        
        # Assert
        assert ticket is not None
        assert ticket.id == test_ticket.id
        assert ticket.title == test_ticket.title
    
    def test_get_ticket_unauthorized_access(self, session: Session, test_ticket, test_admin):
        """Test unauthorized access to a ticket."""
        # Act - A user tries to access another user's ticket
        result = TicketService.get_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_admin.id,
            is_admin=False  # Not acting as admin
        )
        
        # Assert
        assert isinstance(result, dict)
        assert result["error"] == "unauthorized"
    
    def test_get_ticket_admin_access(self, session: Session, test_ticket, test_admin):
        """Test admin access to any ticket."""
        # Act - Admin accesses any ticket
        ticket = TicketService.get_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_admin.id,
            is_admin=True
        )
        
        # Assert
        assert ticket is not None
        assert ticket.id == test_ticket.id
    
    def test_list_user_tickets(self, session: Session, test_user):
        """Test listing tickets for a user."""
        # Arrange
        # Create multiple tickets for the user
        for i in range(3):
            TicketService.create_ticket(
                session=session,
                user_id=test_user.id,
                title=f"Ticket {i}",
                content=f"Content {i}",
                priority=TicketPriority.MEDIUM
            )
        
        # Act
        result = TicketService.list_user_tickets(
            session=session,
            user_id=test_user.id
        )
        
        # Assert
        assert "tickets" in result
        assert len(result["tickets"]) == 3
        assert result["total"] == 3
    
    def test_list_user_tickets_with_status_filter(self, session: Session, test_user):
        """Test listing tickets with status filter."""
        # Arrange
        # Create tickets with different statuses
        TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="Open Ticket",
            content="Open Content",
            priority=TicketPriority.MEDIUM
        )
        
        closed_ticket = TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="Closed Ticket",
            content="Closed Content",
            priority=TicketPriority.MEDIUM
        )
        closed_ticket.status = TicketStatus.CLOSED
        session.add(closed_ticket)
        session.commit()
        
        # Act - Filter by closed status
        result = TicketService.list_user_tickets(
            session=session,
            user_id=test_user.id,
            status=TicketStatus.CLOSED
        )
        
        # Assert
        assert "tickets" in result
        assert len(result["tickets"]) == 1
        assert result["tickets"][0].status == TicketStatus.CLOSED
    
    def test_list_all_tickets(self, session: Session, test_user, test_admin):
        """Test listing all tickets (admin function)."""
        # Arrange
        # Create tickets for different users
        TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="User Ticket",
            content="User Content",
            priority=TicketPriority.MEDIUM
        )
        
        TicketService.create_ticket(
            session=session,
            user_id=test_admin.id,
            title="Admin Ticket",
            content="Admin Content",
            priority=TicketPriority.HIGH
        )
        
        # Act
        result = TicketService.list_all_tickets(
            session=session
        )
        
        # Assert
        assert "tickets" in result
        assert len(result["tickets"]) == 2
    
    def test_list_all_tickets_with_filters(self, session: Session, test_user, test_admin):
        """Test listing all tickets with filters."""
        # Arrange
        TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="Medium Priority",
            content="Medium Content",
            priority=TicketPriority.MEDIUM
        )
        
        TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="High Priority",
            content="High Content",
            priority=TicketPriority.HIGH
        )
        
        # Act - Filter by priority
        result = TicketService.list_all_tickets(
            session=session,
            priority=TicketPriority.HIGH
        )
        
        # Assert
        assert "tickets" in result
        assert len(result["tickets"]) == 1
        assert result["tickets"][0].priority == TicketPriority.HIGH
    
    def test_update_ticket_by_owner(self, session: Session, test_ticket, test_user):
        """Test updating a ticket by its owner."""
        # Arrange
        update_data = {
            "title": "Updated Title",
            "content": "Updated Content",
            "priority": TicketPriority.HIGH
        }
        
        # Act
        updated_ticket = TicketService.update_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_user.id,
            is_admin=False,
            update_data=update_data
        )
        
        # Assert
        assert updated_ticket is not None
        assert updated_ticket.title == "Updated Title"
        assert updated_ticket.content == "Updated Content"
        assert updated_ticket.priority == TicketPriority.HIGH
    
    def test_update_ticket_unauthorized_fields(self, session: Session, test_ticket, test_user):
        """Test user trying to update unauthorized fields."""
        # Arrange
        update_data = {
            "status": TicketStatus.RESOLVED  # User shouldn't be able to change status
        }
        
        # Act
        result = TicketService.update_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_user.id,
            is_admin=False,
            update_data=update_data
        )
        
        # Assert
        assert isinstance(result, dict)
        assert result["error"] == "unauthorized"
    
    def test_update_closed_ticket_by_user(self, session: Session, test_ticket, test_user):
        """Test user trying to update a closed ticket."""
        # Arrange
        test_ticket.status = TicketStatus.CLOSED
        session.add(test_ticket)
        session.commit()
        
        update_data = {
            "title": "Updated Title"
        }
        
        # Act
        result = TicketService.update_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_user.id,
            is_admin=False,
            update_data=update_data
        )
        
        # Assert
        assert isinstance(result, dict)
        assert result["error"] == "unauthorized"
        assert "open tickets" in result["message"]
    
    def test_update_ticket_by_admin(self, session: Session, test_ticket, test_admin):
        """Test updating a ticket by an admin."""
        # Arrange
        update_data = {
            "status": TicketStatus.IN_PROGRESS,
            "priority": TicketPriority.URGENT,
            "admin_notes": "Working on this issue"
        }
        
        # Act
        updated_ticket = TicketService.update_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_admin.id,
            is_admin=True,
            update_data=update_data
        )
        
        # Assert
        assert updated_ticket is not None
        assert updated_ticket.status == TicketStatus.IN_PROGRESS
        assert updated_ticket.priority == TicketPriority.URGENT
        assert updated_ticket.admin_notes == "Working on this issue"
    
    def test_resolve_ticket_sets_resolver(self, session: Session, test_ticket, test_admin):
        """Test resolving a ticket sets resolver info."""
        # Arrange
        update_data = {
            "status": TicketStatus.RESOLVED
        }
        
        # Act
        updated_ticket = TicketService.update_ticket(
            session=session,
            ticket_id=test_ticket.id,
            user_id=test_admin.id,
            is_admin=True,
            update_data=update_data
        )
        
        # Assert
        assert updated_ticket is not None
        assert updated_ticket.status == TicketStatus.RESOLVED
        assert updated_ticket.resolved_by == test_admin.id
        assert updated_ticket.resolved_at is not None
    
    def test_get_ticket_stats(self, session: Session, test_user):
        """Test getting ticket statistics."""
        # Arrange
        # Create tickets with different statuses and priorities
        ticket1 = TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="Open Ticket",
            content="Open Content",
            priority=TicketPriority.MEDIUM
        )
        
        ticket2 = TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="In Progress Ticket",
            content="In Progress Content",
            priority=TicketPriority.HIGH
        )
        ticket2.status = TicketStatus.IN_PROGRESS
        
        ticket3 = TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="Resolved Ticket",
            content="Resolved Content",
            priority=TicketPriority.URGENT
        )
        ticket3.status = TicketStatus.RESOLVED
        
        ticket4 = TicketService.create_ticket(
            session=session,
            user_id=test_user.id,
            title="Closed Ticket",
            content="Closed Content",
            priority=TicketPriority.LOW
        )
        ticket4.status = TicketStatus.CLOSED
        
        session.add_all([ticket2, ticket3, ticket4])
        session.commit()
        
        # Act
        stats = TicketService.get_ticket_stats(session)
        
        # Assert
        assert stats["total"] == 4
        assert stats["open"] == 1
        assert stats["in_progress"] == 1
        assert stats["resolved"] == 1
        assert stats["closed"] == 1
        assert stats["high_priority"] == 1
        assert stats["urgent_priority"] == 1
