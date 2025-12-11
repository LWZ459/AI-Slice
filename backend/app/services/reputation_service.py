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
    
    def check_staff_performance(self, user_id: int) -> None:
        """
        Evaluate staff performance and apply demotions/bonuses.
        
        Rules:
        - Low Rating (< 2.0) OR 3 complaints => Demotion (Lower Salary)
        - 2 Demotions => Fired (Deactivated)
        - High Rating (> 4.0) OR 3 compliments => Bonus
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.user_type not in [UserType.CHEF, UserType.DELIVERY]:
            return

        reputation = self.db.query(Reputation).filter(Reputation.user_id == user_id).first()
        if not reputation:
            return

        # Get Staff Record (Chef or DeliveryPerson)
        staff_record = None
        if user.user_type == UserType.CHEF:
            staff_record = user.chef
        elif user.user_type == UserType.DELIVERY:
            staff_record = user.delivery_person
            
        if not staff_record:
            return

        # --- DEMOTION LOGIC ---
        # Condition: Rating < 2.0 OR Complaints >= 3
        # Note: In a real system, we'd check complaints in a recent window, but requirements imply cumulative "3 complaints".
        # We should reset complaint count after action to avoid loop, or track "processed" complaints.
        # For simplicity based on prompt: "3 complaints will be demoted". Let's assume net active complaints.
        
        # Calculate net complaints (assuming compliments cancel complaints 1:1)
        # However, cancellation is handled in file_compliment. So total_complaints is the historical count?
        # Let's count PENDING or RESOLVED complaints that haven't been "spent" on a demotion?
        # Or just use the raw counters if they are reset.
        # Let's rely on the counters in the Staff model which we added: complaints_count
        
        should_demote = False
        if staff_record.average_rating > 0 and staff_record.average_rating < 2.0:
            should_demote = True
        if staff_record.complaints_count >= 3:
            should_demote = True
            
        if should_demote:
            # Apply Demotion
            staff_record.demotion_count += 1
            
            # 2 Demotions => Fire
            if staff_record.demotion_count >= 2:
                user.status = UserStatus.DEACTIVATED
                self.record_event(user_id, "FIRED", "Fired due to 2nd demotion")
            else:
                # 1st Demotion => Lower Salary
                if staff_record.salary > 0:
                    staff_record.salary *= 0.9 # 10% cut
                self.record_event(user_id, "DEMOTION", "Demoted due to poor performance")
            
            # Reset counters to give another chance (or valid for next cycle)
            staff_record.complaints_count = 0 
            
        # --- BONUS LOGIC ---
        # Condition: Rating > 4.0 OR 3 Compliments
        should_bonus = False
        if staff_record.average_rating > 4.0:
            should_bonus = True
        if staff_record.compliments_count >= 3:
            should_bonus = True
            
        if should_bonus:
            # Apply Bonus (Salary Increase or Cash Bonus?)
            # "receive a bonus" -> Let's give a one-time bonus to wallet AND small raise
            wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
            if wallet:
                wallet.balance += 50.0 # $50 bonus
                
            staff_record.salary *= 1.05 # 5% raise
            self.record_event(user_id, "BONUS", "Performance bonus awarded")
            
            # Reset counters
            staff_record.compliments_count = 0

        self.db.commit()

    def record_event(
        self,
        user_id: int,
        event_type: str,
        details: str = "",
        created_by: Optional[int] = None
    ) -> bool:
        """
        Record events that affect user reputation and update scores.
        """
        # ... (existing implementation) ...
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
            
            # Check Staff Performance
            if user.user_type in [UserType.CHEF, UserType.DELIVERY]:
                # Update staff specific counters
                staff = user.chef if user.user_type == UserType.CHEF else user.delivery_person
                if staff:
                    if event_enum == ReputationEventType.COMPLAINT:
                        staff.complaints_count += 1
                    elif event_enum == ReputationEventType.COMPLIMENT:
                        staff.compliments_count += 1
                
                self.check_staff_performance(user_id)
        
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
        
        # Check performance immediately
        self.check_staff_performance(receiver_id)
        
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
            
            # Decrease complaints count for staff
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                if user.user_type == UserType.CHEF and user.chef:
                    user.chef.complaints_count = max(0, user.chef.complaints_count - 1)
                elif user.user_type == UserType.DELIVERY and user.delivery_person:
                    user.delivery_person.complaints_count = max(0, user.delivery_person.complaints_count - 1)

