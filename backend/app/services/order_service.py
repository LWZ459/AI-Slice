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
            # If dish is VIP-only and customer is not VIP → Reject
            elif dish.is_special and not customer.is_vip:
                return False, f"'{dish.name}' is a VIP-only item. Become a VIP to order this dish!", None
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
        delivery_fee = 5.0 # Default fee
        is_free_delivery = False
        
        if is_vip:
            discount_amount = total_amount * (settings.VIP_DISCOUNT_PERCENTAGE / 100.0)
            
            # Check for free delivery
            from ..models.user import VIPCustomer
            vip_record = self.db.query(VIPCustomer).filter(VIPCustomer.customer_id == customer.id).first()
            if vip_record and vip_record.free_deliveries_earned > vip_record.free_deliveries_used:
                is_free_delivery = True
                delivery_fee = 0.0
                vip_record.free_deliveries_used += 1
                
            final_amount = total_amount - discount_amount + delivery_fee
        else:
            final_amount = total_amount + delivery_fee
        
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
            delivery_fee=delivery_fee,
            is_vip_order=is_vip,
            is_free_delivery=is_free_delivery
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
            
            # Update VIP free delivery progress
            if customer.is_vip:
                customer.vip_orders_count += 1
                if customer.vip_orders_count % 3 == 0:
                    from ..models.user import VIPCustomer
                    vip_record = self.db.query(VIPCustomer).filter(VIPCustomer.customer_id == customer.id).first()
                    if not vip_record:
                        vip_record = VIPCustomer(customer_id=customer.id)
                        self.db.add(vip_record)
                    
                    vip_record.free_deliveries_earned += 1
            
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
        delivery_rating: Optional[float] = None,
        item_ratings: Optional[List[dict]] = None
    ) -> Tuple[bool, str]:
        """Rate food quality and delivery separately."""
        order = self.get_order(order_id)
        if not order:
            return False, "Order not found"
        
        # Handle individual item ratings
        if item_ratings:
            for rating_data in item_ratings:
                item_id = rating_data.get('order_item_id')
                rating_val = rating_data.get('rating')
                
                if item_id and rating_val:
                    # Find item
                    item = next((i for i in order.items if i.id == item_id), None)
                    if item:
                        item.rating = rating_val
                        
                        # Update dish stats
                        dish = item.dish
                        if dish:
                            total_rating = dish.average_rating * dish.rating_count
                            dish.rating_count += 1
                            dish.average_rating = (total_rating + rating_val) / dish.rating_count
        
        # Fallback/Legacy: If overall food_rating is provided but no item ratings, 
        # apply it to all items? Or just keep it as overall order rating.
        # Let's keep existing logic for overall food_rating if provided
        if food_rating is not None:
            if not (1 <= food_rating <= 5):
                return False, "Food rating must be between 1 and 5"
            order.food_rating = food_rating
            
            # Only update dishes if item_ratings wasn't provided (avoid double counting)
            if not item_ratings:
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
            
            # Update delivery person rating
            if order.delivery and order.delivery.delivery_person:
                driver = order.delivery.delivery_person
                total_driver_rating = driver.average_rating * driver.total_deliveries # Approx
                # A better way is to track rating count separately or just increment
                # Since we don't have explicit rating_count for driver in schema (just total_deliveries),
                # let's assume total_deliveries is close enough or use it as count
                
                # Actually driver.total_deliveries is incremented on delivery completion
                # So we can use it as weight
                
                # Check if this order was already rated? 
                # For simplicity, we just update the moving average
                # New Average = Old Average + (New Rating - Old Average) / N
                # But here we treat it as a new data point
                
                # Let's just do weighted average update
                # Since we don't store rating_count separately, use total_deliveries
                count = max(1, driver.total_deliveries)
                driver.average_rating = ((driver.average_rating * count) + delivery_rating) / (count + 1)
        
        self.db.commit()
        return True, "Rating submitted successfully"
    
    def _generate_order_number(self) -> str:
        """Generate unique order number."""
        return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

