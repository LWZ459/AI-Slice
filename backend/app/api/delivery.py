"""
Delivery and bidding API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType, DeliveryPerson
from ..models.delivery import Delivery, DeliveryStatus
from ..schemas.delivery import (
    DeliveryBidCreate, DeliveryBidResponse,
    DeliveryResponse, DeliveryAssignment, DeliveryStatusUpdate
)
from ..services.delivery_service import DeliveryService

router = APIRouter()


@router.get("/available", response_model=List[DeliveryResponse])
async def list_available_deliveries(
    current_user: User = Depends(require_user_type(UserType.DELIVERY, UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List deliveries available for bidding.
    
    Accessible by:
    - Delivery Personnel: To place bids
    - Managers: To view status and manage assignments
    """
    delivery_service = DeliveryService(db)
    deliveries = delivery_service.get_available_deliveries()
    
    return deliveries


@router.post("/{delivery_id}/bid", response_model=dict, status_code=status.HTTP_201_CREATED)
async def place_bid(
    delivery_id: int,
    bid_data: DeliveryBidCreate,
    current_user: User = Depends(require_user_type(UserType.DELIVERY)),
    db: Session = Depends(get_db)
):
    """
    Place a bid for a delivery (Delivery Personnel only).
    
    - **bid_amount**: Your bid amount
    - **estimated_time**: Estimated delivery time in minutes
    - **notes**: Optional notes
    
    Lowest bid typically wins (unless manager overrides).
    """
    # Get delivery person record
    delivery_person = db.query(DeliveryPerson).filter(
        DeliveryPerson.user_id == current_user.id
    ).first()
    
    if not delivery_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery person record not found"
        )
    
    # Check if available
    if not delivery_person.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are currently unavailable for deliveries"
        )
    
    # Place bid
    delivery_service = DeliveryService(db)
    success, message = delivery_service.place_bid(
        delivery_id=delivery_id,
        delivery_person_id=delivery_person.id,
        bid_amount=bid_data.bid_amount,
        estimated_time=bid_data.estimated_time,
        notes=bid_data.notes
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"success": True, "message": message}


@router.get("/{delivery_id}/bids", response_model=List[DeliveryBidResponse])
async def list_delivery_bids(
    delivery_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List all bids for a delivery (Manager only).
    
    Shows all bids sorted by amount (lowest first).
    """
    delivery_service = DeliveryService(db)
    bids = delivery_service.get_delivery_bids(delivery_id)
    
    return bids


@router.post("/{delivery_id}/assign", response_model=dict)
async def assign_delivery(
    delivery_id: int,
    assignment: DeliveryAssignment,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Assign delivery to a delivery person (Manager only).
    
    - **delivery_person_id**: ID of delivery person
    - **justification**: Required if not choosing lowest bidder
    
    System automatically assigns to lowest bidder, but manager can override.
    """
    # Get delivery
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    # Assign delivery
    delivery_service = DeliveryService(db)
    success, message, assigned_id = delivery_service.assign_agent(
        order_id=delivery.order_id,
        manager_override_delivery_person_id=assignment.delivery_person_id,
        justification=assignment.justification
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "delivery_person_id": assigned_id
    }


@router.post("/{delivery_id}/auto-assign", response_model=dict)
async def auto_assign_delivery(
    delivery_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Auto-assign delivery to lowest bidder (Manager only).
    
    Automatically selects the lowest bid without manual intervention.
    """
    # Get delivery
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    # Auto assign
    delivery_service = DeliveryService(db)
    success, message, assigned_id = delivery_service.assign_agent(
        order_id=delivery.order_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "delivery_person_id": assigned_id
    }


@router.put("/{delivery_id}/status", response_model=dict)
async def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    current_user: User = Depends(require_user_type(UserType.DELIVERY)),
    db: Session = Depends(get_db)
):
    """
    Update delivery status (Delivery Personnel only).
    
    - **status**: picked_up, in_transit, delivered
    
    Can only update deliveries assigned to you.
    """
    # Get delivery person record
    delivery_person = db.query(DeliveryPerson).filter(
        DeliveryPerson.user_id == current_user.id
    ).first()
    
    if not delivery_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery person record not found"
        )
    
    # Get delivery
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id,
        Delivery.delivery_person_id == delivery_person.id
    ).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found or not assigned to you"
        )
    
    # Convert string to enum
    try:
        new_status = DeliveryStatus[status_update.status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_update.status}"
        )
        
    # Validate transition
    if new_status == DeliveryStatus.PICKED_UP and delivery.status != DeliveryStatus.ASSIGNED:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only pick up assigned deliveries"
        )
    elif new_status == DeliveryStatus.DELIVERED and delivery.status not in [DeliveryStatus.PICKED_UP, DeliveryStatus.IN_TRANSIT]:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only deliver picked up deliveries"
        )
    
    # Update status
    delivery_service = DeliveryService(db)
    success, message = delivery_service.update_delivery_status(
        delivery_id=delivery_id,
        new_status=new_status
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"success": True, "message": message}


@router.get("/my-deliveries", response_model=List[DeliveryResponse])
async def my_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_user_type(UserType.DELIVERY)),
    db: Session = Depends(get_db)
):
    """
    Get deliveries assigned to me (Delivery Personnel only).
    
    Shows current and past deliveries.
    """
    # Get delivery person record
    delivery_person = db.query(DeliveryPerson).filter(
        DeliveryPerson.user_id == current_user.id
    ).first()
    
    if not delivery_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery person record not found"
        )
    
    deliveries = db.query(Delivery).filter(
        Delivery.delivery_person_id == delivery_person.id
    ).order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()
    
    return deliveries


@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get delivery details.
    
    Accessible to delivery personnel, managers, and the customer who placed the order.
    """
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    return delivery

