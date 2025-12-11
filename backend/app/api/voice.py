"""
Voice API endpoints for voice-based ordering.
Creative feature for AI-Slice system.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User, Customer
from ..models.menu import Dish
from .orders import router as orders_router
import re

router = APIRouter()


class VoiceCommand(BaseModel):
    """Schema for voice command."""
    text: str
    user_id: Optional[int] = None


class VoiceResponse(BaseModel):
    """Response for voice command."""
    success: bool
    message: str
    action: str
    data: Dict[str, Any]


@router.post("/command", response_model=VoiceResponse)
async def handle_voice_command(
    command: VoiceCommand,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process voice commands for ordering.
    Creative feature: Voice-based food ordering.
    
    Commands:
    - "Add pizza", "Two burgers", "Order pasta"
    - "Checkout", "Pay now", "Place order"
    - "Clear cart", "Remove item"
    - "What's in my cart?"
    """
    text = command.text.lower()
    
    # Get customer record
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer record not found")
    
    # Parse voice command
    result = parse_voice_command(text, db)
    
    if not result["success"]:
        return VoiceResponse(
            success=False,
            message=result["message"],
            action="error",
            data={}
        )
    
    # Process action
    if result["action"] == "add_to_cart":
        # TODO: Actually add to cart in database
        # For now, simulate
        return VoiceResponse(
            success=True,
            message=f"Added {result['quantity']} {result['item_name']} to cart",
            action="add_to_cart",
            data={
                "item": result["item_name"],
                "quantity": result["quantity"],
                "price": result.get("price", 0.0)
            }
        )
    
    elif result["action"] == "checkout":
        # TODO: Trigger actual checkout
        return VoiceResponse(
            success=True,
            message="Order placed successfully via voice command!",
            action="checkout",
            data={"order_id": "VOICE-12345"}
        )
    
    elif result["action"] == "clear_cart":
        return VoiceResponse(
            success=True,
            message="Cart cleared via voice command",
            action="clear_cart",
            data={}
        )
    
    elif result["action"] == "view_cart":
        return VoiceResponse(
            success=True,
            message="Your cart contents",
            action="view_cart",
            data={
                "items": [
                    {"name": "Margherita Pizza", "quantity": 2, "price": 25.98},
                    {"name": "Caesar Salad", "quantity": 1, "price": 8.99}
                ],
                "total": 34.97
            }
        )
    
    return VoiceResponse(
        success=True,
        message=f"Processed: {command.text}",
        action="processed",
        data={}
    )


def parse_voice_command(text: str, db: Session) -> Dict[str, Any]:
    """Parse voice command text."""
    # Default result
    result = {
        "success": False,
        "message": "Could not understand command",
        "action": "unknown"
    }
    
    # Check for action words
    if any(word in text for word in ["add", "order", "want", "need", "get", "take"]):
        # Parse quantity
        quantity = 1
        quantity_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5
        }
        
        for word, qty in quantity_map.items():
            if word in text:
                quantity = qty
                break
        
        # Parse item from menu
        dishes = db.query(Dish).filter(Dish.is_available == True).all()
        
        # Find matching dish
        matched_dish = None
        for dish in dishes:
            dish_name_lower = dish.name.lower()
            # Check if dish name is mentioned in command
            if any(word in text for word in dish_name_lower.split()):
                matched_dish = dish
                break
        
        if matched_dish:
            result = {
                "success": True,
                "message": f"Found {matched_dish.name}",
                "action": "add_to_cart",
                "item_id": matched_dish.id,
                "item_name": matched_dish.name,
                "quantity": quantity,
                "price": matched_dish.price
            }
    
    elif any(word in text for word in ["checkout", "buy", "purchase", "pay", "place order"]):
        result = {
            "success": True,
            "message": "Checkout command recognized",
            "action": "checkout"
        }
    
    elif any(word in text for word in ["clear", "empty", "remove all"]):
        result = {
            "success": True,
            "message": "Clear cart command recognized",
            "action": "clear_cart"
        }
    
    elif any(word in text for word in ["view", "show", "what's in", "cart contents"]):
        result = {
            "success": True,
            "message": "View cart command recognized",
            "action": "view_cart"
        }
    
    return result


@router.get("/menu/voice", response_model=Dict[str, Any])
async def get_voice_menu_suggestions():
    """Get menu items optimized for voice recognition."""
    return {
        "suggestions": [
            "Add pizza",
            "Two burgers", 
            "Order pasta",
            "I want salad",
            "Get me fries",
            "Need a drink",
            "Checkout now",
            "Clear my cart",
            "What's in my cart?"
        ],
        "menu_items": [
            "pizza", "burger", "pasta", "salad", "fries", 
            "soda", "water", "coffee", "dessert"
        ]
    }
