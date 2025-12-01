"""
Order Service - Handles order creation and management.
Based on pseudocode section 4.1 from the design document.
"""
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.menu import Dish
from ..models.user import Customer
from ..models.wallet import Wallet
from .payment_service import PaymentService
from .reputation_service import ReputationService
from ..core.config import settings


class OrderService:
    """Service for order operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.payment_service = PaymentService(db)
        self.reputation_service = ReputationService(db)
    
    def create_order(
        self, 
        customer_id: int, 
        cart_items: List[Dict]
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Create a new order from the customer's cart.
        
        Args:
            customer_id: ID of the customer
            cart_items: List of dicts with 'dish_id' and 'quantity'
        
        Returns:
            Tuple of (success: bool, message: str, order_id: Optional[int])
        """
        # If cartItems is empty → Error
        if not cart_items or len(cart_items) == 0:
            return False, "Cart is empty. Cannot create order", None
        
        # Load customer by customerId
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False, "Customer not found", None
        
        # Check each item in cart
        unavailable_items = []
        available_items = []
        
        for item in cart_items:
            dish_id = item.get('dish_id')
            quantity = item.get('quantity', 1)
            
            dish = self.db.query(Dish).filter(Dish.id == dish_id).first()
            
            # If dish missing OR dish unavailable → Mark unavailable
            if not dish or not dish.is_available:
                unavailable_items.append(dish_id)
            else:
                available_items.append({
                    'dish': dish,
                    'quantity': quantity
                })
        
        # If all items are unavailable → Error
        if len(available_items) == 0:
            return False, "All items unavailable. Order cancelled", None
        
        # Compute totalAmount
        total_amount = sum(item['dish'].price * item['quantity'] for item in available_items)
        
        # If customer is VIP → Apply 5% discount
        is_vip = customer.is_vip
        discount_amount = 0.0
        
        if is_vip:
            discount_amount = total_amount * (settings.VIP_DISCOUNT_PERCENTAGE / 100.0)
            final_amount = total_amount - discount_amount
        else:
            final_amount = total_amount
        
        # Load wallet for this customer
        wallet = self.db.query(Wallet).filter(Wallet.user_id == customer.user_id).first()
        if not wallet:
            return False, "Wallet not found", None
        
        # If wallet.balance < finalAmount → Insufficient funds
        if wallet.balance < final_amount:
            # Record reputation event
            self.reputation_service.record_event(
                user_id=customer.user_id,
                event_type="INSUFFICIENT_FUNDS_ORDER_REJECTED",
                details=f"Order amount: ${final_amount:.2f}, Balance: ${wallet.balance:.2f}"
            )
            return False, "Insufficient funds. Order rejected", None
        
        # Create order record with status = "PENDING_PAYMENT"
        order = Order(
            customer_id=customer_id,
            order_number=self._generate_order_number(),
            status=OrderStatus.PENDING_PAYMENT,
            payment_status=PaymentStatus.PENDING,
            subtotal=total_amount,
            discount_amount=discount_amount,
            total_amount=final_amount,
            is_vip_order=is_vip
        )
        
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        # Add order items
        for item in available_items:
            order_item = OrderItem(
                order_id=order.id,
                dish_id=item['dish'].id,
                quantity=item['quantity'],
                unit_price=item['dish'].price,
                total_price=item['dish'].price * item['quantity']
            )
            self.db.add(order_item)
        
        # Call PaymentService.processPayment
        payment_success, payment_message = self.payment_service.process_payment(
            order_id=order.id,
            customer_id=customer_id,
            amount=final_amount
        )
        
        if payment_success:
            # Update order status → "PLACED"
            order.status = OrderStatus.PLACED
            order.payment_status = PaymentStatus.PAID
            
            # Update customer statistics
            customer.total_orders += 1
            customer.total_spent += final_amount
            
            # Update dish popularity
            for item in available_items:
                item['dish'].times_ordered += item['quantity']
            
            self.db.commit()
            
            # TODO: Notify chefs that a new order is placed
            
            return True, "Order created successfully", order.id
        else:
            # Payment failed → Update order status → "REJECTED"
            order.status = OrderStatus.REJECTED
            order.payment_status = PaymentStatus.FAILED
            self.db.commit()
            
            return False, f"Payment failed. {payment_message}", None
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID."""
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def update_order_status(self, order_id: int, new_status: OrderStatus) -> bool:
        """Update order status."""
        order = self.get_order(order_id)
        if not order:
            return False
        
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        if new_status == OrderStatus.COMPLETED:
            order.completed_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def rate_order(
        self, 
        order_id: int, 
        food_rating: Optional[float] = None,
        delivery_rating: Optional[float] = None
    ) -> Tuple[bool, str]:
        """Rate food quality and delivery separately."""
        order = self.get_order(order_id)
        if not order:
            return False, "Order not found"
        
        if food_rating is not None:
            if not (1 <= food_rating <= 5):
                return False, "Food rating must be between 1 and 5"
            order.food_rating = food_rating
            
            # Update dish ratings
            for item in order.items:
                dish = item.dish
                # Recalculate average rating
                total_rating = dish.average_rating * dish.rating_count
                dish.rating_count += 1
                dish.average_rating = (total_rating + food_rating) / dish.rating_count
        
        if delivery_rating is not None:
            if not (1 <= delivery_rating <= 5):
                return False, "Delivery rating must be between 1 and 5"
            order.delivery_rating = delivery_rating
        
        self.db.commit()
        return True, "Rating submitted successfully"
    
    def _generate_order_number(self) -> str:
        """Generate unique order number."""
        return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

