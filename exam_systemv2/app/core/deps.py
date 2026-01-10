from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import verify_password


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Get current user from session."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


def require_role(*allowed_roles: UserRole):
    """Dependency to require specific roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

