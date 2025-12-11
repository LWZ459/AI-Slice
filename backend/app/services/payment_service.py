"""
Payment Service - Handles wallet and payment processing.
Based on pseudocode section 4.2 from the design document.
"""
from typing import Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..models.wallet import Wallet, Transaction, TransactionType, TransactionStatus
from ..models.order import Order, PaymentStatus
from ..models.user import Customer


class PaymentService:
    """Service for payment and wallet operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_payment(
        self, 
        order_id: int, 
        customer_id: int, 
        amount: float
    ) -> Tuple[bool, str]:
        """
        Handle the payment for an order by checking and updating the user's wallet.
        
        Args:
            order_id: ID of the order
            customer_id: ID of the customer
            amount: Amount to pay
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Load customer to get user_id
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return False, "Customer not found"
        
        # Load wallet by customerId (user_id)
        wallet = self.db.query(Wallet).filter(Wallet.user_id == customer.user_id).first()
        
        # If no wallet found → Return FAILED
        if not wallet:
            return False, "Wallet not found"
        
        # If wallet.balance < amount → Insufficient funds
        if wallet.balance < amount:
            # Note: ReputationService is called from OrderService to avoid circular import
            return False, "Insufficient wallet balance"
        
        # Deduct amount from wallet.balance
        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.total_spent += amount
        balance_after = wallet.balance
        
        # Update Customer stats and check for VIP upgrade
        if customer:
            customer.total_spent += amount
            customer.total_orders += 1
            
            # VIP Upgrade Logic: > $100 spent OR >= 3 orders
            if not customer.is_vip:
                if customer.total_spent > 100.0 or customer.total_orders >= 3:
                    # Check for outstanding complaints
                    # We need to access ReputationService, but need to be careful of circular imports
                    # For now, let's assume this check happens or we do a direct DB query
                    from ..models.reputation import Complaint, ComplaintStatus
                    outstanding_complaints = self.db.query(Complaint).filter(
                        Complaint.subject_id == customer.user_id,
                        Complaint.status.in_([ComplaintStatus.PENDING, ComplaintStatus.UNDER_REVIEW])
                    ).count()
                    
                    if outstanding_complaints == 0:
                        customer.is_vip = True
                        customer.vip_since = datetime.utcnow()
                        customer.vip_orders_count = 0 # Reset for free delivery tracking
        
        # Create a payment transaction record
        transaction = Transaction(
            wallet_id=wallet.id,
            order_id=order_id,
            transaction_type=TransactionType.ORDER_PAYMENT,
            status=TransactionStatus.SUCCESS,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            payment_method="WALLET",
            reference_number=self._generate_reference_number()
        )
        
        self.db.add(transaction)
        
        # Update order paymentStatus → "PAID"
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.payment_status = PaymentStatus.PAID
        
        self.db.commit()
        
        # Return SUCCESS
        return True, "Payment completed"
    
    def deposit_money(
        self, 
        user_id: int, 
        amount: float, 
        payment_method: str = "credit_card"
    ) -> Tuple[bool, str]:
        """
        Deposit money into user's wallet.
        
        Args:
            user_id: ID of the user
            amount: Amount to deposit
            payment_method: Payment method used
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if amount <= 0:
            return False, "Deposit amount must be positive"
        
        # Get or create wallet
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0.0)
            self.db.add(wallet)
            self.db.flush()
        
        # Update balance
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.total_deposited += amount
        balance_after = wallet.balance
        
        # Create transaction record
        transaction = Transaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.SUCCESS,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            payment_method=payment_method,
            reference_number=self._generate_reference_number(),
            notes=f"Deposit via {payment_method}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        return True, f"Successfully deposited ${amount:.2f}"
    
    def refund_order(self, order_id: int) -> Tuple[bool, str]:
        """
        Refund an order amount back to the customer's wallet.
        
        Args:
            order_id: ID of the order to refund
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Get the original transaction
        original_transaction = self.db.query(Transaction).filter(
            Transaction.order_id == order_id,
            Transaction.transaction_type == TransactionType.ORDER_PAYMENT
        ).first()
        
        if not original_transaction:
            return False, "Original payment transaction not found"
        
        wallet = original_transaction.wallet
        refund_amount = original_transaction.amount
        
        # Update balance
        balance_before = wallet.balance
        wallet.balance += refund_amount
        wallet.total_refunded += refund_amount
        balance_after = wallet.balance
        
        # Create refund transaction
        refund_transaction = Transaction(
            wallet_id=wallet.id,
            order_id=order_id,
            transaction_type=TransactionType.REFUND,
            status=TransactionStatus.SUCCESS,
            amount=refund_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            payment_method="WALLET",
            reference_number=self._generate_reference_number(),
            notes=f"Refund for order #{order_id}"
        )
        
        self.db.add(refund_transaction)
        
        # Update order payment status
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.payment_status = PaymentStatus.REFUNDED
        
        self.db.commit()
        
        return True, f"Refunded ${refund_amount:.2f} to wallet"
    
    def get_wallet_balance(self, user_id: int) -> float:
        """Get current wallet balance for a user."""
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        return wallet.balance if wallet else 0.0
    
    def get_transaction_history(self, user_id: int, limit: int = 50):
        """Get transaction history for a user."""
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            return []
        
        return self.db.query(Transaction).filter(
            Transaction.wallet_id == wallet.id
        ).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    def _generate_reference_number(self) -> str:
        """Generate unique transaction reference number."""
        return f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

