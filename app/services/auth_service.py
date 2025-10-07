from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.admin import AdminUser
from app.schemas.auth import TokenData
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for admin users"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify JWT token and return token data"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            admin_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if admin_id is None or email is None:
                raise credentials_exception
            
            token_data = TokenData(admin_id=admin_id, email=email)
            return token_data
            
        except JWTError:
            raise credentials_exception
    
    def authenticate_admin(self, email: str, password: str, db) -> Optional[AdminUser]:
        """Authenticate admin user with email and password"""
        admin = db.query(AdminUser).filter(AdminUser.email == email).first()
        
        if not admin:
            return None
        
        if not admin.is_active:
            return None
        
        if not admin.check_password(password):
            return None
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db.commit()
        
        return admin
    
    def get_admin_by_id(self, admin_id: str, db) -> Optional[AdminUser]:
        """Get admin user by ID"""
        return db.query(AdminUser).filter(AdminUser.admin_id == admin_id).first()
    
    def get_admin_by_email(self, email: str, db) -> Optional[AdminUser]:
        """Get admin user by email"""
        return db.query(AdminUser).filter(AdminUser.email == email).first()
