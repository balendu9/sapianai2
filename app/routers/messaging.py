from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.message import ChatMessage
from app.models.quest import Quest
from app.models.participant import QuestParticipant
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse, AIResponse
from app.services.ai_service import AIService
from app.services.credits_service import CreditsService
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()

@router.post("/{quest_id}/messages", response_model=AIResponse)
async def send_message(
    quest_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """Send message in quest (chat with AI)"""
    # Input validation
    if not message.user_message or len(message.user_message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    if len(message.user_message) > 1000:
        raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")
    
    if not message.user_id or len(message.user_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    # Check if user has credits
    credits_service = CreditsService(db)
    credit_status = credits_service.can_send_message(message.user_id, quest_id)
    
    if not credit_status["can_send"]:
        raise HTTPException(
            status_code=402, 
            detail=f"No credits available. You have {credit_status['available_credits']} credits remaining. Purchase more or watch an ad to earn credits."
        )
    
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check if user is participating in quest
    participant = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id,
        QuestParticipant.user_id == message.user_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=400, detail="User is not participating in this quest")
    
    # Save user message
    user_message = ChatMessage(
        quest_id=quest_id,
        user_id=message.user_id,
        content=message.user_message
    )
    
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Get conversation history for context
    conversation_history = db.query(ChatMessage).filter(
        ChatMessage.quest_id == quest_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    # Convert to AI service format
    history = []
    for msg in reversed(conversation_history[-5:]):  # Last 5 messages for context
        history.append({
            "role": "user" if msg.user_id else "assistant",
            "content": msg.content
        })
    
    # Initialize AI service
    ai_service = AIService()
    
    try:
        # Generate AI character response
        quest_details = quest.details or {}
        ai_response = await ai_service.generate_character_response(
            quest_details=quest_details,
            user_message=message.user_message,
            conversation_history=history,
            quest_title=quest.title or "",
            quest_description=quest.description or "",
            quest_context=quest.context or ""
        )
        
        # Check if AI response failed
        if not ai_response.get("success", False):
            raise HTTPException(
                status_code=500, 
                detail=f"AI service failed: {ai_response.get('error', 'Unknown error')}"
            )
        
        # Score the user's message
        scoring_criteria = quest_details.get("instructions", {}).get("scoring_criteria", {
            "creativity": 0.3,
            "depth": 0.4,
            "originality": 0.2,
            "emotional_intelligence": 0.1,
            "philosophical_insight": 0.0
        })
        
        score_result = await ai_service.score_user_message(
            user_message=message.user_message,
            quest_context=quest.context or "",
            scoring_criteria=scoring_criteria
        )
        
        # Check if scoring failed
        if not score_result.get("success", False):
            raise HTTPException(
                status_code=500, 
                detail=f"AI scoring failed: {score_result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    # Update user message with score and save changes
    try:
        user_message.score = score_result.get("score", 50)
        db.commit()
        
        # Update participant score
        participant.score += score_result.get("score", 50)
        participant.last_reply_at = datetime.now()
        
        # Update user's last activity
        from app.models.user import User
        user = db.query(User).filter(User.user_id == message.user_id).first()
        if user:
            user.last_activity = datetime.now()
        
        # Add to reply log
        reply_log = participant.reply_log or []
        reply_log.append({
            "message_id": user_message.message_id,
            "content": message.user_message,
            "score": score_result.get("score", 50),
            "score_breakdown": score_result.get("score_breakdown", {}),
            "timestamp": datetime.now().isoformat()
        })
        participant.reply_log = reply_log
        
        # Spend credit for sending message
        credit_result = credits_service.spend_credit(
            user_id=message.user_id,
            quest_id=quest_id,
            description="Message sent to AI"
        )
        
        if not credit_result["success"]:
            logger.warning(f"Failed to spend credit for user {message.user_id}: {credit_result.get('error')}")
        
        # Update leaderboard and check for quest end
        leaderboard_service = LeaderboardService(db)
        leaderboard_result = leaderboard_service.update_leaderboard(quest_id)
        
        if leaderboard_result.get("quest_ended"):
            logger.info(f"Quest {quest_id} ended due to 100% completion")
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update message and participant: {str(e)}")
    
    # Save AI response as a message
    try:
        ai_message = ChatMessage(
            quest_id=quest_id,
            user_id=None,  # AI message
            content=ai_response.get("character_response", "I'm having trouble responding right now."),
            score=None
        )
        
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save AI response: {str(e)}")

@router.get("/{quest_id}/messages", response_model=List[MessageResponse])
async def get_quest_messages(
    quest_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get chat history for quest including opening AI message"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Get all messages for the quest (including opening AI message)
    messages = db.query(ChatMessage).filter(
        ChatMessage.quest_id == quest_id
    ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    
    return [
        MessageResponse(
            message_id=msg.message_id,
            quest_id=msg.quest_id,
            user_id=msg.user_id,
            content=msg.content,
            score=msg.score,
            created_at=msg.created_at
        )
        for msg in messages
    ]

@router.get("/{quest_id}/messages/{user_id}", response_model=List[MessageResponse])
async def get_user_messages(
    quest_id: str,
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's message history in quest"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.quest_id == quest_id,
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return [
        MessageResponse(
            message_id=msg.message_id,
            quest_id=msg.quest_id,
            user_id=msg.user_id,
            content=msg.content,
            score=msg.score,
            created_at=msg.created_at
        )
        for msg in messages
    ]
