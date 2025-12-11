"""
Chef API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType
from ..models.order import Order, OrderStatus
from ..schemas.order import OrderResponse
from ..services.order_service import OrderService
from ..services.delivery_service import DeliveryService

router = APIRouter()


class OrderStatusUpdate(BaseModel):
    status: str


@router.get("/orders", response_model=List[OrderResponse])
async def list_chef_orders(
    current_user: User = Depends(require_user_type(UserType.CHEF, UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List active orders for chefs.
    
    Shows orders in PLACED or PREPARING status.
    """
    # For now, show all active orders to all chefs
    # In a real app, we might filter by dishes the chef specializes in
    orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.PLACED, OrderStatus.PREPARING])
    ).order_by(Order.created_at.asc()).all()
    
    # Convert to response format
    result = []
    for order in orders:
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
            "created_at": order.created_at,
            "items": [
                {
                    "id": item.id,
                    "dish_id": item.dish_id,
                    "dish_name": item.dish.name,
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


@router.put("/orders/{order_id}/status", response_model=dict)
async def update_order_status(
    order_id: int,
    update_data: OrderStatusUpdate,
    current_user: User = Depends(require_user_type(UserType.CHEF, UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Update order status (Chef only).
    
    Allowed transitions:
    - PLACED -> PREPARING
    - PREPARING -> READY_FOR_DELIVERY
    
    When marked READY_FOR_DELIVERY, a delivery listing is automatically created.
    """
    try:
        new_status = OrderStatus[update_data.status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {update_data.status}"
        )
    
    order_service = OrderService(db)
    order = order_service.get_order(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate transition
    if new_status == OrderStatus.PREPARING:
        if order.status != OrderStatus.PLACED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only move to PREPARING from PLACED"
            )
            
    elif new_status == OrderStatus.READY_FOR_DELIVERY:
        if order.status != OrderStatus.PREPARING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only move to READY_FOR_DELIVERY from PREPARING"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status transition for chef"
        )
    
    # Update status
    success = order_service.update_order_status(order_id, new_status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )
    
    message = f"Order status updated to {new_status.value}"
    
    # If Ready for Delivery -> Create Delivery Listing
    if new_status == OrderStatus.READY_FOR_DELIVERY:
        delivery_service = DeliveryService(db)
        
        # Mock values for now
        pickup_addr = "123 Restaurant Row, AI City"
        distance = 5.0 # Mock distance
        
        success, delivery_msg, _ = delivery_service.create_delivery_listing(
            order_id=order.id,
            pickup_address=pickup_addr,
            delivery_address=order.delivery_address or "Customer Address",
            distance=distance,
            delivery_fee=order.delivery_fee,
            bidding_duration_minutes=30
        )
        
        if success:
            message += ". Delivery listing created."
        else:
            message += f". Warning: Failed to create delivery listing: {delivery_msg}"
            
    return {"success": True, "message": message}


@router.get("/stats", response_model=dict)
async def get_chef_stats(
    current_user: User = Depends(require_user_type(UserType.CHEF)),
    db: Session = Depends(get_db)
):
    """
    Get statistics for the current chef.
    """
    chef = current_user.chef
    if not chef:
        raise HTTPException(status_code=404, detail="Chef profile not found")
        
    # Active orders (placed or preparing)
    active_orders_count = db.query(Order).filter(
        Order.status.in_([OrderStatus.PLACED, OrderStatus.PREPARING])
    ).count()
    
    # Total dishes - count actual Dish records
    from ..models.menu import Dish
    total_dishes = db.query(Dish).filter(Dish.chef_id == chef.id).count()
    
    return {
        "active_orders": active_orders_count,
        "total_dishes": total_dishes,
        "total_completed": chef.total_orders_completed,
        "average_rating": chef.average_rating
    }

