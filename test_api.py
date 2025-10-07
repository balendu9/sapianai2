#!/usr/bin/env python3
"""
Test script for Sapien AI-Quest API
"""
import requests
import json

# API base URL (change this to your deployed URL)
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_quests():
    """Test quests endpoint"""
    print("🔍 Testing quests endpoint...")
    response = requests.get(f"{BASE_URL}/api/quests")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_docs():
    """Test API documentation"""
    print("🔍 Testing API documentation...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {response.status_code}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("🧪 Testing Sapien AI-Quest API...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Quests Endpoint", test_quests),
        ("API Documentation", test_docs)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
        
        print("-" * 30)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API setup.")

if __name__ == "__main__":
    main()
