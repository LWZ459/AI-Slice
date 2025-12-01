"""
Reputation management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType
from ..models.reputation import Complaint, ComplaintStatus
from ..schemas.reputation import (
    ComplaintCreate, ComplaintResponse, ComplaintDispute,
    ComplimentCreate, ComplimentResponse,
    ReputationResponse, ManagerComplaintDecision, WarningCreate
)
from ..services.reputation_service import ReputationService

router = APIRouter()


@router.post("/complaint", response_model=dict, status_code=status.HTTP_201_CREATED)
async def file_complaint(
    complaint_data: ComplaintCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    File a complaint against another user.
    
    - **subject_id**: User ID being complained about
    - **title**: Short title
    - **description**: Detailed description
    - **order_id**: Optional related order
    
    VIP complaints count double.
    All complaints go to manager for review.
    """
    # Check if complaining about self
    if complaint_data.subject_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot file complaint against yourself"
        )
    
    # Check if subject exists
    subject = db.query(User).filter(User.id == complaint_data.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # File complaint
    reputation_service = ReputationService(db)
    success, message, complaint_id = reputation_service.file_complaint(
        complainant_id=current_user.id,
        subject_id=complaint_data.subject_id,
        title=complaint_data.title,
        description=complaint_data.description,
        order_id=complaint_data.order_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "complaint_id": complaint_id
    }


@router.post("/compliment", response_model=dict, status_code=status.HTTP_201_CREATED)
async def give_compliment(
    compliment_data: ComplimentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Give a compliment to another user.
    
    - **receiver_id**: User ID receiving compliment
    - **title**: Short title
    - **description**: Optional detailed description
    - **order_id**: Optional related order
    
    VIP compliments count double.
    One compliment cancels one complaint for the receiver.
    """
    # Check if complimenting self
    if compliment_data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot compliment yourself"
        )
    
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == compliment_data.receiver_id).first()
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Give compliment
    reputation_service = ReputationService(db)
    success, message, compliment_id = reputation_service.file_compliment(
        giver_id=current_user.id,
        receiver_id=compliment_data.receiver_id,
        title=compliment_data.title,
        description=compliment_data.description,
        order_id=compliment_data.order_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "compliment_id": compliment_id
    }


@router.get("/complaints", response_model=List[ComplaintResponse])
async def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List complaints.
    
    - Customers: See complaints they filed or against them
    - Managers: See all complaints
    - **status_filter**: pending, resolved, disputed, rejected
    """
    query = db.query(Complaint)
    
    # Filter based on user type
    if current_user.user_type != UserType.MANAGER:
        query = query.filter(
            (Complaint.complainant_id == current_user.id) |
            (Complaint.subject_id == current_user.id)
        )
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = ComplaintStatus[status_filter.upper()]
            query = query.filter(Complaint.status == status_enum)
        except KeyError:
            pass
    
    complaints = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()
    
    return complaints


@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get complaint details.
    
    Can view if you're involved or if you're a manager.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check permission
    if current_user.user_type != UserType.MANAGER:
        if current_user.id not in [complaint.complainant_id, complaint.subject_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this complaint"
            )
    
    return complaint


@router.post("/complaints/{complaint_id}/dispute", response_model=dict)
async def dispute_complaint(
    complaint_id: int,
    dispute_data: ComplaintDispute,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Dispute a complaint filed against you.
    
    - **dispute_reason**: Explanation of why the complaint is unfair
    
    Manager will review and make final decision.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check if user is the subject
    if complaint.subject_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only dispute complaints against you"
        )
    
    # Check if already disputed
    if complaint.is_disputed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint already disputed"
        )
    
    # Mark as disputed
    complaint.is_disputed = True
    complaint.dispute_reason = dispute_data.dispute_reason
    complaint.status = ComplaintStatus.DISPUTED
    
    db.commit()
    
    return {"success": True, "message": "Complaint disputed. Pending manager review."}


@router.post("/complaints/{complaint_id}/decide", response_model=dict)
async def manager_decide_complaint(
    complaint_id: int,
    decision_data: ManagerComplaintDecision,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Make a decision on a complaint (Manager only).
    
    - **decision**: Explanation of decision
    - **action**: resolve, reject, warn_complainant, warn_subject
    
    Final authority on all complaints.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    from ..models.user import Manager
    manager = db.query(Manager).filter(Manager.user_id == current_user.id).first()
    
    # Record decision
    complaint.manager_decision = decision_data.decision
    complaint.manager_id = manager.id if manager else None
    from datetime import datetime
    complaint.resolved_at = datetime.utcnow()
    
    # Take action
    reputation_service = ReputationService(db)
    
    if decision_data.action == "resolve":
        complaint.status = ComplaintStatus.RESOLVED
    elif decision_data.action == "reject":
        complaint.status = ComplaintStatus.REJECTED
    elif decision_data.action == "warn_complainant":
        complaint.status = ComplaintStatus.REJECTED
        reputation_service.apply_warning(
            user_id=complaint.complainant_id,
            reason="False complaint"
        )
    elif decision_data.action == "warn_subject":
        complaint.status = ComplaintStatus.RESOLVED
        reputation_service.apply_warning(
            user_id=complaint.subject_id,
            reason=f"Complaint: {complaint.title}"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action"
        )
    
    db.commit()
    
    return {"success": True, "message": f"Complaint {decision_data.action}"}


@router.get("/{user_id}/reputation", response_model=ReputationResponse)
async def get_user_reputation(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get reputation information for a user.
    
    Anyone can view reputation of others.
    """
    from ..models.reputation import Reputation
    
    reputation = db.query(Reputation).filter(Reputation.user_id == user_id).first()
    
    if not reputation:
        # Create if doesn't exist
        reputation = Reputation(user_id=user_id, score=0)
        db.add(reputation)
        db.commit()
        db.refresh(reputation)
    
    return reputation


@router.get("/my-warnings", response_model=dict)
async def get_my_warnings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get your warning count.
    
    Shows how many warnings you have (displayed on login).
    """
    reputation_service = ReputationService(db)
    warning_count = reputation_service.check_warnings(current_user.id)
    
    from ..core.config import settings
    
    return {
        "warning_count": warning_count,
        "threshold_deregister": settings.WARNING_THRESHOLD_DEREGISTER,
        "threshold_vip_demotion": settings.WARNING_THRESHOLD_VIP_DEMOTION,
        "message": f"You have {warning_count} warning(s)"
    }


@router.post("/warn", response_model=dict)
async def issue_warning(
    warning_data: WarningCreate,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Issue a warning to a user (Manager only).
    
    - **user_id**: User to warn
    - **reason**: Reason for warning
    
    Warnings can lead to:
    - 3 warnings: Deregistration
    - 2 warnings for VIP: Demotion
    """
    # Check if user exists
    user = db.query(User).filter(User.id == warning_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Issue warning
    reputation_service = ReputationService(db)
    reputation_service.apply_warning(
        user_id=warning_data.user_id,
        reason=warning_data.reason
    )
    
    return {"success": True, "message": "Warning issued"}

