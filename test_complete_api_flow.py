#!/usr/bin/env python3
"""
Complete API Flow Test with AI Integration
Tests the entire quest creation and messaging flow with real AI responses.
"""

import requests
import json
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import AIService
from app.core.config import settings

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API server is running"""
    print("🏥 Testing API Health")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running: {data['message']}")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Docs: {data['docs']}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def create_admin_user():
    """Create an admin user for testing"""
    print("\n👤 Creating Admin User")
    print("-" * 30)
    
    admin_data = {
        "username": "test_admin",
        "email": "admin@test.com",
        "password": "testpassword123",
        "is_admin": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
        if response.status_code == 200:
            print("✅ Admin user created successfully")
            return response.json()
        elif response.status_code == 400 and "already exists" in response.text:
            print("✅ Admin user already exists")
            # Try to login instead
            return login_admin()
        else:
            print(f"❌ Failed to create admin: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return None

def login_admin():
    """Login as admin user"""
    print("\n🔐 Logging in as Admin")
    print("-" * 30)
    
    login_data = {
        "username": "test_admin",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful")
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error logging in: {e}")
        return None

def create_quest_with_ai(token):
    """Create a quest using the JSON example with AI integration"""
    print("\n🎯 Creating Quest with AI Integration")
    print("-" * 40)
    
    quest_data = {
        "title": "The Oracle's Prophecy Quest",
        "description": "A mystical journey where seekers must unlock ancient prophecies through philosophical dialogue with the Oracle of Time",
        "context": "In the realm of Chronos, where time flows like a river, the Oracle of Time guards the secrets of destiny. Only those who can engage in deep philosophical discourse can unlock the prophecies that will shape the future.",
        
        "properties": {
            "character_name": "Chronos, the Oracle of Time",
            "personality": "ancient, wise, mysterious, and slightly melancholic",
            "background": "An immortal being who has witnessed the rise and fall of countless civilizations across millennia",
            "character_quirks": [
                "speaks in riddles about time",
                "references historical events as if they happened yesterday",
                "has a habit of pausing dramatically before important revelations"
            ],
            "special_abilities": [
                "time manipulation",
                "prophetic visions",
                "ancient wisdom"
            ]
        },
        
        "instructions": {
            "speaking_style": "poetic, rhythmic, and filled with temporal metaphors",
            "hints_style": "cryptic prophecies and time-based riddles",
            "interaction_style": "challenging, thought-provoking, and deeply philosophical",
            "quest_instructions": "Guide seekers through temporal paradoxes to unlock the prophecy of the Eternal Cycle",
            "scoring_criteria": {
                "creativity": 0.25,
                "depth": 0.35,
                "originality": 0.20,
                "emotional_intelligence": 0.10,
                "philosophical_insight": 0.10
            },
            "example_responses": [
                "Time flows like a river, but what if the river flows backward?",
                "In the tapestry of eternity, your thread is but a moment, yet it weaves the pattern of all existence."
            ]
        },
        
        "additional_text": {
            "backstory": "Chronos was once a mortal philosopher who achieved enlightenment and became the guardian of temporal wisdom."
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
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/quests/json", json=quest_data, headers=headers)
        if response.status_code == 200:
            quest = response.json()
            print("✅ Quest created successfully!")
            print(f"   Quest ID: {quest['quest_id']}")
            print(f"   Title: {quest['title']}")
            print(f"   Character: {quest['details']['properties']['character_name']}")
            return quest
        else:
            print(f"❌ Quest creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating quest: {e}")
        return None

def test_messaging_with_ai(quest_id, token):
    """Test messaging with AI character"""
    print("\n💬 Testing AI Messaging")
    print("-" * 30)
    
    # Create a test user first
    user_data = {
        "username": "test_user",
        "email": "user@test.com",
        "password": "testpassword123"
    }
    
    try:
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code != 200 and "already exists" not in response.text:
            print(f"⚠️  User registration issue: {response.status_code}")
        
        # Login user
        login_response = requests.post(f"{BASE_URL}/api/auth/login", data={
            "username": "test_user",
            "password": "testpassword123"
        })
        
        if login_response.status_code == 200:
            user_token = login_response.json()["access_token"]
            print("✅ Test user authenticated")
        else:
            print("❌ User authentication failed")
            return False
        
        # Send message to quest
        message_data = {
            "user_id": "test_user",
            "user_message": "Hello Chronos, I seek wisdom about the nature of time. What can you teach me?"
        }
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/messaging/quest/{quest_id}/message",
            json=message_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Message sent successfully!")
            print(f"   AI Response: {result['ai_response'][:150]}...")
            print(f"   Score: {result['score']}/100")
            print(f"   User Balance: {result.get('user_balance', 'N/A')}")
            return True
        else:
            print(f"❌ Messaging failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing messaging: {e}")
        return False

def test_ai_service_directly():
    """Test AI service directly"""
    print("\n🤖 Testing AI Service Directly")
    print("-" * 35)
    
    if not settings.GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not configured")
        return False
    
    try:
        ai_service = AIService()
        
        # Test character response
        quest_details = {
            "properties": {
                "character_name": "Test Oracle",
                "personality": "wise and mysterious",
                "background": "A test character"
            },
            "instructions": {
                "speaking_style": "poetic and enigmatic",
                "hints_style": "cryptic and mysterious",
                "interaction_style": "challenging and thought-provoking"
            },
            "additional_text": {
                "backstory": "A test character for API testing"
            }
        }
        
        response = asyncio.run(ai_service.generate_character_response(
            quest_details, 
            "Hello, I'm testing the AI service!",
            [],
            "Test Quest",
            "A test quest for API testing",
            "Testing the AI integration"
        ))
        
        if response['success']:
            print("✅ AI Service working perfectly!")
            print(f"   Response: {response['character_response'][:100]}...")
            return True
        else:
            print(f"❌ AI Service failed: {response.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ AI Service error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Complete API Flow Test with AI Integration")
    print("=" * 60)
    
    # Test 1: API Health
    if not test_api_health():
        print("\n❌ API server is not running. Please start it first:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: AI Service Direct
    ai_working = test_ai_service_directly()
    
    # Test 3: Admin Authentication
    token = create_admin_user()
    if not token:
        print("\n❌ Cannot proceed without admin authentication")
        return
    
    # Test 4: Create Quest with AI
    quest = create_quest_with_ai(token)
    if not quest:
        print("\n❌ Cannot proceed without quest creation")
        return
    
    # Test 5: Test Messaging with AI
    messaging_working = test_messaging_with_ai(quest['quest_id'], token)
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 20)
    print(f"API Health: ✅ PASSED")
    print(f"AI Service: {'✅ PASSED' if ai_working else '❌ FAILED'}")
    print(f"Admin Auth: ✅ PASSED")
    print(f"Quest Creation: ✅ PASSED")
    print(f"AI Messaging: {'✅ PASSED' if messaging_working else '❌ FAILED'}")
    
    if ai_working and messaging_working:
        print("\n🎉 ALL TESTS PASSED! Your AI-powered quest system is working perfectly!")
        print(f"\n🔗 Test your quest at: http://localhost:8000/docs")
        print(f"   Quest ID: {quest['quest_id']}")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

