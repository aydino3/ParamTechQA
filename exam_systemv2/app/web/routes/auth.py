from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.core.deps import get_current_user
from app.models.user import User
from app.web.templates_helper import render_template

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return render_template("auth/login.html", request=request)


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    auth_service = AuthService(db)
    try:
        user = auth_service.authenticate(username, password)
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        return render_template("auth/login.html", request=request, error="Invalid username or password")


@router.get("/logout")
async def logout(request: Request):
    """Logout."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Dashboard (role-based)."""
    if current_user.role.value == "teacher":
        return RedirectResponse(url="/teacher/dashboard", status_code=status.HTTP_302_FOUND)
    elif current_user.role.value == "student":
        return RedirectResponse(url="/student/dashboard", status_code=status.HTTP_302_FOUND)
    elif current_user.role.value == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

