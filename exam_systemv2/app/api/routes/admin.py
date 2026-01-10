from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.user_service import UserService
from app.services.admin_service import AdminService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse
from app.core.deps import require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new user. Only admins can create users."""
    service = UserService(db)
    return service.create_user(current_user, user)


@router.get("/users", response_model=PaginatedResponse[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    sort: Optional[str] = Query("created_at", description="Field to sort by (created_at, username)"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List users with pagination and sorting. Only admins can list all users."""
    service = UserService(db)
    skip = (page - 1) * page_size
    users, total = service.list_users(current_user, skip, page_size, role, sort, order)
    return PaginatedResponse.create(users, total, page, page_size)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get user by ID. Only admins can view any user."""
    service = UserService(db)
    return service.get_user(current_user, user_id)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update user. Only admins can update users."""
    service = UserService(db)
    return service.update_user(current_user, user_id, user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete user. Only admins can delete users."""
    service = UserService(db)
    return service.delete_user(current_user, user_id)


@router.post("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Activate a user. Only admins can activate users."""
    service = UserService(db)
    return service.activate_user(current_user, user_id)


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Deactivate a user. Only admins can deactivate users."""
    service = UserService(db)
    return service.deactivate_user(current_user, user_id)


@router.get("/stats")
def get_system_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get system statistics. Only admins can access. Cached for 5 minutes."""
    from app.core.cache import cache_result
    
    @cache_result(ttl_seconds=300)  # Cache for 5 minutes
    def _get_stats():
        service = AdminService(db)
        return service.get_system_stats(current_user)
    
    return _get_stats()


@router.get("/reports")
def get_reports(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get system reports. Only admins can access."""
    service = AdminService(db)
    return service.get_reports(current_user)

