"""
Reputation Service - Handles user reputation tracking and management.
Based on pseudocode section 4.6 from the design document.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.reputation import (
    Reputation, 
    ReputationEvent, 
    ReputationEventType,
    Complaint,
    Compliment,
    ComplaintStatus
)
from ..models.user import User, UserStatus, Customer, Chef, DeliveryPerson
from ..core.config import settings


class ReputationService:
    """Service for reputation management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_event(
        self,
        user_id: int,
        event_type: str,
        details: str = "",
        created_by: Optional[int] = None
    ) -> bool:
        """
        Record events that affect user reputation and update scores.
        
        Args:
            user_id: ID of the user
            event_type: Type of event (string, will be converted to enum)
            details: Description of the event
            created_by: ID of user who created this event
        
        Returns:
            bool: Success status
        """
        # Get or create reputation record
        reputation = self.db.query(Reputation).filter(
            Reputation.user_id == user_id
        ).first()
        
        if not reputation:
            reputation = Reputation(user_id=user_id, score=0)
            self.db.add(reputation)
            self.db.flush()
        
        # Convert string to enum
        try:
            event_enum = ReputationEventType[event_type.upper()]
        except KeyError:
            # If not a valid enum, use a generic one
            event_enum = ReputationEventType.ORDER_COMPLETED
        
        # Use ReputationRuleEngine to compute scoreChange
        score_change = self._calculate_score_change(event_enum)
        
        # Insert a new row into reputation log
        event = ReputationEvent(
            reputation_id=reputation.id,
            event_type=event_enum,
            score_change=score_change,
            description=event_type,
            details=details,
            created_by=created_by
        )
        self.db.add(event)
        
        # Load current reputationScore
        current_score = reputation.score
        new_score = current_score + score_change
        
        # Save newScore back to database
        reputation.score = new_score
        reputation.updated_at = datetime.utcnow()
        
        # Update event counters
        if event_enum == ReputationEventType.COMPLAINT:
            reputation.total_complaints += 1
        elif event_enum == ReputationEventType.COMPLIMENT:
            reputation.total_compliments += 1
        elif event_enum == ReputationEventType.WARNING:
            reputation.total_warnings += 1
        
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if user:
            # Check VIP threshold
            if new_score >= settings.VIP_REPUTATION_THRESHOLD:
                customer = self.db.query(Customer).filter(
                    Customer.user_id == user_id
                ).first()
                if customer and not customer.is_vip:
                    self._promote_to_vip(customer)
            
            # Check blacklist threshold
            if new_score <= settings.BLACKLIST_REPUTATION_THRESHOLD:
                user.status = UserStatus.BLACKLISTED
                # TODO: Notify security or manager
        
        self.db.commit()
        return True
    
    def file_complaint(
        self,
        complainant_id: int,
        subject_id: int,
        title: str,
        description: str,
        order_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        File a complaint against a user.
        
        Args:
            complainant_id: ID of user filing complaint
            subject_id: ID of user being complained about
            title: Title of complaint
            description: Description of complaint
            order_id: Optional related order ID
        
        Returns:
            Tuple of (success: bool, message: str, complaint_id: Optional[int])
        """
        # Check if complainant is VIP (complaints count double)
        complainant = self.db.query(Customer).filter(
            Customer.user_id == complainant_id
        ).first()
        
        weight = 2 if (complainant and complainant.is_vip) else 1
        
        # Create complaint
        complaint = Complaint(
            complainant_id=complainant_id,
            subject_id=subject_id,
            title=title,
            description=description,
            order_id=order_id,
            weight=weight,
            status=ComplaintStatus.PENDING
        )
        
        self.db.add(complaint)
        
        # Record reputation event for subject
        self.record_event(
            user_id=subject_id,
            event_type="COMPLAINT",
            details=f"Complaint: {title}",
            created_by=complainant_id
        )
        
        self.db.commit()
        
        return True, "Complaint filed successfully", complaint.id
    
    def file_compliment(
        self,
        giver_id: int,
        receiver_id: int,
        title: str,
        description: str = "",
        order_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        File a compliment for a user.
        
        Args:
            giver_id: ID of user giving compliment
            receiver_id: ID of user receiving compliment
            title: Title of compliment
            description: Description of compliment
            order_id: Optional related order ID
        
        Returns:
            Tuple of (success: bool, message: str, compliment_id: Optional[int])
        """
        # Check if giver is VIP (compliments count double)
        giver = self.db.query(Customer).filter(
            Customer.user_id == giver_id
        ).first()
        
        weight = 2 if (giver and giver.is_vip) else 1
        
        # Create compliment
        compliment = Compliment(
            giver_id=giver_id,
            receiver_id=receiver_id,
            title=title,
            description=description,
            order_id=order_id,
            weight=weight
        )
        
        self.db.add(compliment)
        
        # Record reputation event for receiver
        self.record_event(
            user_id=receiver_id,
            event_type="COMPLIMENT",
            details=f"Compliment: {title}",
            created_by=giver_id
        )
        
        # One compliment cancels one complaint (if applicable)
        self._cancel_complaint_with_compliment(receiver_id)
        
        self.db.commit()
        
        return True, "Compliment submitted successfully", compliment.id
    
    def check_warnings(self, user_id: int) -> int:
        """Get warning count for a user."""
        reputation = self.db.query(Reputation).filter(
            Reputation.user_id == user_id
        ).first()
        
        return reputation.total_warnings if reputation else 0
    
    def apply_warning(self, user_id: int, reason: str) -> bool:
        """Apply a warning to a user."""
        # Record reputation event
        self.record_event(
            user_id=user_id,
            event_type="WARNING",
            details=reason
        )
        
        # Check if user should be deregistered
        warning_count = self.check_warnings(user_id)
        
        if warning_count >= settings.WARNING_THRESHOLD_DEREGISTER:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.status = UserStatus.DEACTIVATED
        
        # Check if VIP should be demoted
        customer = self.db.query(Customer).filter(Customer.user_id == user_id).first()
        if customer and customer.is_vip:
            if warning_count >= settings.WARNING_THRESHOLD_VIP_DEMOTION:
                self._demote_from_vip(customer)
        
        self.db.commit()
        return True
    
    def _calculate_score_change(self, event_type: ReputationEventType) -> int:
        """Calculate score change based on event type."""
        score_map = {
            ReputationEventType.COMPLAINT: -10,
            ReputationEventType.COMPLIMENT: +10,
            ReputationEventType.WARNING: -20,
            ReputationEventType.BONUS: +15,
            ReputationEventType.DEMOTION: -25,
            ReputationEventType.PROMOTION: +30,
            ReputationEventType.ORDER_COMPLETED: +2,
            ReputationEventType.ORDER_REJECTED: -5,
            ReputationEventType.INSUFFICIENT_FUNDS: -3,
            ReputationEventType.RATING_RECEIVED: 0,  # Calculated separately
        }
        
        return score_map.get(event_type, 0)
    
    def _promote_to_vip(self, customer: Customer) -> None:
        """Promote a customer to VIP status."""
        customer.is_vip = True
        customer.vip_since = datetime.utcnow()
        
        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if user:
            user.user_type = UserType.VIP
    
    def _demote_from_vip(self, customer: Customer) -> None:
        """Demote a customer from VIP status."""
        customer.is_vip = False
        customer.vip_since = None
        customer.vip_orders_count = 0
        
        # Clear warnings (per requirements)
        reputation = self.db.query(Reputation).filter(
            Reputation.user_id == customer.user_id
        ).first()
        if reputation:
            reputation.total_warnings = 0
        
        user = self.db.query(User).filter(User.id == customer.user_id).first()
        if user:
            from ..models.user import UserType
            user.user_type = UserType.CUSTOMER
    
    def _cancel_complaint_with_compliment(self, user_id: int) -> None:
        """Cancel one complaint with one compliment."""
        # Find an unresolved complaint
        complaint = self.db.query(Complaint).filter(
            Complaint.subject_id == user_id,
            Complaint.status == ComplaintStatus.PENDING
        ).first()
        
        if complaint:
            complaint.status = ComplaintStatus.RESOLVED
            complaint.resolved_at = datetime.utcnow()
            complaint.manager_decision = "Cancelled by compliment"

