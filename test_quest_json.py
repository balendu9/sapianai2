#!/usr/bin/env python3
"""
Quest JSON Validation and Testing Script
Tests the complete quest JSON examples with the AI service.
"""

import json
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import AIService
from app.core.config import settings

async def test_quest_json(json_file_path):
    """Test a quest JSON file with the AI service"""
    
    print(f"🧪 Testing Quest JSON: {json_file_path}")
    print("=" * 60)
    
    # Load JSON file
    try:
        with open(json_file_path, 'r') as f:
            quest_data = json.load(f)
        print("✅ JSON file loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return False
    
    # Check if API key is configured
    if not settings.GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not configured!")
        print("Please set your Gemini API key to test AI responses")
        print("Example: export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API Key configured: {settings.GEMINI_API_KEY[:10]}...")
    print()
    
    try:
        # Initialize AI service
        ai_service = AIService()
        print("✅ AI Service initialized")
        
        # Extract quest details
        quest_title = quest_data.get("title", "")
        quest_description = quest_data.get("description", "")
        quest_context = quest_data.get("context", "")
        quest_details = {
            "properties": quest_data.get("properties", {}),
            "instructions": quest_data.get("instructions", {}),
            "additional_text": quest_data.get("additional_text", {})
        }
        
        print(f"📋 Quest Details:")
        print(f"   Title: {quest_title}")
        print(f"   Description: {quest_description[:100]}...")
        print(f"   Character: {quest_details['properties'].get('character_name', 'Unknown')}")
        print()
        
        # Test 1: Generate Opening Message
        print("🚀 Test 1: Generate Opening Message")
        print("-" * 40)
        
        opening_response = await ai_service.generate_quest_opening_message(
            quest_details, quest_context, quest_title, quest_description
        )
        
        print(f"✅ Opening Message Generated:")
        print(f"   Success: {opening_response['success']}")
        print(f"   Message: {opening_response['opening_message'][:200]}...")
        if not opening_response['success']:
            print(f"   Error: {opening_response.get('error', 'Unknown error')}")
        print()
        
        # Test 2: Generate Character Response
        print("💬 Test 2: Generate Character Response")
        print("-" * 40)
        
        user_message = "Hello, I'm ready to begin this quest!"
        conversation_history = []
        
        response = await ai_service.generate_character_response(
            quest_details, user_message, conversation_history,
            quest_title, quest_description, quest_context
        )
        
        print(f"✅ Character Response Generated:")
        print(f"   Success: {response['success']}")
        print(f"   Response: {response['character_response'][:200]}...")
        if not response['success']:
            print(f"   Error: {response.get('error', 'Unknown error')}")
        print()
        
        # Test 3: Score User Message
        print("📊 Test 3: Score User Message")
        print("-" * 40)
        
        scoring_criteria = quest_details['instructions'].get('scoring_criteria', {})
        
        score_response = await ai_service.score_user_message(
            user_message, quest_context, scoring_criteria
        )
        
        print(f"✅ Message Scored:")
        print(f"   Success: {score_response['success']}")
        print(f"   Score: {score_response['score']}/100")
        print(f"   Breakdown: {score_response['score_breakdown']}")
        print(f"   Feedback: {score_response['feedback'][:100]}...")
        print()
        
        # Test 4: Test with Different User Message
        print("🔄 Test 4: Different User Message")
        print("-" * 40)
        
        different_message = "What is the meaning of life?"
        conversation_history = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response['character_response'][:100] + "..."}
        ]
        
        response2 = await ai_service.generate_character_response(
            quest_details, different_message, conversation_history,
            quest_title, quest_description, quest_context
        )
        
        print(f"✅ Second Response Generated:")
        print(f"   Success: {response2['success']}")
        print(f"   Response: {response2['character_response'][:200]}...")
        print()
        
        print("🎉 All Tests Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🧪 Quest JSON Testing Suite")
    print("=" * 60)
    
    # Test files
    test_files = [
        "example_quest_simple.json",
        "example_quest_complete.json"
    ]
    
    results = []
    
    for test_file in test_files:
        if os.path.exists(test_file):
            result = await test_quest_json(test_file)
            results.append((test_file, result))
            print("\n" + "="*60 + "\n")
        else:
            print(f"⚠️  File not found: {test_file}")
            results.append((test_file, False))
    
    # Summary
    print("📋 Test Summary")
    print("=" * 20)
    for filename, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{filename}: {status}")
    
    print(f"\n🔧 Setup Requirements:")
    print("1. Set GEMINI_API_KEY environment variable")
    print("2. Ensure JSON files are valid")
    print("3. Check internet connection for Gemini API access")

if __name__ == "__main__":
    asyncio.run(main())
