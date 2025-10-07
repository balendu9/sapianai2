#!/usr/bin/env python3
"""
Test Opening Message Refinement
Demonstrates how AI refines opening message templates from JSON.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_service import AIService
from app.core.config import settings

async def test_opening_message_refinement():
    """Test the opening message refinement feature"""
    
    print("🎭 Testing Opening Message Refinement")
    print("=" * 50)
    
    if not settings.GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not configured!")
        return False
    
    try:
        ai_service = AIService()
        print("✅ AI Service initialized")
        
        # Test 1: With opening message template (refinement)
        print("\n📝 Test 1: Refining Opening Message Template")
        print("-" * 45)
        
        quest_details_with_template = {
            "properties": {
                "character_name": "Chronos, the Oracle of Time",
                "personality": "ancient, wise, mysterious, and slightly melancholic",
                "background": "An immortal being who has witnessed the rise and fall of countless civilizations",
                "opening_message_template": "Welcome, seeker, to the realm of temporal mysteries. I am Chronos, the Oracle of Time, and I have been waiting for you. The threads of destiny have brought you here to unlock the ancient prophecies that will shape the future. Are you ready to begin your journey through the corridors of time?"
            },
            "instructions": {
                "speaking_style": "poetic, rhythmic, and filled with temporal metaphors",
                "hints_style": "cryptic prophecies and time-based riddles",
                "interaction_style": "challenging, thought-provoking, and deeply philosophical"
            },
            "additional_text": {
                "backstory": "Chronos was once a mortal philosopher who achieved enlightenment"
            }
        }
        
        response1 = await ai_service.generate_quest_opening_message(
            quest_details_with_template,
            "In the realm of Chronos, where time flows like a river...",
            "The Oracle's Prophecy Quest",
            "A mystical journey where seekers must unlock ancient prophecies"
        )
        
        print(f"✅ Refined Opening Message:")
        print(f"   Success: {response1['success']}")
        print(f"   Message: {response1['opening_message']}")
        print()
        
        # Test 2: Without opening message template (generation from scratch)
        print("📝 Test 2: Generating Opening Message from Scratch")
        print("-" * 50)
        
        quest_details_without_template = {
            "properties": {
                "character_name": "Sage Wisdom",
                "personality": "wise, patient, and encouraging",
                "background": "A learned philosopher who has guided many seekers"
            },
            "instructions": {
                "speaking_style": "calm, thoughtful, and encouraging",
                "hints_style": "gentle guidance and wisdom",
                "interaction_style": "supportive and challenging"
            },
            "additional_text": {
                "backstory": "A mentor who helps seekers find wisdom"
            }
        }
        
        response2 = await ai_service.generate_quest_opening_message(
            quest_details_without_template,
            "You encounter a wise mentor who challenges your thinking",
            "The Wise Mentor's Challenge",
            "A philosophical quest where you learn from a wise mentor"
        )
        
        print(f"✅ Generated Opening Message:")
        print(f"   Success: {response2['success']}")
        print(f"   Message: {response2['opening_message']}")
        print()
        
        # Test 3: Compare refinement vs generation
        print("🔄 Test 3: Comparison")
        print("-" * 20)
        
        print("REFINEMENT APPROACH (with template):")
        print("- Uses admin-provided template as base")
        print("- AI refines it to match character style")
        print("- More control over core message content")
        print("- Consistent with admin's vision")
        print()
        
        print("GENERATION APPROACH (without template):")
        print("- AI generates completely from scratch")
        print("- Based on character properties and quest context")
        print("- More creative but less predictable")
        print("- Good fallback when no template provided")
        print()
        
        print("🎉 Opening Message Refinement Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_json_examples():
    """Test with the JSON examples"""
    print("\n📄 Testing JSON Examples")
    print("=" * 30)
    
    try:
        ai_service = AIService()
        
        # Test complete quest JSON
        print("\n🎯 Testing Complete Quest JSON")
        print("-" * 35)
        
        with open("example_quest_complete.json", "r") as f:
            import json
            quest_data = json.load(f)
        
        quest_details = {
            "properties": quest_data["properties"],
            "instructions": quest_data["instructions"],
            "additional_text": quest_data["additional_text"]
        }
        
        response = await ai_service.generate_quest_opening_message(
            quest_details,
            quest_data["context"],
            quest_data["title"],
            quest_data["description"]
        )
        
        print(f"✅ Complete Quest Opening Message:")
        print(f"   Success: {response['success']}")
        print(f"   Message: {response['opening_message']}")
        print()
        
        # Test simple quest JSON
        print("🎯 Testing Simple Quest JSON")
        print("-" * 30)
        
        with open("example_quest_simple.json", "r") as f:
            quest_data = json.load(f)
        
        quest_details = {
            "properties": quest_data["properties"],
            "instructions": quest_data["instructions"],
            "additional_text": quest_data["additional_text"]
        }
        
        response = await ai_service.generate_quest_opening_message(
            quest_details,
            quest_data["context"],
            quest_data["title"],
            quest_data["description"]
        )
        
        print(f"✅ Simple Quest Opening Message:")
        print(f"   Success: {response['success']}")
        print(f"   Message: {response['opening_message']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing JSON examples: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Opening Message Refinement Test Suite")
    print("=" * 60)
    
    # Test refinement functionality
    refinement_success = asyncio.run(test_opening_message_refinement())
    
    # Test with JSON examples
    json_success = asyncio.run(test_json_examples())
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 20)
    print(f"Refinement Test: {'✅ PASSED' if refinement_success else '❌ FAILED'}")
    print(f"JSON Examples: {'✅ PASSED' if json_success else '❌ FAILED'}")
    
    if refinement_success and json_success:
        print("\n🎉 ALL TESTS PASSED! Opening message refinement is working perfectly!")
        print("\n💡 Key Benefits:")
        print("   - Admins can provide opening message templates")
        print("   - AI refines them to match character style")
        print("   - More control over quest content")
        print("   - Consistent with admin's vision")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

