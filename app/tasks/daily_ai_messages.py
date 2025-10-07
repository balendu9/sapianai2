from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from app.database import SessionLocal
from app.models.user import User
from app.models.quest import Quest, QuestStatus
from app.models.daily_ai_message import DailyAIMessage
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

# Import Celery app
from app.celery_app import celery_app

@celery_app.task
def send_daily_ai_messages():
    """Send daily AI messages to users who haven't been active"""
    db: Session = SessionLocal()
    try:
        # Get users who haven't received a daily AI message in the last 24 hours
        # and have daily AI messages enabled
        yesterday = datetime.now() - timedelta(days=1)
        
        inactive_users = db.query(User).filter(
            User.daily_ai_messages_enabled == True,
            User.last_activity < yesterday,
            (User.last_daily_ai_message.is_(None)) | (User.last_daily_ai_message < yesterday)
        ).all()
        
        logger.info(f"Found {len(inactive_users)} users for daily AI messages")
        
        ai_service = AIService()
        messages_sent = 0
        
        for user in inactive_users:
            try:
                # Get user's active quests they're participating in
                from app.models.participant import QuestParticipant
                
                user_quest_ids = db.query(QuestParticipant.quest_id).filter(
                    QuestParticipant.user_id == user.user_id
                ).subquery()
                
                active_quests = db.query(Quest).filter(
                    Quest.quest_id.in_(user_quest_ids),
                    Quest.status == QuestStatus.ACTIVE,
                    Quest.end_date > datetime.now()
                ).all()
                
                if not active_quests:
                    # No active quests, send general engagement message
                    message_content = await generate_general_engagement_message(ai_service, user)
                    quest_id = None
                else:
                    # Send quest-specific message from the character
                    quest = active_quests[0]  # Use first active quest
                    message_content = await generate_quest_engagement_message(ai_service, user, quest, db)
                    quest_id = quest.quest_id
                
                # Create daily AI message record
                daily_message = DailyAIMessage(
                    user_id=user.user_id,
                    quest_id=quest_id,
                    content=message_content,
                    message_type="daily_reminder",
                    ai_generation_metadata={
                        "generated_at": datetime.now().isoformat(),
                        "user_activity_status": "inactive",
                        "quest_context": quest_id is not None
                    }
                )
                
                db.add(daily_message)
                
                # Update user's last daily AI message timestamp
                user.last_daily_ai_message = datetime.now()
                
                messages_sent += 1
                logger.info(f"Sent daily AI message to user {user.user_id}")
                
            except Exception as e:
                logger.error(f"Failed to send daily AI message to user {user.user_id}: {e}")
                continue
        
        db.commit()
        logger.info(f"Successfully sent {messages_sent} daily AI messages")
        
        return {
            "status": "success",
            "messages_sent": messages_sent,
            "total_users_checked": len(inactive_users)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Daily AI message task failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

async def generate_general_engagement_message(ai_service: AIService, user: User) -> str:
    """Generate a mysterious engagement message for users with no active quests"""
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
    
    try:
        response = ai_service.model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate general engagement message: {e}")
        return "I sense your absence in the realm of philosophical mysteries. New enigmas have emerged that await your unique perspective. Will you return to unravel them?"

async def generate_quest_engagement_message(ai_service: AIService, user: User, quest: Quest, db: Session) -> str:
    """Generate a quest-specific engagement message from the character"""
    quest_details = quest.details or {}
    properties = quest_details.get("properties", {})
    instructions = quest_details.get("instructions", {})
    additional_text = quest_details.get("additional_text", {})
    
    character_name = properties.get("character_name", "AI Character")
    character_personality = properties.get("personality", "mysterious and wise")
    character_background = properties.get("background", "A powerful being")
    
    # Get user's participation history in this quest
    from app.models.participant import QuestParticipant
    from app.models.message import ChatMessage
    
    participant = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest.quest_id,
        QuestParticipant.user_id == user.user_id
    ).first()
    
    # Get recent conversation history
    recent_messages = db.query(ChatMessage).filter(
        ChatMessage.quest_id == quest.quest_id,
        ChatMessage.user_id == user.user_id
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
- Score: {participant.score if participant else 0}
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
    
    try:
        response = ai_service.model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate quest engagement message: {e}")
        return f"I sense your absence, {user.username or 'seeker'}. {character_name} here - the enigmas we began to unravel have deepened in your absence. What new insights await your return to our philosophical discourse?"

# Schedule the task to run daily at 2 PM UTC
@celery_app.task
def check_and_end_expired_quests():
    """Check for expired quests and end them automatically"""
    db: Session = SessionLocal()
    try:
        from app.models.quest import Quest, QuestStatus, QuestStatus
        from app.models.participant import QuestParticipant
        from datetime import datetime
        
        # Get active quests that have passed their end date
        now = datetime.now()
        expired_quests = db.query(Quest).filter(
            Quest.status == QuestStatus.ACTIVE,
            Quest.end_date < now,
            Quest.is_paused == False
        ).all()
        
        logger.info(f"Found {len(expired_quests)} expired quests to end")
        
        ended_quests = []
        
        for quest in expired_quests:
            try:
                # Get all participants for reward distribution
                participants = db.query(QuestParticipant).filter(
                    QuestParticipant.quest_id == quest.quest_id
                ).order_by(QuestParticipant.score.desc()).all()
                
                if not participants:
                    # No participants, just end the quest
                    quest.status = QuestStatus.ENDED
                    quest.is_paused = False
                    quest.paused_at = None
                    db.commit()
                    
                    ended_quests.append({
                        "quest_id": quest.quest_id,
                        "title": quest.title,
                        "participants": 0,
                        "rewards_distributed": 0
                    })
                    continue
                
                # Calculate total prize pool from quest distribution rules
                distribution_rules = quest.details.get("distribution_rules", {}) if quest.details else {}
                base_prize_pool = distribution_rules.get("base_prize_pool", 250.0)
                
                # Create reward distribution list
                rewards = []
                for i, participant in enumerate(participants):
                    # Calculate reward based on rank and score
                    if i == 0:  # First place
                        reward_amount = base_prize_pool * 0.4  # 40% to winner
                    elif i < 3:  # Top 3
                        reward_amount = base_prize_pool * 0.2  # 20% each
                    elif i < 10:  # Top 10
                        reward_amount = base_prize_pool * 0.05  # 5% each
                    else:
                        reward_amount = base_prize_pool * 0.01  # 1% each
                    
                    rewards.append({
                        "user_id": participant.user_id,
                        "quest_id": quest.quest_id,
                        "amount": reward_amount,
                        "percentage": (reward_amount / base_prize_pool) * 100,
                        "description": f"Quest completion reward - Rank {i+1}"
                    })
                
                # Distribute rewards to user wallets
                from app.models.wallet import UserWallet, WalletTransaction
                from app.schemas.wallet import RewardDistribution
                
                total_distributed = 0.0
                distribution_result = {"success": True, "distributed": []}
                
                for reward in rewards:
                    # Get or create user wallet
                    wallet = db.query(UserWallet).filter(UserWallet.user_id == reward["user_id"]).first()
                    if not wallet:
                        wallet = UserWallet(user_id=reward["user_id"], balance=0.0)
                        db.add(wallet)
                        db.commit()
                        db.refresh(wallet)
                    
                    # Create reward transaction
                    transaction = WalletTransaction(
                        wallet_id=wallet.wallet_id,
                        user_id=reward["user_id"],
                        transaction_type="reward",
                        amount=reward["amount"],
                        balance_before=wallet.balance,
                        balance_after=wallet.balance + reward["amount"],
                        status="completed",
                        quest_id=reward["quest_id"],
                        description=reward["description"],
                        metadata={
                            "quest_id": reward["quest_id"],
                            "percentage": reward["percentage"],
                            "distributed_at": datetime.now().isoformat(),
                            "source": "quest_completion"
                        },
                        processed_at=datetime.now()
                    )
                    
                    db.add(transaction)
                    
                    # Update wallet balance
                    wallet.balance += reward["amount"]
                    wallet.total_earned += reward["amount"]
                    total_distributed += reward["amount"]
                    
                    distribution_result["distributed"].append({
                        "user_id": reward["user_id"],
                        "amount": reward["amount"],
                        "percentage": reward["percentage"]
                    })
                
                db.commit()
                
                # End the quest
                quest.status = QuestStatus.ENDED
                quest.is_paused = False
                quest.paused_at = None
                
                ended_quests.append({
                    "quest_id": quest.quest_id,
                    "title": quest.title,
                    "participants": len(participants),
                    "rewards_distributed": sum(r["amount"] for r in rewards),
                    "distribution_result": distribution_result
                })
                
                logger.info(f"Ended quest {quest.quest_id} with {len(participants)} participants")
                
            except Exception as e:
                logger.error(f"Failed to end quest {quest.quest_id}: {e}")
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "ended_quests": len(ended_quests),
            "quests": ended_quests
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Quest ending task failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

@celery_app.task
def schedule_daily_ai_messages():
    """Schedule daily AI messages to run every day at 2 PM UTC"""
    from celery.schedules import crontab
    
    celery_app.conf.beat_schedule = {
        'daily-ai-messages': {
            'task': 'app.tasks.daily_ai_messages.send_daily_ai_messages',
            'schedule': crontab(hour=14, minute=0),  # 2 PM UTC
        },
        'check-expired-quests': {
            'task': 'app.tasks.daily_ai_messages.check_and_end_expired_quests',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
    }
