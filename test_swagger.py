#!/usr/bin/env python3
"""
Test script to verify Swagger documentation readiness
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_swagger_readiness():
    """Test if the API is ready for Swagger documentation"""
    try:
        # Test imports
        print("🔍 Testing imports...")
        
        # Test FastAPI app creation
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        # Test main app structure
        from app.main import app
        print("✅ Main app imported successfully")
        
        # Test router imports
        from app.routers import quests, users, leaderboard, treasury, analytics, messaging, participation, bonus, wallet, auth, daily_ai_messages
        print("✅ All routers imported successfully")
        
        # Test model imports
        from app.models import user, quest, participant, input, pool, reward, leaderboard, bonus, message, wallet, admin, daily_ai_message
        print("✅ All models imported successfully")
        
        # Test schema imports
        from app.schemas import user, quest, participant, input, pool, reward, leaderboard, bonus, message, wallet, auth, daily_ai_message
        print("✅ All schemas imported successfully")
        
        # Test service imports
        from app.services import ai_service, auth_service
        print("✅ All services imported successfully")
        
        # Check FastAPI app configuration
        print("\n🔍 Checking FastAPI app configuration...")
        print(f"✅ App title: {app.title}")
        print(f"✅ App description: {app.description}")
        print(f"✅ App version: {app.version}")
        
        # Check routes
        print("\n🔍 Checking routes...")
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{route.methods} {route.path}")
        
        print(f"✅ Total routes: {len(routes)}")
        
        # Group routes by tag
        route_groups = {}
        for route in app.routes:
            if hasattr(route, 'tags') and route.tags:
                for tag in route.tags:
                    if tag not in route_groups:
                        route_groups[tag] = 0
                    route_groups[tag] += 1
        
        print("\n📊 Route groups:")
        for tag, count in route_groups.items():
            print(f"  {tag}: {count} endpoints")
        
        # Check for missing documentation
        print("\n🔍 Checking endpoint documentation...")
        undocumented_endpoints = []
        for route in app.routes:
            if hasattr(route, 'endpoint') and hasattr(route, 'path'):
                if not hasattr(route.endpoint, '__doc__') or not route.endpoint.__doc__:
                    undocumented_endpoints.append(f"{route.path}")
        
        if undocumented_endpoints:
            print(f"⚠️  {len(undocumented_endpoints)} endpoints without docstrings:")
            for endpoint in undocumented_endpoints[:5]:  # Show first 5
                print(f"  - {endpoint}")
            if len(undocumented_endpoints) > 5:
                print(f"  ... and {len(undocumented_endpoints) - 5} more")
        else:
            print("✅ All endpoints have docstrings")
        
        print("\n🎉 Swagger readiness check completed!")
        print("📚 Swagger documentation will be available at:")
        print("  - http://localhost:8000/docs (Swagger UI)")
        print("  - http://localhost:8000/redoc (ReDoc)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_swagger_readiness()
    sys.exit(0 if success else 1)
