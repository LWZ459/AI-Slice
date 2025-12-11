"""
Delivery Service - Handles delivery assignment and bidding.
Based on pseudocode section 4.3 from the design document.
"""
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..models.delivery import Delivery, DeliveryBid, DeliveryStatus, BidStatus, AssignmentType
from ..models.order import Order, OrderStatus
from ..models.user import DeliveryPerson, Manager


class DeliveryService:
    """Service for delivery and bidding operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assign_agent(
        self, 
        order_id: int,
        manager_override_delivery_person_id: Optional[int] = None,
        justification: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Assign a delivery person to an order after the bidding process.
        
        Args:
            order_id: ID of the order
            manager_override_delivery_person_id: Optional manual assignment by manager
            justification: Required justification if manager overrides
        
        Returns:
            Tuple of (success: bool, message: str, delivery_person_id: Optional[int])
        """
        # Load order by orderId
        order = self.db.query(Order).filter(Order.id == order_id).first()
        
        # If order not found → Error
        if not order:
            return False, "Order not found", None
        
        # Get or create delivery record
        delivery = self.db.query(Delivery).filter(Delivery.order_id == order_id).first()
        if not delivery:
            return False, "Delivery record not found", None
        
        # Load all bids for this order
        bids = self.db.query(DeliveryBid).filter(
            DeliveryBid.delivery_id == delivery.id,
            DeliveryBid.status == BidStatus.PENDING
        ).all()
        
        # If no bids → Set status and notify manager
        if len(bids) == 0:
            delivery.status = DeliveryStatus.NO_BIDDERS
            order.status = OrderStatus.READY_FOR_DELIVERY  # Waiting for manual assignment
            self.db.commit()
            
            # TODO: Notify manager: "No bids for this order"
            
            return False, "No bids. Manager must assign manually", None
        
        # Sort bids from lowest bidAmount to highest (tie: earlier timestamp first)
        sorted_bids = sorted(bids, key=lambda b: (b.bid_amount, b.created_at))
        lowest_bid = sorted_bids[0]
        
        # Check if there is a manager override
        if manager_override_delivery_person_id is not None:
            # Check if override is not the lowest bid
            override_bid = next(
                (b for b in bids if b.delivery_person_id == manager_override_delivery_person_id),
                None
            )
            
            if override_bid and override_bid.bid_amount > lowest_bid.bid_amount:
                if not justification:
                    return False, "Choosing a higher bid requires a justification memo", None
            
            chosen_delivery_person_id = manager_override_delivery_person_id
            assignment_type = AssignmentType.MANAGER_OVERRIDE
            
            if not override_bid:
                return False, "Manager override delivery person has no bid", None
            
            winning_bid_amount = override_bid.bid_amount
            override_bid.status = BidStatus.ACCEPTED
            
            # Reject other bids
            for bid in bids:
                if bid.id != override_bid.id:
                    bid.status = BidStatus.REJECTED
            
            # Save justification
            delivery.manager_justification = justification
        else:
            # Auto-assign to lowest bidder
            chosen_delivery_person_id = lowest_bid.delivery_person_id
            assignment_type = AssignmentType.AUTO_ASSIGN
            winning_bid_amount = lowest_bid.bid_amount
            
            # Mark winning bid as accepted
            lowest_bid.status = BidStatus.ACCEPTED
            
            # Reject other bids
            for bid in bids:
                if bid.id != lowest_bid.id:
                    bid.status = BidStatus.REJECTED
        
        # Create/update delivery assignment record
        delivery.delivery_person_id = chosen_delivery_person_id
        delivery.assignment_type = assignment_type
        delivery.winning_bid_amount = winning_bid_amount
        delivery.status = DeliveryStatus.ASSIGNED
        
        # Update order status
        order.status = OrderStatus.ASSIGNED_FOR_DELIVERY
        
        # Update delivery person stats
        delivery_person = self.db.query(DeliveryPerson).filter(
            DeliveryPerson.id == chosen_delivery_person_id
        ).first()
        if delivery_person:
            delivery_person.is_available = False
        
        self.db.commit()
        
        # TODO: Notify chosenDeliveryPerson: "You have been assigned to order #orderId"
        
        return True, "Delivery assigned successfully", chosen_delivery_person_id
    
    def create_delivery_listing(
        self, 
        order_id: int,
        pickup_address: str,
        delivery_address: str,
        distance: float,
        delivery_fee: float,
        bidding_duration_minutes: int = 30
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Create a delivery listing for bidding.
        
        Args:
            order_id: ID of the order
            pickup_address: Restaurant address
            delivery_address: Customer address
            distance: Distance in kilometers
            delivery_fee: Suggested delivery fee
            bidding_duration_minutes: How long bidding stays open
        
        Returns:
            Tuple of (success: bool, message: str, delivery_id: Optional[int])
        """
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False, "Order not found", None
        
        # Check if delivery already exists
        existing_delivery = self.db.query(Delivery).filter(
            Delivery.order_id == order_id
        ).first()
        if existing_delivery:
            return False, "Delivery already exists for this order", existing_delivery.id
        
        # Create delivery record
        delivery = Delivery(
            order_id=order_id,
            status=DeliveryStatus.PENDING_BIDDING,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            distance=distance,
            delivery_fee=delivery_fee,
            bidding_ends_at=datetime.utcnow() + timedelta(minutes=bidding_duration_minutes)
        )
        
        self.db.add(delivery)
        self.db.commit()
        
        return True, "Delivery listing created", delivery.id
    
    def place_bid(
        self,
        delivery_id: int,
        delivery_person_id: int,
        bid_amount: float,
        estimated_time: int,
        notes: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Place a bid for a delivery.
        
        Args:
            delivery_id: ID of the delivery
            delivery_person_id: ID of the delivery person
            bid_amount: Bid amount
            estimated_time: Estimated delivery time in minutes
            notes: Optional notes
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            return False, "Delivery not found"
        
        # Check if bidding is still open
        if datetime.utcnow() > delivery.bidding_ends_at:
            return False, "Bidding period has ended"
        
        # Check if delivery person already bid
        existing_bid = self.db.query(DeliveryBid).filter(
            DeliveryBid.delivery_id == delivery_id,
            DeliveryBid.delivery_person_id == delivery_person_id
        ).first()
        
        if existing_bid:
            return False, "You have already placed a bid for this delivery"
        
        # Create bid
        bid = DeliveryBid(
            delivery_id=delivery_id,
            delivery_person_id=delivery_person_id,
            bid_amount=bid_amount,
            estimated_time=estimated_time,
            notes=notes,
            status=BidStatus.PENDING
        )
        
        self.db.add(bid)
        self.db.commit()
        
        return True, "Bid placed successfully"
    
    def update_delivery_status(
        self,
        delivery_id: int,
        new_status: DeliveryStatus
    ) -> Tuple[bool, str]:
        """Update delivery status."""
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if not delivery:
            return False, "Delivery not found"
        
        delivery.status = new_status
        
        # Update timestamps based on status
        if new_status == DeliveryStatus.PICKED_UP:
            delivery.actual_pickup_time = datetime.utcnow()
        elif new_status == DeliveryStatus.DELIVERED:
            delivery.actual_delivery_time = datetime.utcnow()
            
            # Update delivery person availability
            if delivery.delivery_person_id:
                delivery_person = self.db.query(DeliveryPerson).filter(
                    DeliveryPerson.id == delivery.delivery_person_id
                ).first()
                if delivery_person:
                    delivery_person.is_available = True
                    delivery_person.total_deliveries += 1
        
        # Update related order status
        order = delivery.order
        if order:
            if new_status == DeliveryStatus.PICKED_UP:
                order.status = OrderStatus.IN_TRANSIT
            elif new_status == DeliveryStatus.DELIVERED:
                order.status = OrderStatus.DELIVERED
                # Also set order as completed for now, or require a separate step?
                # Let's mark it as delivered first. Rating can happen after.
                order.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return True, "Delivery status updated"
    
    def get_available_deliveries(self) -> List[Delivery]:
        """Get deliveries available for bidding or assignment."""
        return self.db.query(Delivery).filter(
            Delivery.status.in_([
                DeliveryStatus.PENDING_BIDDING,
                DeliveryStatus.NO_BIDDERS  # Also show deliveries needing assignment
            ])
        ).all()
    
    def get_delivery_bids(self, delivery_id: int) -> List[DeliveryBid]:
        """Get all bids for a delivery."""
        return self.db.query(DeliveryBid).filter(
            DeliveryBid.delivery_id == delivery_id
        ).order_by(DeliveryBid.bid_amount, DeliveryBid.created_at).all()

