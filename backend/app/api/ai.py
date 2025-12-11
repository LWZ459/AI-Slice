"""
AI chat and knowledge base API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType
from ..schemas.ai import (
    QuestionRequest,
    QuestionResponse,
    AnswerRating,
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    MenuRecommendationRequest,
    AIRatingCreate,
    AIRatingResponse,
    AIRatingUpdate,
)
from ..schemas.menu import DishResponse
from ..services.ai_service import AIEngine
from ..crud.crud_ai_rating import create_rating, update_rating

router = APIRouter()


@router.post("/", response_model=AIRatingResponse)
def create_ai_rating(
    rating_in: AIRatingCreate,
    db: Session = Depends(get_db),
):
    """Create a new AI rating record."""
    return create_rating(db, rating_in)


@router.put("/{rating_id}", response_model=AIRatingResponse)
def update_ai_rating(
    rating_id: int,
    rating_in: AIRatingUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing AI rating."""
    updated = update_rating(db, rating_id, rating_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Rating not found")
    return updated


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    question_data: QuestionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Ask a question to the AI assistant.
    
    - **question**: Your question about the restaurant, menu, or policies
    
    Available to all users (including visitors).
    
    System tries local knowledge base first, then falls back to LLM if needed.
    You can rate answers from the knowledge base to improve quality.
    """
    # Get user info if authenticated (visitors can also ask)
    user_id = None  # TODO: Get from optional auth
    
    # Get client IP
    client_ip = request.client.host if request.client else None
    
    # Get or create session ID (simplified)
    session_id = request.headers.get("X-Session-ID", "anonymous")
    
    # Ask question
    ai_engine = AIEngine(db)
    answer, source, kb_id = ai_engine.answer_question(
        user_id=user_id,
        question_text=question_data.question,
        session_id=session_id,
        ip_address=client_ip
    )
    
    # Get chat log ID (last inserted)
    from ..models.ai import ChatLog
    chat_log = db.query(ChatLog).order_by(ChatLog.id.desc()).first()
    chat_log_id = chat_log.id if chat_log else 0
    
    return QuestionResponse(
        question=question_data.question,
        answer=answer,
        source=source,
        chat_log_id=chat_log_id,
        can_rate=(source == "local_kb")  # Can only rate KB answers
    )


@router.post("/rate", response_model=dict)
async def rate_answer(
    rating_data: AnswerRating,
    db: Session = Depends(get_db)
):
    """
    Rate an answer from the knowledge base.
    
    - **chat_log_id**: ID of the chat interaction
    - **rating**: Rating from 0-5 (0 = very poor, flags for manager review)
    - **feedback**: Optional feedback
    
    Ratings help improve the knowledge base quality.
    Answers rated 0-1 are automatically flagged for manager review.
    """
    ai_engine = AIEngine(db)
    success, message = ai_engine.rate_answer(
        chat_log_id=rating_data.chat_log_id,
        rating=rating_data.rating,
        feedback=rating_data.feedback
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"success": True, "message": message}


@router.get("/recommendations", response_model=List[DishResponse])
async def get_menu_recommendations(
    time_of_day: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized menu recommendations.
    
    - **time_of_day**: Optional (morning, lunch, dinner, night)
    
    Returns dishes recommended based on:
    - Your order history
    - Popular dishes
    - Time of day
    - Your preferences
    """
    context = {}
    if time_of_day:
        context["time_of_day"] = time_of_day
    
    ai_engine = AIEngine(db)
    recommendations = ai_engine.recommend_menu(
        user_id=current_user.id,
        context=context
    )
    
    return recommendations


# Knowledge Base Management (Manager only)

@router.get("/knowledge-base", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_base(
    skip: int = 0,
    limit: int = 50,
    flagged_only: bool = False,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List knowledge base entries (Manager only).
    
    - **flagged_only**: Show only entries flagged for review
    
    Used for managing and reviewing the AI knowledge base.
    """
    from ..models.ai import KnowledgeBase
    
    query = db.query(KnowledgeBase)
    
    if flagged_only:
        query = query.filter(KnowledgeBase.is_flagged == True)
    
    entries = query.order_by(KnowledgeBase.times_used.desc()).offset(skip).limit(limit).all()
    
    return entries


@router.post("/knowledge-base", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_entry(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge base entry (Manager only).
    
    - **question**: The question
    - **answer**: The answer
    - **category**: Optional category
    - **tags**: Optional comma-separated tags
    
    Adds new Q&A to the knowledge base for faster responses.
    """
    from ..models.user import Manager
    
    manager = db.query(Manager).filter(Manager.user_id == current_user.id).first()
    manager_id = manager.id if manager else None
    
    ai_engine = AIEngine(db)
    success, message, kb_id = ai_engine.add_knowledge_entry(
        question=kb_data.question,
        answer=kb_data.answer,
        category=kb_data.category,
        tags=kb_data.tags,
        created_by=manager_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Get created entry
    from ..models.ai import KnowledgeBase
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    return entry


@router.put("/knowledge-base/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_entry(
    kb_id: int,
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Update a knowledge base entry (Manager only).
    
    Used to fix or improve existing answers.
    """
    from ..models.ai import KnowledgeBase
    
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found"
        )
    
    # Update fields
    entry.question = kb_data.question
    entry.answer = kb_data.answer
    if kb_data.category:
        entry.category = kb_data.category
    if kb_data.tags:
        entry.tags = kb_data.tags
    
    # Clear flag if updated
    entry.is_flagged = False
    entry.flag_count = 0
    
    db.commit()
    db.refresh(entry)
    
    return entry


@router.delete("/knowledge-base/{kb_id}", response_model=dict)
async def delete_knowledge_entry(
    kb_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Delete a knowledge base entry (Manager only).
    
    Removes poor quality or outdated answers.
    """
    from ..models.ai import KnowledgeBase
    
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return {"success": True, "message": "Knowledge base entry deleted"}

