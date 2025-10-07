from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.admin import AdminUser
from app.schemas.auth import AdminLogin, TokenResponse, AdminResponse
from app.services.auth_service import AuthService
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Get current authenticated admin user"""
    auth_service = AuthService()
    
    # Verify token
    token_data = auth_service.verify_token(credentials.credentials)
    
    # Get admin user
    admin = auth_service.get_admin_by_id(token_data.admin_id, db)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return admin

def get_super_admin(current_admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    """Get current super admin user"""
    if not current_admin.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_admin

@router.post("/login", response_model=TokenResponse)
async def admin_login(login_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login with email and password"""
    auth_service = AuthService()
    
    # Authenticate admin
    admin = auth_service.authenticate_admin(login_data.email, login_data.password, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": admin.admin_id, "email": admin.email},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        admin=AdminResponse(
            admin_id=admin.admin_id,
            email=admin.email,
            full_name=admin.full_name,
            is_active=admin.is_active,
            is_super_admin=admin.is_super_admin,
            created_at=admin.created_at,
            last_login=admin.last_login
        )
    )

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: AdminUser = Depends(get_current_admin)):
    """Get current admin user information"""
    return AdminResponse(
        admin_id=current_admin.admin_id,
        email=current_admin.email,
        full_name=current_admin.full_name,
        is_active=current_admin.is_active,
        is_super_admin=current_admin.is_super_admin,
        created_at=current_admin.created_at,
        last_login=current_admin.last_login
    )

@router.post("/logout")
async def admin_logout(current_admin: AdminUser = Depends(get_current_admin)):
    """Admin logout (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.post("/verify-token")
async def verify_token(current_admin: AdminUser = Depends(get_current_admin)):
    """Verify if token is valid"""
    return {
        "valid": True,
        "admin_id": current_admin.admin_id,
        "email": current_admin.email
    }
