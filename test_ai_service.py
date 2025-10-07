#!/usr/bin/env python3
"""
AI Service Test Script
Tests all AI service functionality to ensure everything is working properly.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import AIService
from app.core.config import settings

async def test_ai_service():
    """Test all AI service functions"""
    
    print("🤖 AI Service Test Suite")
    print("=" * 50)
    
    # Check if API key is configured
    if not settings.GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not configured!")
        print("Please set your Gemini API key in environment variables or .env file")
        print("Example: export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API Key configured: {settings.GEMINI_API_KEY[:10]}...")
    print(f"✅ Model: {settings.GEMINI_MODEL}")
    print()
    
    try:
        # Initialize AI service
        print("🔧 Initializing AI Service...")
        ai_service = AIService()
        print("✅ AI Service initialized successfully")
        print()
        
        # Test 1: Generate Character Response
        print("📝 Test 1: Generate Character Response")
        print("-" * 30)
        
        quest_details = {
            "properties": {
                "character_name": "The Oracle",
                "personality": "mysterious and wise",
                "background": "Ancient being of knowledge",
                "character_quirks": ["speaks in riddles", "loves philosophical questions"],
                "special_abilities": ["foresight", "wisdom"]
            },
            "instructions": {
                "speaking_style": "poetic and enigmatic",
                "hints_style": "cryptic and mysterious",
                "interaction_style": "challenging and thought-provoking",
                "example_responses": [
                    "The path you seek lies within the question itself...",
                    "Wisdom comes not from answers, but from understanding the question."
                ]
            },
            "additional_text": {
                "backstory": "The Oracle has guided seekers for millennia through philosophical challenges."
            }
        }
        
        user_message = "What is the meaning of life?"
        conversation_history = [
            {"role": "user", "content": "Hello, Oracle"},
            {"role": "assistant", "content": "Greetings, seeker. What wisdom do you seek?"}
        ]
        
        response = await ai_service.generate_character_response(
            quest_details, user_message, conversation_history,
            quest_title="The Oracle's Challenge",
            quest_description="A philosophical quest with an AI oracle",
            quest_context="You encounter a mysterious oracle who challenges your thinking"
        )
        
        print(f"✅ Character Response Generated:")
        print(f"   Success: {response['success']}")
        print(f"   Response: {response['character_response'][:100]}...")
        if not response['success']:
            print(f"   Error: {response.get('error', 'Unknown error')}")
        print()
        
        # Test 2: Score User Message
        print("📊 Test 2: Score User Message")
        print("-" * 30)
        
        quest_context = "A philosophical quest about the nature of existence"
        scoring_criteria = {
            "creativity": 0.3,
            "depth": 0.4,
            "originality": 0.2,
            "emotional_intelligence": 0.1,
            "philosophical_insight": 0.0
        }
        
        score_response = await ai_service.score_user_message(
            user_message, quest_context, scoring_criteria
        )
        
        print(f"✅ Message Scored:")
        print(f"   Success: {score_response['success']}")
        print(f"   Score: {score_response['score']}/100")
        print(f"   Breakdown: {score_response['score_breakdown']}")
        print(f"   Feedback: {score_response['feedback'][:100]}...")
        if not score_response['success']:
            print(f"   Error: {score_response.get('error', 'Unknown error')}")
        print()
        
        # Test 3: Generate Quest Opening Message
        print("🚀 Test 3: Generate Quest Opening Message")
        print("-" * 30)
        
        quest_context = "A mystical journey through the realm of philosophical questions"
        
        opening_response = await ai_service.generate_quest_opening_message(
            quest_details, quest_context, "The Oracle's Challenge", "A philosophical quest with an AI oracle"
        )
        
        print(f"✅ Opening Message Generated:")
        print(f"   Success: {opening_response['success']}")
        print(f"   Message: {opening_response['opening_message'][:150]}...")
        if not opening_response['success']:
            print(f"   Error: {opening_response.get('error', 'Unknown error')}")
        print()
        
        # Test 4: Test with different character types
        print("🎭 Test 4: Different Character Types")
        print("-" * 30)
        
        # Test with a different character
        different_quest_details = {
            "properties": {
                "character_name": "The Warrior Sage",
                "personality": "bold and direct",
                "background": "Battle-tested philosopher",
                "character_quirks": ["speaks in metaphors", "challenges directly"],
                "special_abilities": ["battle wisdom", "strategic thinking"]
            },
            "instructions": {
                "speaking_style": "direct and powerful",
                "hints_style": "challenging and confrontational",
                "interaction_style": "aggressive and motivating",
                "example_responses": [
                    "Face your fears head-on!",
                    "True strength comes from within!"
                ]
            },
            "additional_text": {
                "backstory": "A warrior who found wisdom through battle and now teaches others."
            }
        }
        
        warrior_response = await ai_service.generate_character_response(
            different_quest_details, "How do I overcome my fears?", [],
            quest_title="The Warrior's Path",
            quest_description="A quest about courage and overcoming fears",
            quest_context="A battle-tested warrior teaches about facing fears"
        )
        
        print(f"✅ Warrior Character Response:")
        print(f"   Success: {warrior_response['success']}")
        print(f"   Response: {warrior_response['character_response'][:100]}...")
        print()
        
        # Test 5: Error handling
        print("🛡️ Test 5: Error Handling")
        print("-" * 30)
        
        # Test with empty quest details
        empty_response = await ai_service.generate_character_response(
            {}, "Test message", []
        )
        
        print(f"✅ Empty Quest Details Test:")
        print(f"   Success: {empty_response['success']}")
        print(f"   Response: {empty_response['character_response'][:100]}...")
        print()
        
        print("🎉 All AI Service Tests Completed!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        print("This indicates a fundamental issue with the AI service setup.")
        return False

async def test_api_endpoints():
    """Test AI service through API endpoints"""
    
    print("\n🌐 API Endpoint Tests")
    print("=" * 50)
    
    import requests
    import json
    
    base_url = "http://localhost:8000"
    
    # Test quest creation with AI
    print("📝 Test: Create Quest with AI Opening Message")
    print("-" * 40)
    
    quest_data = {
        "title": "Test Quest - AI Integration",
        "description": "Testing AI service integration",
        "context": "A test quest to verify AI functionality",
        "properties": {
            "character_name": "Test Oracle",
            "personality": "helpful and testing",
            "background": "AI testing character"
        },
        "instructions": {
            "speaking_style": "clear and helpful",
            "hints_style": "direct and informative",
            "interaction_style": "friendly and supportive"
        },
        "additional_text": {
            "backstory": "A character designed for testing AI functionality"
        },
        "distribution_rules": {
            "1": 50.0,
            "2-13": 40.0,
            "14-50": 10.0
        },
        "initial_pool": 1000.0,
        "treasury_percentage": 10.0,
        "user_percentage": 90.0
    }
    
    try:
        # Create quest
        response = requests.post(f"{base_url}/api/quests/json", json=quest_data)
        
        if response.status_code == 200:
            quest = response.json()
            print(f"✅ Quest created successfully: {quest['quest_id']}")
            print(f"   Title: {quest['title']}")
            
            # Test messaging endpoint
            print("\n💬 Test: Send Message to Quest")
            print("-" * 30)
            
            message_data = {
                "user_id": "test_user_123",
                "user_message": "Hello, Test Oracle! How are you today?"
            }
            
            message_response = requests.post(
                f"{base_url}/api/messaging/quest/{quest['quest_id']}/message",
                json=message_data
            )
            
            if message_response.status_code == 200:
                message_result = message_response.json()
                print(f"✅ Message sent successfully")
                print(f"   AI Response: {message_result['ai_response'][:100]}...")
                print(f"   Score: {message_result['score']}/100")
            else:
                print(f"❌ Message failed: {message_response.status_code}")
                print(f"   Error: {message_response.text}")
                
        else:
            print(f"❌ Quest creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ API test error: {str(e)}")

def main():
    """Main test function"""
    print("🧪 AI Service Comprehensive Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run AI service tests
    ai_success = asyncio.run(test_ai_service())
    
    # Run API endpoint tests
    asyncio.run(test_api_endpoints())
    
    print("\n📋 Test Summary")
    print("=" * 20)
    if ai_success:
        print("✅ AI Service: PASSED")
    else:
        print("❌ AI Service: FAILED")
    
    print("\n🔧 Setup Requirements:")
    print("1. Set GEMINI_API_KEY environment variable")
    print("2. Ensure API server is running (uvicorn app.main:app --reload)")
    print("3. Check internet connection for Gemini API access")
    print("4. Verify all dependencies are installed")

if __name__ == "__main__":
    main()
