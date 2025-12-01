"""
Menu and dish management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType, Chef, Customer
from ..models.menu import Dish, DishCategory
from ..schemas.menu import (
    DishCreate, DishUpdate, DishResponse,
    DishCategoryCreate, DishCategoryResponse,
    MenuSearchRequest
)
from ..services.ai_service import AIEngine

router = APIRouter()


@router.get("/", response_model=List[DishResponse])
async def browse_menu(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    chef_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    include_special: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Browse available dishes.
    
    - **category_id**: Filter by category
    - **chef_id**: Filter by chef
    - **search**: Search in dish name and description
    - **min_price** / **max_price**: Price range filter
    - **include_special**: Include VIP-only dishes (requires VIP status)
    """
    query = db.query(Dish).filter(Dish.is_available == True)
    
    # Apply filters
    if category_id:
        query = query.filter(Dish.category_id == category_id)
    
    if chef_id:
        query = query.filter(Dish.chef_id == chef_id)
    
    if search:
        query = query.filter(
            (Dish.name.ilike(f"%{search}%")) | 
            (Dish.description.ilike(f"%{search}%"))
        )
    
    if min_price is not None:
        query = query.filter(Dish.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Dish.price <= max_price)
    
    # Filter special dishes (VIP only)
    if not include_special:
        query = query.filter(Dish.is_special == False)
    
    dishes = query.order_by(Dish.times_ordered.desc()).offset(skip).limit(limit).all()
    
    return dishes


@router.get("/recommendations", response_model=List[DishResponse])
async def get_recommendations(
    time_of_day: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized menu recommendations.
    
    - **time_of_day**: morning, lunch, dinner, night
    
    Returns recommendations based on:
    - User's order history
    - Dish popularity
    - Time of day
    - User preferences
    """
    # Get customer ID
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    
    # Create context
    context = {}
    if time_of_day:
        context["time_of_day"] = time_of_day
    
    # Get recommendations
    ai_engine = AIEngine(db)
    recommended_dishes = ai_engine.recommend_menu(
        user_id=customer.id if customer else None,
        context=context
    )
    
    return recommended_dishes


@router.get("/{dish_id}", response_model=DishResponse)
async def get_dish(
    dish_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific dish.
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    return dish


@router.post("/", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
async def create_dish(
    dish_data: DishCreate,
    current_user: User = Depends(require_user_type(UserType.CHEF)),
    db: Session = Depends(get_db)
):
    """
    Create a new dish (Chef only).
    
    Chefs can independently create and manage their dishes.
    """
    # Get chef record
    chef = db.query(Chef).filter(Chef.user_id == current_user.id).first()
    if not chef:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chef record not found"
        )
    
    # Create dish
    dish = Dish(
        chef_id=chef.id,
        name=dish_data.name,
        description=dish_data.description,
        price=dish_data.price,
        category_id=dish_data.category_id,
        image_url=dish_data.image_url,
        tags=dish_data.tags,
        is_special=dish_data.is_special,
        is_available=True
    )
    
    db.add(dish)
    
    # Update chef stats
    chef.total_dishes_created += 1
    
    db.commit()
    db.refresh(dish)
    
    return dish


@router.put("/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    current_user: User = Depends(require_user_type(UserType.CHEF)),
    db: Session = Depends(get_db)
):
    """
    Update a dish (Chef only - own dishes).
    
    Chefs can only update their own dishes.
    """
    # Get chef record
    chef = db.query(Chef).filter(Chef.user_id == current_user.id).first()
    if not chef:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chef record not found"
        )
    
    # Get dish
    dish = db.query(Dish).filter(
        Dish.id == dish_id,
        Dish.chef_id == chef.id
    ).first()
    
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found or not owned by you"
        )
    
    # Update fields
    update_data = dish_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dish, field, value)
    
    db.commit()
    db.refresh(dish)
    
    return dish


@router.delete("/{dish_id}", response_model=dict)
async def delete_dish(
    dish_id: int,
    current_user: User = Depends(require_user_type(UserType.CHEF)),
    db: Session = Depends(get_db)
):
    """
    Delete a dish (Chef only - own dishes).
    
    Actually marks as unavailable rather than deleting from database.
    """
    # Get chef record
    chef = db.query(Chef).filter(Chef.user_id == current_user.id).first()
    if not chef:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chef record not found"
        )
    
    # Get dish
    dish = db.query(Dish).filter(
        Dish.id == dish_id,
        Dish.chef_id == chef.id
    ).first()
    
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found or not owned by you"
        )
    
    # Mark as unavailable instead of deleting
    dish.is_available = False
    db.commit()
    
    return {"success": True, "message": "Dish marked as unavailable"}


# Category endpoints

@router.get("/categories/", response_model=List[DishCategoryResponse])
async def list_categories(
    db: Session = Depends(get_db)
):
    """
    List all dish categories.
    """
    categories = db.query(DishCategory).all()
    return categories


@router.post("/categories/", response_model=DishCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: DishCategoryCreate,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Create a dish category (Manager only).
    """
    # Check if category already exists
    existing = db.query(DishCategory).filter(
        DishCategory.name == category_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )
    
    category = DishCategory(
        name=category_data.name,
        description=category_data.description
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category

