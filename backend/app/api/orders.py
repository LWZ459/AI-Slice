"""
Order management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType, Customer
from ..models.order import Order, OrderStatus
from ..schemas.order import OrderCreate, OrderResponse, OrderRating, OrderItemResponse
from ..services.order_service import OrderService

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(require_user_type(UserType.CUSTOMER, UserType.VIP)),
    db: Session = Depends(get_db)
):
    """
    Create a new order.
    
    - **items**: List of cart items with dish_id and quantity
    - **delivery_address**: Delivery address
    - **delivery_instructions**: Optional delivery notes
    
    Automatically applies VIP discount if applicable.
    Order is rejected if wallet balance is insufficient.
    """
    # Get customer record
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer record not found"
        )
    
    # Create order service
    order_service = OrderService(db)
    
    # Convert schema to service format
    cart_items = [
        {"dish_id": item.dish_id, "quantity": item.quantity}
        for item in order_data.items
    ]
    
    # Create order
    success, message, order_id = order_service.create_order(
        customer_id=customer.id,
        cart_items=cart_items
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update order with delivery details
    order = order_service.get_order(order_id)
    if order:
        order.delivery_address = order_data.delivery_address
        order.delivery_instructions = order_data.delivery_instructions
        db.commit()
    
    return {
        "success": True,
        "message": message,
        "order_id": order_id,
        "order_number": order.order_number if order else None
    }


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List orders for current user.
    
    - **skip**: Number of orders to skip (pagination)
    - **limit**: Maximum number of orders to return
    - **status_filter**: Optional filter by status
    
    Returns different orders based on user type:
    - Customers: Their own orders
    - Chefs: Orders containing their dishes
    - Delivery: Orders assigned to them
    - Managers: All orders
    """
    query = db.query(Order)
    
    # Filter based on user type
    if current_user.user_type in [UserType.CUSTOMER, UserType.VIP]:
        customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
        if customer:
            query = query.filter(Order.customer_id == customer.id)
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = OrderStatus[status_filter.upper()]
            query = query.filter(Order.status == status_enum)
        except KeyError:
            pass
    
    # Get orders
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format
    result = []
    for order in orders:
        # Get delivery person's User ID if delivery exists
        delivery_person_id = None
        if order.delivery and order.delivery.delivery_person:
            delivery_person_id = order.delivery.delivery_person.user_id
        
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status.value,
            "payment_status": order.payment_status.value,
            "subtotal": order.subtotal,
            "discount_amount": order.discount_amount,
            "delivery_fee": order.delivery_fee,
            "total_amount": order.total_amount,
            "is_vip_order": order.is_vip_order,
            "is_free_delivery": order.is_free_delivery,
            "delivery_address": order.delivery_address or "",
            "food_rating": order.food_rating,
            "delivery_rating": order.delivery_rating,
            "delivery_person_id": delivery_person_id,
            "created_at": order.created_at,
            "items": [
                {
                    "id": item.id,
                    "dish_id": item.dish_id,
                    "dish_name": item.dish.name,
                    "chef_id": item.dish.chef.user_id if item.dish and item.dish.chef else None,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "special_instructions": item.special_instructions
                }
                for item in order.items
            ]
        }
        result.append(OrderResponse(**order_dict))
    
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific order.
    
    Users can only view their own orders (except managers).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permission (except managers)
    if current_user.user_type not in [UserType.MANAGER]:
        if current_user.user_type in [UserType.CUSTOMER, UserType.VIP]:
            customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
            if not customer or order.customer_id != customer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this order"
                )
    
    # Get delivery person's User ID if delivery exists
    delivery_person_id = None
    if order.delivery and order.delivery.delivery_person:
        delivery_person_id = order.delivery.delivery_person.user_id
    
    # Convert to response
    order_dict = {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status.value,
        "payment_status": order.payment_status.value,
        "subtotal": order.subtotal,
        "discount_amount": order.discount_amount,
        "delivery_fee": order.delivery_fee,
        "total_amount": order.total_amount,
        "is_vip_order": order.is_vip_order,
        "is_free_delivery": order.is_free_delivery,
        "delivery_address": order.delivery_address or "",
        "food_rating": order.food_rating,
        "delivery_rating": order.delivery_rating,
        "delivery_person_id": delivery_person_id,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "dish_id": item.dish_id,
                "dish_name": item.dish.name,
                "chef_id": item.dish.chef.user_id if item.dish and item.dish.chef else None,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "special_instructions": item.special_instructions
            }
            for item in order.items
        ]
    }
    
    return OrderResponse(**order_dict)


@router.put("/{order_id}/rate", response_model=dict)
async def rate_order(
    order_id: int,
    rating: OrderRating,
    current_user: User = Depends(require_user_type(UserType.CUSTOMER, UserType.VIP)),
    db: Session = Depends(get_db)
):
    """
    Rate an order's food quality and/or delivery service.
    
    - **food_rating**: Rating for food quality (1-5 stars)
    - **delivery_rating**: Rating for delivery service (1-5 stars)
    
    Can rate either or both. Order must be completed to rate.
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer record not found"
        )
    
    # Get order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == customer.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if order is completed
    if order.status not in [OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed/delivered orders"
        )
    
    # Rate order
    order_service = OrderService(db)
    success, message = order_service.rate_order(
        order_id=order_id,
        food_rating=rating.food_rating,
        delivery_rating=rating.delivery_rating,
        item_ratings=rating.items
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"success": True, "message": message}


@router.delete("/{order_id}", response_model=dict)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order (only if not yet in delivery).
    
    Refunds the amount to wallet.
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer record not found"
        )
    
    # Get order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == customer.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if order can be cancelled
    if order.status in [OrderStatus.IN_TRANSIT, OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order in status: {order.status.value}"
        )
    
    # Update status
    order_service = OrderService(db)
    order_service.update_order_status(order_id, OrderStatus.CANCELLED)
    
    # Refund if paid
    from ..services.payment_service import PaymentService
    payment_service = PaymentService(db)
    payment_service.refund_order(order_id)
    
    return {"success": True, "message": "Order cancelled and refunded"}

