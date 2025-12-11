"""
Manager-specific API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type, get_password_hash
from ..models.user import User, UserType, UserStatus, Manager, Customer, Chef, DeliveryPerson
from ..models.wallet import Wallet
from ..models.reputation import Reputation, Complaint, Compliment, ComplaintStatus
from ..schemas.user import UserResponse

router = APIRouter()


# -----------------------------------------------------------------------------
# Hiring / Registration Management
# -----------------------------------------------------------------------------

@router.get("/pending-registrations", response_model=List[UserResponse])
async def list_pending_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List all pending staff registrations (Manager only).
    """
    users = db.query(User).filter(
        User.status == UserStatus.PENDING
    ).offset(skip).limit(limit).all()
    
    return users

@router.post("/approve-user/{user_id}", response_model=dict)
async def approve_user(
    user_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Approve a pending registration (Manager only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="User is not pending")
    
    user.status = UserStatus.ACTIVE
    db.commit()
    
    return {"success": True, "message": f"User {user.username} approved"}

@router.post("/reject-user/{user_id}", response_model=dict)
async def reject_user(
    user_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Reject a pending registration (Manager only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # We can delete rejected users or mark them as DEACTIVATED
    # Let's delete to keep it clean for re-registration attempts
    db.delete(user)
    db.commit()
    
    return {"success": True, "message": f"User {user.username} rejected and removed"}


@router.post("/customers/{user_id}/close", response_model=dict)
async def close_customer_account(
    user_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Close a customer account (Customer quits).
    Clears deposit and deactivates.
    """
    user = db.query(User).filter(User.id == user_id, User.user_type == UserType.CUSTOMER).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    # Clear wallet / Refund
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    refund_amount = 0.0
    if wallet:
        refund_amount = wallet.balance
        wallet.balance = 0.0
        # TODO: Record refund transaction?
        
    user.status = UserStatus.DEACTIVATED
    db.commit()
    
    return {"success": True, "message": f"Account closed. Refunded ${refund_amount:.2f}"}

@router.post("/customers/{user_id}/kick", response_model=dict)
async def kick_customer(
    user_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Kick out a customer (Blacklist).
    Clears deposit and blacklists.
    """
    user = db.query(User).filter(User.id == user_id, User.user_type == UserType.CUSTOMER).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    # Clear wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    confiscated_amount = 0.0
    if wallet:
        confiscated_amount = wallet.balance
        wallet.balance = 0.0
        
    user.status = UserStatus.BLACKLISTED
    db.commit()
    
    return {"success": True, "message": f"Customer kicked out and blacklisted. Confiscated ${confiscated_amount:.2f}"}


# -----------------------------------------------------------------------------
# Staff Management (Hire/Fire/Pay)
# -----------------------------------------------------------------------------

class StaffUpdate(BaseModel):
    salary: Optional[float] = None

class StaffResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: str
    user_type: str
    status: str
    salary: float = 0.0
    rating: float = 0.0
    
    class Config:
        from_attributes = True

@router.get("/staff", response_model=List[StaffResponse])
async def list_staff(
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List all Chefs and Delivery Personnel.
    """
    staff_users = db.query(User).filter(
        User.user_type.in_([UserType.CHEF, UserType.DELIVERY]),
        User.status != UserStatus.DEACTIVATED # Show active and suspended, maybe pending too?
    ).all()
    
    results = []
    for u in staff_users:
        salary = 0.0
        rating = 0.0
        if u.user_type == UserType.CHEF and u.chef:
            salary = u.chef.salary or 0.0
            rating = u.chef.average_rating
        elif u.user_type == UserType.DELIVERY and u.delivery_person:
            salary = u.delivery_person.salary or 0.0
            rating = u.delivery_person.average_rating
            
        results.append(StaffResponse(
            id=u.id,
            username=u.username,
            full_name=u.full_name,
            email=u.email,
            user_type=u.user_type.value,
            status=u.status.value,
            salary=salary,
            rating=rating
        ))
        
    return results

@router.post("/staff/{user_id}/fire", response_model=dict)
async def fire_staff(
    user_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Fire (Deactivate) a staff member.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.user_type not in [UserType.CHEF, UserType.DELIVERY]:
        raise HTTPException(status_code=400, detail="Can only fire staff (Chef/Delivery)")
        
    user.status = UserStatus.DEACTIVATED
    db.commit()
    
    return {"success": True, "message": f"{user.username} has been fired (deactivated)"}

@router.put("/staff/{user_id}/salary", response_model=dict)
async def update_salary(
    user_id: int,
    update: StaffUpdate,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Update salary for a staff member.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if update.salary is None or update.salary < 0:
        raise HTTPException(status_code=400, detail="Invalid salary amount")
        
    if user.user_type == UserType.CHEF and user.chef:
        user.chef.salary = update.salary
    elif user.user_type == UserType.DELIVERY and user.delivery_person:
        user.delivery_person.salary = update.salary
    else:
        raise HTTPException(status_code=400, detail="User is not a valid staff member")
        
    db.commit()
    
    return {"success": True, "message": "Salary updated", "new_salary": update.salary}


# -----------------------------------------------------------------------------
# Complaints / Compliments
# -----------------------------------------------------------------------------

@router.get("/complaints", response_model=List[dict])
async def list_complaints(
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List all complaints.
    """
    complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    
    results = []
    for c in complaints:
        results.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "status": c.status.value,
            "created_at": c.created_at,
            "complainant": c.complainant.username,
            "subject": c.subject.username,
            "order_id": c.order_id
        })
    return results

@router.put("/complaints/{complaint_id}/resolve", response_model=dict)
async def resolve_complaint(
    complaint_id: int,
    decision: str = Body(..., embed=True),
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Resolve a complaint.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = ComplaintStatus.RESOLVED
    complaint.manager_decision = decision
    complaint.manager_id = current_user.manager.id if current_user.manager else None
    
    # Update staff rating if decision is against them (implied by resolution usually)
    # Simple logic: resolving a complaint penalizes rating by 0.5
    if complaint.subject:
        subject = complaint.subject
        if subject.user_type == UserType.CHEF and subject.chef:
            subject.chef.average_rating = max(1.0, subject.chef.average_rating - 0.5)
        elif subject.user_type == UserType.DELIVERY and subject.delivery_person:
            subject.delivery_person.average_rating = max(1.0, subject.delivery_person.average_rating - 0.5)
            
    db.commit()
    return {"success": True, "message": "Complaint resolved and rating updated"}

@router.put("/compliments/{compliment_id}/acknowledge", response_model=dict)
async def acknowledge_compliment(
    compliment_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Acknowledge a compliment and boost staff rating.
    """
    compliment = db.query(Compliment).filter(Compliment.id == compliment_id).first()
    if not compliment:
        raise HTTPException(status_code=404, detail="Compliment not found")
        
    # Check if already acknowledged (using description hack for now to avoid schema change)
    if compliment.description and "[ACKNOWLEDGED]" in compliment.description:
         raise HTTPException(status_code=400, detail="Compliment already acknowledged")

    # Boost rating
    if compliment.receiver:
        receiver = compliment.receiver
        if receiver.user_type == UserType.CHEF and receiver.chef:
            receiver.chef.average_rating = min(5.0, receiver.chef.average_rating + 0.2)
        elif receiver.user_type == UserType.DELIVERY and receiver.delivery_person:
            receiver.delivery_person.average_rating = min(5.0, receiver.delivery_person.average_rating + 0.2)
    
    # Mark as acknowledged
    if compliment.description:
        compliment.description += " [ACKNOWLEDGED]"
    else:
        compliment.description = "[ACKNOWLEDGED]"
        
    db.commit()
    return {"success": True, "message": "Compliment acknowledged and rating boosted"}

@router.get("/compliments", response_model=List[dict])
async def list_compliments(
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List all compliments.
    """
    compliments = db.query(Compliment).order_by(Compliment.created_at.desc()).all()
    
    results = []
    for c in compliments:
        results.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "created_at": c.created_at,
            "giver": c.giver.username,
            "receiver": c.receiver.username,
            "order_id": c.order_id
        })
    return results


# -----------------------------------------------------------------------------
# Manager Creation (Bootstrap)
# -----------------------------------------------------------------------------

class ManagerCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = None
    secret_code: str


@router.post("/create-manager", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_manager(
    data: ManagerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a manager account.
    """
    # Check secret code
    MANAGER_SECRET = "create-manager-2025"  
    
    if data.secret_code != MANAGER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret code"
        )
    
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        user_type=UserType.MANAGER,
        status=UserStatus.ACTIVE
    )
    
    db.add(user)
    db.flush()
    
    manager = Manager(user_id=user.id, department="Operations", access_level=1)
    db.add(manager)
    
    reputation = Reputation(user_id=user.id, score=0)
    db.add(reputation)
    
    db.commit()
    db.refresh(user)
    
    return user
