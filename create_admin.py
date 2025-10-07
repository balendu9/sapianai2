#!/usr/bin/env python3
"""
Script to create the first admin user
Run this once to set up the initial admin account
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.admin import AdminUser
from app.models import admin  # Import to register the model

def create_admin_user():
    """Create the first admin user"""
    # Create tables if they don't exist
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if any admin users exist
        existing_admin = db.query(AdminUser).first()
        if existing_admin:
            print("Admin user already exists!")
            print(f"Email: {existing_admin.email}")
            return
        
        # Create first admin user
        admin_user = AdminUser(
            email="admin@sapienai.com",
            full_name="System Administrator",
            is_active=True,
            is_super_admin=True
        )
        admin_user.set_password("admin123")  # Change this password!
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"Email: {admin_user.email}")
        print("Password: admin123")
        print("⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
