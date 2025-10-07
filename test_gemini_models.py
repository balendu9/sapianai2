#!/usr/bin/env python3
"""
Test Gemini API models and connectivity
"""

import google.generativeai as genai
import os

# Set API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY environment variable not set!")
    print("Please set your Gemini API key:")
    print("export GEMINI_API_KEY='your-api-key-here'")
    exit(1)

genai.configure(api_key=api_key)

print("🤖 Testing Gemini API Models")
print("=" * 40)

try:
    # List available models
    print("📋 Available Models:")
    models = genai.list_models()
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✅ {model.name}")
    
    print("\n🧪 Testing Model Generation:")
    
    # Test with different model names
    test_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001", 
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-pro",
        "gemini-pro-vision"
    ]
    
    for model_name in test_models:
        try:
            print(f"\n🔍 Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, say 'AI is working' if you can hear me.")
            print(f"  ✅ {model_name}: {response.text[:50]}...")
            break  # Use the first working model
        except Exception as e:
            print(f"  ❌ {model_name}: {str(e)[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")

