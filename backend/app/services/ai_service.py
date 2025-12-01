"""
AI Service - Handles AI-powered Q&A and menu recommendations.
Based on pseudocode sections 4.4 and 4.5 from the design document.
"""
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import re

from ..models.ai import KnowledgeBase, ChatLog, QuestionRating
from ..models.menu import Dish
from ..models.order import Order
from ..core.config import settings


class AIEngine:
    """Service for AI-powered features."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def answer_question(
        self,
        user_id: Optional[int],
        question_text: str,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, str, Optional[int]]:
        """
        Answer user questions via chat.
        First try the local knowledge base, if not found use external LLM.
        
        Args:
            user_id: ID of the user (None for visitors)
            question_text: The question to answer
            session_id: Session identifier
            ip_address: IP address of the requester
        
        Returns:
            Tuple of (answer: str, source: str, kb_id: Optional[int])
        """
        # Save the question in chat log (for history and analytics)
        # We'll create the log first and update it with the answer
        
        # Search local Knowledge Base with questionText
        kb_answer = self._search_knowledge_base(question_text)
        
        if kb_answer:
            # Get kbAnswer
            answer_text = kb_answer.answer
            source = "local_kb"
            kb_id = kb_answer.id
            
            # Update KB usage stats
            kb_answer.times_used += 1
            
            # Create chat log
            chat_log = ChatLog(
                user_id=user_id,
                question=question_text,
                answer=answer_text,
                source=source,
                knowledge_base_id=kb_id,
                session_id=session_id,
                ip_address=ip_address
            )
            self.db.add(chat_log)
            self.db.commit()
            
            # Display kbAnswer to user
            # Note: Rating is prompted by the frontend
            # If rating is very low (0 or 1), it will be flagged via rate_answer method
            
            return answer_text, source, kb_id
        
        else:
            # No local answer found
            # Send questionText to external LLM service
            llm_answer = self._query_llm(question_text)
            answer_text = llm_answer
            source = "llm"
            
            # Create chat log (no rating prompted for LLM answers)
            chat_log = ChatLog(
                user_id=user_id,
                question=question_text,
                answer=answer_text,
                source=source,
                llm_model="ollama" if settings.USE_LOCAL_LLM else "openai",
                session_id=session_id,
                ip_address=ip_address
            )
            self.db.add(chat_log)
            self.db.commit()
            
            return answer_text, source, None
    
    def rate_answer(
        self,
        chat_log_id: int,
        rating: int,
        feedback: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Rate an answer from the knowledge base.
        
        Args:
            chat_log_id: ID of the chat log
            rating: Rating from 0-5 (0 = flag for review)
            feedback: Optional feedback text
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate rating
        if not (0 <= rating <= 5):
            return False, "Invalid rating. Must be between 0 and 5"
        
        # Get chat log
        chat_log = self.db.query(ChatLog).filter(ChatLog.id == chat_log_id).first()
        if not chat_log:
            return False, "Chat log not found"
        
        # Only rate answers from knowledge base
        if chat_log.source != "local_kb" or not chat_log.knowledge_base_id:
            return False, "Can only rate answers from knowledge base"
        
        # Check if already rated
        existing_rating = self.db.query(QuestionRating).filter(
            QuestionRating.chat_log_id == chat_log_id
        ).first()
        if existing_rating:
            return False, "Answer already rated"
        
        # Create rating
        question_rating = QuestionRating(
            chat_log_id=chat_log_id,
            knowledge_base_id=chat_log.knowledge_base_id,
            rating=rating,
            feedback=feedback
        )
        self.db.add(question_rating)
        
        # Update KB entry statistics
        kb_entry = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == chat_log.knowledge_base_id
        ).first()
        
        if kb_entry:
            # Recalculate average rating
            total_rating = kb_entry.average_rating * kb_entry.total_ratings
            kb_entry.total_ratings += 1
            kb_entry.average_rating = (total_rating + rating) / kb_entry.total_ratings
            
            # If rating is very low (0 or 1), flag for manager review
            if rating <= 1:
                kb_entry.is_flagged = True
                kb_entry.flag_count += 1
                # TODO: Notify manager for review
        
        self.db.commit()
        
        return True, "Rating submitted successfully"
    
    def recommend_menu(
        self,
        user_id: Optional[int] = None,
        context: Optional[Dict] = None
    ) -> List[Dish]:
        """
        Recommend dishes to the user based on popularity and user's history.
        
        Args:
            user_id: Optional user ID for personalized recommendations
            context: Optional context dict with 'time_of_day', etc.
        
        Returns:
            List of recommended dishes
        """
        # Get all dishes that are currently available
        available_dishes = self.db.query(Dish).filter(Dish.is_available == True).all()
        
        favorite_tags = []
        
        # If userId exists / user is logged in
        if user_id:
            # Load past orders of this user
            past_orders = self.db.query(Order).filter(
                Order.customer_id == user_id
            ).limit(20).all()
            
            # Extract favorite tags or categories
            tag_frequency = {}
            for order in past_orders:
                for item in order.items:
                    if item.dish.tags:
                        tags = [t.strip() for t in item.dish.tags.split(',')]
                        for tag in tags:
                            tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            
            # Get top tags
            if tag_frequency:
                sorted_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)
                favorite_tags = [tag for tag, _ in sorted_tags[:5]]
        
        # Calculate scores for each dish
        scored_dishes = []
        
        for dish in available_dishes:
            # Start with popularity score
            score = dish.times_ordered * 1.0 + dish.average_rating * 10.0
            
            # If dish.tags overlap with favoriteTags → bonus
            if dish.tags and favorite_tags:
                dish_tags = [t.strip() for t in dish.tags.split(',')]
                overlap = set(dish_tags) & set(favorite_tags)
                if overlap:
                    score += 10 * len(overlap)
            
            # If dish fits current time of day from context
            if context and 'time_of_day' in context:
                time_of_day = context['time_of_day']
                if dish.tags:
                    dish_tags = [t.strip().lower() for t in dish.tags.split(',')]
                    
                    # Simple time-based matching
                    if time_of_day == 'morning' and 'breakfast' in dish_tags:
                        score += 15
                    elif time_of_day == 'lunch' and 'lunch' in dish_tags:
                        score += 15
                    elif time_of_day == 'dinner' and 'dinner' in dish_tags:
                        score += 15
                    elif time_of_day == 'night' and 'dessert' in dish_tags:
                        score += 10
            
            scored_dishes.append((dish, score))
        
        # Sort all dishes by score from highest to lowest
        scored_dishes.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N dishes (for example N = 10)
        top_n = 10
        recommendations = [dish for dish, score in scored_dishes[:top_n]]
        
        return recommendations
    
    def _search_knowledge_base(self, question: str) -> Optional[KnowledgeBase]:
        """
        Search the knowledge base for an answer.
        Uses simple keyword matching. Can be improved with vector similarity.
        """
        # Clean and normalize question
        question_lower = question.lower().strip()
        
        # Try exact match first
        kb_entries = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.is_flagged == False
        ).all()
        
        # Simple keyword matching
        best_match = None
        best_score = 0
        
        for entry in kb_entries:
            entry_question_lower = entry.question.lower()
            
            # Calculate simple similarity score
            score = 0
            
            # Exact match gets highest score
            if question_lower == entry_question_lower:
                return entry
            
            # Check word overlap
            question_words = set(re.findall(r'\w+', question_lower))
            entry_words = set(re.findall(r'\w+', entry_question_lower))
            
            common_words = question_words & entry_words
            score = len(common_words) / max(len(question_words), len(entry_words))
            
            # Check if entry question is contained in question or vice versa
            if entry_question_lower in question_lower or question_lower in entry_question_lower:
                score += 0.5
            
            if score > best_score and score > 0.3:  # Threshold
                best_score = score
                best_match = entry
        
        return best_match
    
    def _query_llm(self, question: str) -> str:
        """
        Query external LLM service.
        This is a placeholder - actual implementation would call Ollama or OpenAI API.
        """
        # TODO: Implement actual LLM integration
        # For now, return a placeholder response
        
        if settings.USE_LOCAL_LLM:
            # Would use Ollama here
            return f"[LLM Response] This is a placeholder response to: {question}. Please configure Ollama integration."
        else:
            # Would use OpenAI here
            return f"[LLM Response] This is a placeholder response to: {question}. Please configure OpenAI API key."
    
    def add_knowledge_entry(
        self,
        question: str,
        answer: str,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Add a new entry to the knowledge base.
        
        Args:
            question: The question
            answer: The answer
            category: Category of the question
            tags: Comma-separated tags
            created_by: Manager ID who created this
        
        Returns:
            Tuple of (success: bool, message: str, kb_id: Optional[int])
        """
        kb_entry = KnowledgeBase(
            question=question,
            answer=answer,
            category=category,
            tags=tags,
            created_by=created_by
        )
        
        self.db.add(kb_entry)
        self.db.commit()
        
        return True, "Knowledge entry added successfully", kb_entry.id

