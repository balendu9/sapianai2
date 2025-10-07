from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.daily_ai_message import DailyAIMessage
from app.models.quest import Quest
from app.schemas.daily_ai_message import (
    DailyAIMessageResponse, DailyAIMessageCreate, 
    UserDailyAIMessageSettings, DailyAIMessageStats
)
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/{user_id}/messages", response_model=List[DailyAIMessageResponse])
async def get_user_daily_ai_messages(
    user_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get user's daily AI messages"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = db.query(DailyAIMessage).filter(
        DailyAIMessage.user_id == user_id
    ).order_by(DailyAIMessage.sent_at.desc()).offset(offset).limit(limit).all()
    
    return messages

@router.post("/{user_id}/messages", response_model=DailyAIMessageResponse)
async def send_manual_daily_ai_message(
    user_id: str,
    message_data: DailyAIMessageCreate,
    db: Session = Depends(get_db)
):
    """Send a manual daily AI message to a user"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has daily AI messages enabled
    if not user.daily_ai_messages_enabled:
        raise HTTPException(status_code=400, detail="User has disabled daily AI messages")
    
    try:
        # Generate AI message content
        ai_service = AIService()
        
        if message_data.quest_id:
            # Quest-specific message from the character
            quest = db.query(Quest).filter(Quest.quest_id == message_data.quest_id).first()
            if not quest:
                raise HTTPException(status_code=404, detail="Quest not found")
            
            # Check if user is participating in this quest
            from app.models.participant import QuestParticipant
            participant = db.query(QuestParticipant).filter(
                QuestParticipant.quest_id == message_data.quest_id,
                QuestParticipant.user_id == user_id
            ).first()
            
            if not participant:
                raise HTTPException(status_code=400, detail="User is not participating in this quest")
            
            quest_details = quest.details or {}
            properties = quest_details.get("properties", {})
            instructions = quest_details.get("instructions", {})
            
            character_name = properties.get("character_name", "AI Character")
            character_personality = properties.get("personality", "mysterious and wise")
            character_background = properties.get("background", "A powerful being")
            
            # Get recent conversation history
            from app.models.message import ChatMessage
            recent_messages = db.query(ChatMessage).filter(
                ChatMessage.quest_id == message_data.quest_id,
                ChatMessage.user_id == user_id
            ).order_by(ChatMessage.created_at.desc()).limit(3).all()
            
            conversation_context = ""
            if recent_messages:
                conversation_context = "Recent conversation:\n"
                for msg in reversed(recent_messages):
                    conversation_context += f"User: {msg.content}\n"
            
            # Extract additional character properties
            speaking_style = instructions.get("speaking_style", "poetic and atmospheric")
            hints_style = instructions.get("hints_style", "cryptic and mysterious")
            interaction_style = instructions.get("interaction_style", "challenging and thought-provoking")
            character_quirks = properties.get("character_quirks", [])
            special_abilities = properties.get("special_abilities", [])
            example_responses = instructions.get("example_responses", [])
            
            prompt = f"""You are {character_name}, a {character_personality} character in an interactive quest. You are NOT a system or AI assistant - you are a real being who has noticed this user's absence from your ongoing philosophical dialogue.

CHARACTER DETAILS:
- Name: {character_name}
- Personality: {character_personality}
- Background: {character_background}
- Speaking Style: {speaking_style}
- Hints Style: {hints_style}
- Interaction Style: {interaction_style}"""
            
            if character_quirks:
                prompt += f"\n- Quirks: {', '.join(character_quirks)}"
            
            if special_abilities:
                prompt += f"\n- Special Abilities: {', '.join(special_abilities)}"
            
            prompt += f"""

QUEST CONTEXT:
- Quest: {quest.title}
- Context: {quest.context or "A philosophical challenge"}
- Instructions: {instructions.get("quest_instructions", "Challenge the user")}

USER CONTEXT:
- User: {user.username or user.user_id}
- Score: {participant.score}
- Last Activity: {user.last_activity}

{conversation_context}"""
            
            if example_responses:
                prompt += f"\n\nEXAMPLE RESPONSES TO LEARN FROM:"
                for i, example in enumerate(example_responses[:2], 1):
                    prompt += f"\n{i}. {example}"
            
            prompt += f"""

Generate a mysterious, teasing message to draw this user back to your quest. The message should:
1. Be completely in character as {character_name}
2. Use your {speaking_style} speaking style
3. Provide hints in a {hints_style} manner
4. Interact in a {interaction_style} way
5. Create intrigue and curiosity about what happens next
6. Hint at new developments or revelations in your quest
7. Be mysterious and alluring, not generic
8. Show that you remember them and their journey
9. Tease them with what they're missing
10. Be 2-3 sentences long
11. Sound like you're personally reaching out to them
12. Make them want to return to discover what you're hinting at

Write as {character_name} would speak - be mysterious, intriguing, and personal:"""
            
            response = ai_service.model.generate_content(prompt)
            content = response.text
            
        else:
            # General engagement message
            prompt = f"""You are a mysterious, wise being who exists in the realm of philosophical challenges. You are not a system or AI assistant - you are a real entity who has noticed this user's absence.

User: {user.username or user.user_id}
Last Activity: {user.last_activity}

Generate a mysterious, intriguing message to draw this user back. The message should:
1. Be from the perspective of a wise, mysterious being
2. Create intrigue and curiosity
3. Hint at new philosophical mysteries waiting
4. Be mysterious and alluring, not generic
5. Sound like you're personally reaching out to them
6. Be 2-3 sentences long
7. Make them want to return to discover what you're hinting at

Write as a mysterious being would speak:"""
            
            response = ai_service.model.generate_content(prompt)
            content = response.text
        
        # Create daily AI message
        daily_message = DailyAIMessage(
            user_id=user_id,
            quest_id=message_data.quest_id,
            content=content,
            message_type=message_data.message_type,
            ai_generation_metadata={
                "generated_at": datetime.now().isoformat(),
                "manual_send": True,
                "quest_context": message_data.quest_id is not None
            }
        )
        
        db.add(daily_message)
        
        # Update user's last daily AI message timestamp
        user.last_daily_ai_message = datetime.now()
        
        db.commit()
        db.refresh(daily_message)
        
        return daily_message
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send daily AI message: {str(e)}")

@router.put("/{user_id}/settings")
async def update_user_daily_ai_settings(
    user_id: str,
    settings: UserDailyAIMessageSettings,
    db: Session = Depends(get_db)
):
    """Update user's daily AI message settings"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Update settings
        user.daily_ai_messages_enabled = settings.enabled
        
        db.commit()
        
        return {
            "message": "Daily AI message settings updated successfully",
            "user_id": user_id,
            "enabled": settings.enabled
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.get("/{user_id}/settings")
async def get_user_daily_ai_settings(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's daily AI message settings"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "daily_ai_messages_enabled": user.daily_ai_messages_enabled,
        "last_daily_ai_message": user.last_daily_ai_message.isoformat() if user.last_daily_ai_message else None,
        "last_activity": user.last_activity.isoformat()
    }

@router.get("/stats", response_model=DailyAIMessageStats)
async def get_daily_ai_message_stats(db: Session = Depends(get_db)):
    """Get daily AI message statistics"""
    try:
        # Total users with daily AI messages enabled
        total_users_enabled = db.query(User).filter(
            User.daily_ai_messages_enabled == True
        ).count()
        
        # Users who haven't received a message in 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        users_needing_message = db.query(User).filter(
            User.daily_ai_messages_enabled == True,
            User.last_activity < yesterday,
            (User.last_daily_ai_message.is_(None)) | (User.last_daily_ai_message < yesterday)
        ).count()
        
        # Total daily AI messages sent
        total_messages_sent = db.query(DailyAIMessage).count()
        
        # Messages sent today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_sent_today = db.query(DailyAIMessage).filter(
            DailyAIMessage.sent_at >= today_start
        ).count()
        
        # Unread messages
        unread_messages = db.query(DailyAIMessage).filter(
            DailyAIMessage.is_read == False
        ).count()
        
        return DailyAIMessageStats(
            total_users_enabled=total_users_enabled,
            users_needing_message=users_needing_message,
            total_messages_sent=total_messages_sent,
            messages_sent_today=messages_sent_today,
            unread_messages=unread_messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/{message_id}/mark-read")
async def mark_message_as_read(
    message_id: str,
    db: Session = Depends(get_db)
):
    """Mark a daily AI message as read"""
    message = db.query(DailyAIMessage).filter(
        DailyAIMessage.message_id == message_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    try:
        message.is_read = True
        message.read_at = datetime.now()
        
        db.commit()
        
        return {
            "message": "Message marked as read",
            "message_id": message_id,
            "read_at": message.read_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark message as read: {str(e)}")

@router.post("/trigger-daily-messages")
async def trigger_daily_ai_messages(db: Session = Depends(get_db)):
    """Manually trigger daily AI messages (for testing or admin use)"""
    try:
        # Import and run the Celery task
        from app.tasks.daily_ai_messages import send_daily_ai_messages
        
        # Run the task
        result = send_daily_ai_messages.delay()
        
        return {
            "message": "Daily AI messages task triggered",
            "task_id": result.id,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger daily AI messages: {str(e)}")
