"""
CRUD operations for AI ratings.
"""
from sqlalchemy.orm import Session

from ..models.ai import AIRating
from ..schemas.ai import AIRatingCreate, AIRatingUpdate


def create_rating(db: Session, rating_in: AIRatingCreate) -> AIRating:
    """Create a new AI rating record."""
    db_rating = AIRating(
        chat_log_id=rating_in.chat_log_id,
        rating=rating_in.rating,
        feedback=rating_in.feedback,
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def update_rating(db: Session, rating_id: int, rating_in: AIRatingUpdate) -> AIRating | None:
    """Update an existing AI rating; returns None if not found."""
    rating = db.query(AIRating).filter(AIRating.id == rating_id).first()
    if not rating:
        return None

    if rating_in.rating is not None:
        rating.rating = rating_in.rating
    if rating_in.feedback is not None:
        rating.feedback = rating_in.feedback

    db.commit()
    db.refresh(rating)
    return rating

