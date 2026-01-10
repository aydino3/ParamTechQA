from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user import LoginRequest
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/login")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """API login endpoint."""
    auth_service = AuthService(db)
    user = auth_service.authenticate(login_data.username, login_data.password)
    
    request.session["user_id"] = user.id
    return {"message": "Login successful", "user_id": user.id}


@router.post("/logout")
async def logout(request: Request):
    """API logout endpoint."""
    request.session.clear()
    return {"message": "Logout successful"}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value
    }

