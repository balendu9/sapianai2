from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import uuid
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models.quest import Quest, QuestStatus
from app.models.admin import AdminUser
from app.models.message import ChatMessage
from app.schemas.quest import QuestCreate, QuestResponse, QuestUpdate
from app.routers.auth import get_current_admin
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[QuestResponse])
async def get_all_quests(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all quests, optionally filter for active ones"""
    query = db.query(Quest)
    
    if active_only:
        now = datetime.now()
        query = query.filter(
            Quest.start_date <= now,
            Quest.end_date >= now
        )
    
    quests = query.all()
    return quests

@router.get("/{quest_id}", response_model=QuestResponse)
async def get_quest_by_id(quest_id: str, db: Session = Depends(get_db)):
    """Get quest by ID"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

@router.get("/search", response_model=List[QuestResponse])
async def search_quests(
    name: str,
    db: Session = Depends(get_db)
):
    """Search quests by name"""
    quests = db.query(Quest).filter(
        Quest.title.ilike(f"%{name}%")
    ).all()
    return quests

@router.get("/active", response_model=List[QuestResponse])
async def get_active_quests(db: Session = Depends(get_db)):
    """Get only active quests"""
    now = datetime.now()
    quests = db.query(Quest).filter(
        Quest.start_date <= now,
        Quest.end_date >= now
    ).all()
    return quests

@router.post("/", response_model=QuestResponse)
async def create_quest(
    current_admin: AdminUser = Depends(get_current_admin),
    title: str = Form(...),
    description: str = Form(...),
    context: str = Form(...),
    properties: str = Form(...),  # JSON string
    instructions: str = Form(...),  # JSON string
    additional_text: str = Form(...),  # JSON string
    distribution_rules: str = Form(...),  # JSON string
    profile_image: UploadFile = File(None),
    quest_media: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Create a new quest (admin-only)"""
    
    # Parse JSON strings
    try:
        properties_dict = json.loads(properties)
        instructions_dict = json.loads(instructions)
        additional_text_dict = json.loads(additional_text)
        distribution_rules_dict = json.loads(distribution_rules)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form data")
    
    # Handle file uploads (simplified - in production use cloud storage)
    profile_image_url = None
    media_url = None
    
    try:
        if profile_image:
            # Validate file type and size
            if profile_image.size > 5 * 1024 * 1024:  # 5MB limit
                raise HTTPException(status_code=400, detail="Profile image too large (max 5MB)")
            
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if profile_image.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Invalid image type. Allowed: JPEG, PNG, GIF, WebP")
            
            # Save file and get URL (simplified)
            profile_image_url = f"uploads/{uuid.uuid4()}_{profile_image.filename}"
        
        if quest_media:
            # Validate file type and size
            if quest_media.size > 50 * 1024 * 1024:  # 50MB limit for media
                raise HTTPException(status_code=400, detail="Quest media too large (max 50MB)")
            
            allowed_media_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/webm"]
            if quest_media.content_type not in allowed_media_types:
                raise HTTPException(status_code=400, detail="Invalid media type. Allowed: JPEG, PNG, GIF, WebP, MP4, WebM")
            
            # Save file and get URL (simplified)
            media_url = f"uploads/{uuid.uuid4()}_{quest_media.filename}"
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")
    
    # Create quest
    quest = Quest(
        title=title,
        description=description,
        context=context,
        details={
            "properties": properties_dict,
            "instructions": instructions_dict,
            "additional_text": additional_text_dict
        },
        profile_image_url=profile_image_url,
        media_url=media_url,
        distribution_rules=distribution_rules_dict
    )
    
    try:
        db.add(quest)
        db.commit()
        db.refresh(quest)
        
        # Generate opening AI message for the quest
        try:
            ai_service = AIService()
            opening_response = await ai_service.generate_quest_opening_message(
                quest_details=quest.details,
                quest_context=quest.context or ""
            )
            
            if opening_response.get("success"):
                # Create opening AI message
                opening_message = ChatMessage(
                    quest_id=quest.quest_id,
                    user_id=None,  # AI message
                    content=opening_response.get("opening_message", "Welcome to this quest!"),
                    score=None
                )
                db.add(opening_message)
                db.commit()
            else:
                # Fallback opening message
                opening_message = ChatMessage(
                    quest_id=quest.quest_id,
                    user_id=None,  # AI message
                    content="Welcome to this quest! Are you ready to begin?",
                    score=None
                )
                db.add(opening_message)
                db.commit()
                
        except Exception as ai_error:
            # If AI generation fails, create a simple opening message
            opening_message = ChatMessage(
                quest_id=quest.quest_id,
                user_id=None,  # AI message
                content="Welcome to this quest! Are you ready to begin?",
                score=None
            )
            db.add(opening_message)
            db.commit()
        
        return quest
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create quest: {str(e)}")

@router.post("/json", response_model=QuestResponse)
async def create_quest_json(
    quest_data: QuestCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new quest with JSON data (better for AI and production)"""
    
    try:
        # Create quest with JSON objects directly
        # Calculate treasury and user amounts
        treasury_amount = quest_data.initial_pool * (quest_data.treasury_percentage / 100)
        user_pool_amount = quest_data.initial_pool * (quest_data.user_percentage / 100)
        
        quest = Quest(
            title=quest_data.title,
            description=quest_data.description,
            context=quest_data.context,
            details={
                "properties": quest_data.properties,
                "instructions": quest_data.instructions,
                "additional_text": quest_data.additional_text
            },
            profile_image_url=quest_data.profile_image_url,
            media_url=quest_data.media_url,
            distribution_rules={
                "initial_pool": quest_data.initial_pool,
                "treasury_percentage": quest_data.treasury_percentage,
                "user_percentage": quest_data.user_percentage,
                "treasury_amount": treasury_amount,
                "user_pool_amount": user_pool_amount,
                "rank_distribution": quest_data.distribution_rules
            },
            start_date=quest_data.start_date or datetime.now(),
            end_date=quest_data.end_date or (datetime.now() + timedelta(days=30))
        )
        
        db.add(quest)
        db.commit()
        db.refresh(quest)
        
        # Generate AI opening message
        try:
            ai_service = AIService()
            opening_response = await ai_service.generate_opening_message(quest)
            
            if opening_response.get("success"):
                # Create opening AI message
                opening_message = ChatMessage(
                    quest_id=quest.quest_id,
                    user_id=None,  # AI message
                    content=opening_response.get("opening_message", "Welcome to this quest!"),
                    score=None
                )
                db.add(opening_message)
                db.commit()
            else:
                # Fallback opening message
                opening_message = ChatMessage(
                    quest_id=quest.quest_id,
                    user_id=None,  # AI message
                    content="Welcome to this quest! Are you ready to begin?",
                    score=None
                )
                db.add(opening_message)
                db.commit()
        except Exception as ai_error:
            # Continue even if AI message generation fails
            logger.warning(f"Failed to generate AI opening message: {ai_error}")
        
        return quest
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create quest: {str(e)}")

@router.put("/{quest_id}", response_model=QuestResponse)
async def update_quest(
    quest_id: str,
    quest_update: QuestUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update quest by ID (admin-only)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Update fields
    for field, value in quest_update.dict(exclude_unset=True).items():
        setattr(quest, field, value)
    
    try:
        db.commit()
        db.refresh(quest)
        return quest
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update quest: {str(e)}")

@router.delete("/{quest_id}")
async def delete_quest(
    quest_id: str, 
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete quest by ID (admin-only)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    try:
        db.delete(quest)
        db.commit()
        return {"message": "Quest deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete quest: {str(e)}")

@router.get("/{quest_id}/status")
async def get_quest_status(quest_id: str, db: Session = Depends(get_db)):
    """Get quest status (active/ended)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    now = datetime.now()
    if quest.start_date and quest.start_date > now:
        status = "scheduled"
    elif quest.end_date and quest.end_date < now:
        status = "ended"
    elif quest.start_date and quest.start_date <= now and (not quest.end_date or quest.end_date >= now):
        status = "active"
    else:
        status = "draft"
    
    return {"quest_id": quest_id, "status": status}

@router.post("/{quest_id}/start")
async def start_quest(quest_id: str, db: Session = Depends(get_db)):
    """Start quest (admin-only)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    quest.start_date = datetime.now()
    db.commit()
    
    return {"message": "Quest started successfully"}

@router.post("/{quest_id}/end")
async def end_quest(quest_id: str, db: Session = Depends(get_db)):
    """End quest if end time has passed and distribute rewards"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check if quest has already ended
    if quest.end_date and quest.end_date < datetime.now():
        # Quest has expired, proceed with ending
        try:
            # Get all participants for reward distribution
            from app.models.participant import QuestParticipant
            participants = db.query(QuestParticipant).filter(
                QuestParticipant.quest_id == quest_id
            ).order_by(QuestParticipant.score.desc()).all()
            
            if not participants:
                return {
                    "message": "Quest ended but no participants to reward",
                    "quest_id": quest_id,
                    "ended_at": datetime.now().isoformat()
                }
            
            # Calculate total prize pool (this would come from quest settings)
            # For now, using a placeholder calculation
            total_prize_pool = 1000.0  # This should come from quest.distribution_rules
            
            # Create reward distribution list
            rewards = []
            for i, participant in enumerate(participants):
                # Calculate reward based on rank and score
                if i == 0:  # First place
                    reward_amount = total_prize_pool * 0.4  # 40% to winner
                elif i < 3:  # Top 3
                    reward_amount = total_prize_pool * 0.2  # 20% each
                elif i < 10:  # Top 10
                    reward_amount = total_prize_pool * 0.05  # 5% each
                else:
                    reward_amount = total_prize_pool * 0.01  # 1% each
                
                rewards.append({
                    "user_id": participant.user_id,
                    "quest_id": quest_id,
                    "amount": reward_amount,
                    "percentage": (reward_amount / total_prize_pool) * 100,
                    "description": f"Quest completion reward - Rank {i+1}"
                })
            
            # Distribute rewards to user wallets
            from app.routers.wallet import distribute_quest_rewards
            distribution_result = await distribute_quest_rewards(
                quest_id=quest_id,
                rewards=rewards,
                db=db
            )
            
            return {
                "message": "Quest ended successfully",
                "quest_id": quest_id,
                "ended_at": datetime.now().isoformat(),
                "participants_count": len(participants),
                "total_rewards_distributed": sum(r["amount"] for r in rewards),
                "distribution_result": distribution_result
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to end quest: {str(e)}")
    
    else:
        # Quest hasn't expired yet
        time_remaining = quest.end_date - datetime.now() if quest.end_date else None
        return {
            "message": "Quest has not ended yet",
            "quest_id": quest_id,
            "end_date": quest.end_date.isoformat() if quest.end_date else None,
            "time_remaining": str(time_remaining) if time_remaining else None
        }

@router.get("/{quest_id}/info")
async def get_quest_info(quest_id: str, db: Session = Depends(get_db)):
    """Get detailed quest information for the info modal"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Get participant count
    from app.models.participant import QuestParticipant
    participant_count = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id
    ).count()
    
    # Calculate time remaining
    now = datetime.now()
    time_remaining = None
    if quest.end_date and quest.end_date > now:
        time_diff = quest.end_date - now
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_remaining = f"{days}d {hours}h {minutes}m"
    
    # Get quest details
    quest_details = quest.details or {}
    properties = quest_details.get("properties", {})
    distribution_rules = quest.details.get("distribution_rules", {}) if quest.details else {}
    
    # Calculate prize pool (this would come from actual quest settings)
    base_prize_pool = distribution_rules.get("base_prize_pool", 250.0)
    daily_bonus_prizes = distribution_rules.get("daily_bonus_prizes", 185.44)
    top_message_prizes = distribution_rules.get("top_message_prizes", 47.59)
    
    # Get character wallet (this would be stored in quest properties)
    character_wallet = properties.get("character_wallet", "0xec93...a967")
    
    return {
        "quest_id": quest_id,
        "character": {
            "name": properties.get("character_name", "AI Character"),
            "avatar": quest.profile_image_url or "/placeholder.svg",
            "wallet": character_wallet
        },
        "status": quest.status,
        "time_left": time_remaining,
        "prize_pool": {
            "total": base_prize_pool,
            "daily_bonus": daily_bonus_prizes,
            "top_message": top_message_prizes
        },
        "participants": {
            "count": participant_count,
            "label": f"{participant_count} humans {'are playing' if quest.end_date and quest.end_date > now else 'played'}"
        },
        "rules": {
            "description": quest.description or "Quest description not available",
            "context": quest.context or "Quest context not available",
            "distribution_percentages": {
                "prize_pool": 65,
                "top_message": 5,
                "treasury": 30
            },
            "daily_bonus_time": "2pm UTC",
            "price_doubling": "Last day if no winner"
        },
        "created_at": quest.created_at.isoformat(),
        "start_date": quest.start_date.isoformat() if quest.start_date else None,
        "end_date": quest.end_date.isoformat() if quest.end_date else None
    }

@router.put("/{quest_id}/info")
async def update_quest_info(
    quest_id: str,
    quest_info_update: dict,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update quest information (admin-only)"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    try:
        # Update quest details
        if "character" in quest_info_update:
            character_data = quest_info_update["character"]
            if "name" in character_data:
                # Update character name in quest details
                quest_details = quest.details or {}
                properties = quest_details.get("properties", {})
                properties["character_name"] = character_data["name"]
                quest_details["properties"] = properties
                quest.details = quest_details
            
            if "wallet" in character_data:
                # Update character wallet in quest details
                quest_details = quest.details or {}
                properties = quest_details.get("properties", {})
                properties["character_wallet"] = character_data["wallet"]
                quest_details["properties"] = properties
                quest.details = quest_details
        
        # Update prize pool information
        if "prize_pool" in quest_info_update:
            prize_pool_data = quest_info_update["prize_pool"]
            quest_details = quest.details or {}
            distribution_rules = quest_details.get("distribution_rules", {})
            
            if "total" in prize_pool_data:
                distribution_rules["base_prize_pool"] = prize_pool_data["total"]
            if "daily_bonus" in prize_pool_data:
                distribution_rules["daily_bonus_prizes"] = prize_pool_data["daily_bonus"]
            if "top_message" in prize_pool_data:
                distribution_rules["top_message_prizes"] = prize_pool_data["top_message"]
            
            quest_details["distribution_rules"] = distribution_rules
            quest.details = quest_details
        
        # Update quest rules
        if "rules" in quest_info_update:
            rules_data = quest_info_update["rules"]
            if "description" in rules_data:
                quest.description = rules_data["description"]
            if "context" in rules_data:
                quest.context = rules_data["context"]
            
            # Update distribution percentages
            if "distribution_percentages" in rules_data:
                quest_details = quest.details or {}
                distribution_rules = quest_details.get("distribution_rules", {})
                distribution_rules.update(rules_data["distribution_percentages"])
                quest_details["distribution_rules"] = distribution_rules
                quest.details = quest_details
        
        # Update quest dates
        if "start_date" in quest_info_update:
            quest.start_date = datetime.fromisoformat(quest_info_update["start_date"])
        if "end_date" in quest_info_update:
            quest.end_date = datetime.fromisoformat(quest_info_update["end_date"])
        
        db.commit()
        db.refresh(quest)
        
        return {
            "message": "Quest information updated successfully",
            "quest_id": quest_id,
            "updated_fields": list(quest_info_update.keys())
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update quest info: {str(e)}")

@router.get("/{quest_id}/admin-info")
async def get_quest_admin_info(
    quest_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed quest information for admin dashboard"""
    # Check if quest exists
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Get participant count and details
    from app.models.participant import QuestParticipant
    participants = db.query(QuestParticipant).filter(
        QuestParticipant.quest_id == quest_id
    ).order_by(QuestParticipant.score.desc()).all()
    
    # Get quest details
    quest_details = quest.details or {}
    properties = quest_details.get("properties", {})
    distribution_rules = quest.details.get("distribution_rules", {}) if quest.details else {}
    
    return {
        "quest_id": quest_id,
        "title": quest.title,
        "description": quest.description,
        "context": quest.context,
        "character": {
            "name": properties.get("character_name", "AI Character"),
            "avatar": quest.profile_image_url,
            "wallet": properties.get("character_wallet", "0xec93...a967"),
            "personality": properties.get("personality", "mysterious and wise"),
            "background": properties.get("background", "A powerful being")
        },
        "prize_pool": {
            "base_prize_pool": distribution_rules.get("base_prize_pool", 250.0),
            "daily_bonus_prizes": distribution_rules.get("daily_bonus_prizes", 185.44),
            "top_message_prizes": distribution_rules.get("top_message_prizes", 47.59),
            "total_contributed": sum(p.score for p in participants) * 0.65  # 65% goes to prize pool
        },
        "participants": {
            "total_count": len(participants),
            "top_participants": [
                {
                    "user_id": p.user_id,
                    "score": p.score,
                    "rank": i + 1,
                    "last_reply_at": p.last_reply_at.isoformat() if p.last_reply_at else None
                }
                for i, p in enumerate(participants[:10])  # Top 10
            ]
        },
        "distribution_rules": distribution_rules,
        "quest_properties": properties,
        "created_at": quest.created_at.isoformat(),
        "start_date": quest.start_date.isoformat() if quest.start_date else None,
        "end_date": quest.end_date.isoformat() if quest.end_date else None,
        "is_active": quest.end_date and quest.end_date > datetime.now() if quest.end_date else True
    }

@router.post("/{quest_id}/pause")
async def pause_quest(
    quest_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Pause a quest (admin-only)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    if quest.status == QuestStatus.ENDED:
        raise HTTPException(status_code=400, detail="Cannot pause an ended quest")
    
    if quest.is_paused:
        raise HTTPException(status_code=400, detail="Quest is already paused")
    
    try:
        # Store original end date if not already stored
        if not quest.original_end_date and quest.end_date:
            quest.original_end_date = quest.end_date
        
        # Pause the quest
        quest.is_paused = True
        quest.paused_at = datetime.now()
        quest.status = QuestStatus.STALLED
        
        db.commit()
        
        return {
            "message": "Quest paused successfully",
            "quest_id": quest_id,
            "paused_at": quest.paused_at.isoformat(),
            "status": quest.status
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to pause quest: {str(e)}")

@router.post("/{quest_id}/resume")
async def resume_quest(
    quest_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Resume a paused quest (admin-only)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    if not quest.is_paused:
        raise HTTPException(status_code=400, detail="Quest is not paused")
    
    try:
        # Calculate paused duration
        if quest.paused_at:
            paused_duration = (datetime.now() - quest.paused_at).total_seconds()
            quest.paused_duration += int(paused_duration)
        
        # Resume the quest
        quest.is_paused = False
        quest.paused_at = None
        quest.status = QuestStatus.ACTIVE
        
        # Extend end date by paused duration
        if quest.original_end_date:
            quest.end_date = quest.original_end_date + timedelta(seconds=quest.paused_duration)
        
        db.commit()
        
        return {
            "message": "Quest resumed successfully",
            "quest_id": quest_id,
            "resumed_at": datetime.now().isoformat(),
            "status": quest.status,
            "total_paused_duration": quest.paused_duration,
            "new_end_date": quest.end_date.isoformat() if quest.end_date else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to resume quest: {str(e)}")

@router.post("/{quest_id}/end")
async def end_quest_manually(
    quest_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually end a quest (admin-only)"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    if quest.status == QuestStatus.ENDED:
        raise HTTPException(status_code=400, detail="Quest is already ended")
    
    try:
        # End the quest
        quest.status = QuestStatus.ENDED
        quest.is_paused = False
        quest.paused_at = None
        
        db.commit()
        
        return {
            "message": "Quest ended successfully",
            "quest_id": quest_id,
            "ended_at": datetime.now().isoformat(),
            "status": quest.status
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to end quest: {str(e)}")

@router.get("/{quest_id}/status")
async def get_quest_status(quest_id: str, db: Session = Depends(get_db)):
    """Get quest status and timing information"""
    quest = db.query(Quest).filter(Quest.quest_id == quest_id).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    now = datetime.now()
    
    # Calculate time remaining
    time_remaining = None
    if quest.end_date and quest.status == QuestStatus.ACTIVE:
        if quest.end_date > now:
            time_diff = quest.end_date - now
            days = time_diff.days
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_remaining = f"{days}d {hours}h {minutes}m"
        else:
            time_remaining = "Expired"
    
    return {
        "quest_id": quest_id,
        "status": quest.status,
        "is_paused": quest.is_paused,
        "paused_at": quest.paused_at.isoformat() if quest.paused_at else None,
        "paused_duration": quest.paused_duration,
        "start_date": quest.start_date.isoformat() if quest.start_date else None,
        "end_date": quest.end_date.isoformat() if quest.end_date else None,
        "original_end_date": quest.original_end_date.isoformat() if quest.original_end_date else None,
        "time_remaining": time_remaining,
        "created_at": quest.created_at.isoformat()
    }

@router.post("/check-expired-quests")
async def trigger_expired_quest_check(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually trigger expired quest check (admin-only)"""
    try:
        # Import and run the Celery task
        from app.tasks.daily_ai_messages import check_and_end_expired_quests
        
        # Run the task
        result = check_and_end_expired_quests.delay()
        
        return {
            "message": "Expired quest check triggered",
            "task_id": result.id,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger quest check: {str(e)}")
