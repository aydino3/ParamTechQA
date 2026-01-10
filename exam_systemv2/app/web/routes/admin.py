from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.core.deps import require_role
from app.models.user import User, UserRole
from app.services.admin_service import AdminService
from app.services.user_service import UserService
from app.services.subject_service import SubjectService
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.web.templates_helper import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Admin dashboard with statistics."""
    try:
        admin_service = AdminService(db)
        stats = admin_service.get_system_stats(current_user)
        return render_template(
            "admin/dashboard.html",
            request=request, user=current_user, stats=stats
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")


@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List all users."""
    try:
        service = UserService(db)
        users, _ = service.list_users(current_user, skip=0, limit=1000)
        return render_template(
            "admin/users/list.html",
            request=request, user=current_user, users=users or []
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error loading users: {str(e)}")


@router.get("/users/new", response_class=HTMLResponse)
async def new_user_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """New user page."""
    return render_template(
        "admin/users/new.html",
        request=request, user=current_user
    )


@router.post("/users/new")
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(None),
    password: str = Form(...),
    role: str = Form(...),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new user."""
    try:
        from app.schemas.user import UserCreate
        
        role_enum = UserRole[role.upper()] if hasattr(UserRole, role.upper()) else UserRole.STUDENT
        
        user_data = UserCreate(
            username=username,
            email=email if email else None,
            password=password,
            role=role_enum
        )
        
        service = UserService(db)
        service.create_user(current_user, user_data)
        
        request.session["flash_message"] = {"type": "success", "message": "User created successfully!"}
        return RedirectResponse(url="/admin/users", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error creating user: {str(e)}"}
        return RedirectResponse(url="/admin/users/new", status_code=302)


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_page(
    request: Request,
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Edit user page."""
    try:
        service = UserService(db)
        user = service.get_user(current_user, user_id)
        return render_template(
            "admin/users/edit.html",
            request=request, user=current_user, edit_user=user
        )
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/admin/users", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading user: {str(e)}"}
        return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/edit")
async def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(None),
    role: str = Form(...),
    is_active: Optional[bool] = Form(False),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update a user."""
    try:
        from app.schemas.user import UserUpdate
        
        role_enum = UserRole[role.upper()] if hasattr(UserRole, role.upper()) else UserRole.STUDENT
        
        user_data = UserUpdate(
            username=username,
            email=email if email else None,
            role=role_enum,
            is_active=is_active
        )
        
        service = UserService(db)
        service.update_user(current_user, user_id, user_data)
        
        request.session["flash_message"] = {"type": "success", "message": "User updated successfully!"}
        return RedirectResponse(url="/admin/users", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error updating user: {str(e)}"}
        return RedirectResponse(url=f"/admin/users/{user_id}/edit", status_code=302)


@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    try:
        service = UserService(db)
        service.delete_user(current_user, user_id)
        request.session["flash_message"] = {"type": "success", "message": "User deleted successfully!"}
        return RedirectResponse(url="/admin/users", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/admin/users", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error deleting user: {str(e)}"}
        return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Activate a user."""
    try:
        service = UserService(db)
        service.activate_user(current_user, user_id)
        request.session["flash_message"] = {"type": "success", "message": "User activated successfully!"}
        return RedirectResponse(url="/admin/users", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/admin/users", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error activating user: {str(e)}"}
        return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Deactivate a user."""
    try:
        service = UserService(db)
        service.deactivate_user(current_user, user_id)
        request.session["flash_message"] = {"type": "success", "message": "User deactivated successfully!"}
        return RedirectResponse(url="/admin/users", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/admin/users", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error deactivating user: {str(e)}"}
        return RedirectResponse(url="/admin/users", status_code=302)


# Subject Management Routes
@router.get("/subjects", response_class=HTMLResponse)
async def list_subjects(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
    active_only: Optional[bool] = None
):
    """List all subjects."""
    try:
        service = SubjectService(db)
        show_active_only = active_only if active_only is not None else True
        subjects = service.list_subjects(active_only=show_active_only)
        return render_template(
            "admin/subjects/list.html",
            request=request, user=current_user, subjects=subjects or [], active_only=show_active_only
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading subjects: {str(e)}")


@router.get("/subjects/new", response_class=HTMLResponse)
async def new_subject_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """New subject page."""
    return render_template(
        "admin/subjects/new.html",
        request=request, user=current_user
    )


@router.post("/subjects/new")
async def create_subject(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    is_active: Optional[bool] = Form(True),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new subject."""
    try:
        subject_data = SubjectCreate(
            name=name.strip(),
            description=description.strip() if description else None,
            is_active=is_active if is_active is not None else True
        )
        
        service = SubjectService(db)
        service.create_subject(current_user, subject_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Subject created successfully!"}
        return RedirectResponse(url="/admin/subjects", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        request.session["form_data"] = {"name": name, "description": description, "is_active": is_active}
        return RedirectResponse(url="/admin/subjects/new", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error creating subject: {str(e)}"}
        request.session["form_data"] = {"name": name, "description": description, "is_active": is_active}
        return RedirectResponse(url="/admin/subjects/new", status_code=302)


@router.get("/subjects/{subject_id}/edit", response_class=HTMLResponse)
async def edit_subject_page(
    request: Request,
    subject_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Edit subject page."""
    try:
        service = SubjectService(db)
        subject = service.get_subject(subject_id)
        return render_template(
            "admin/subjects/edit.html",
            request=request, user=current_user, subject=subject
        )
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/admin/subjects", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading subject: {str(e)}"}
        return RedirectResponse(url="/admin/subjects", status_code=302)


@router.post("/subjects/{subject_id}/edit")
async def update_subject(
    request: Request,
    subject_id: int,
    name: str = Form(...),
    description: str = Form(None),
    is_active: Optional[bool] = Form(False),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update a subject."""
    try:
        subject_data = SubjectUpdate(
            name=name.strip(),
            description=description.strip() if description else None,
            is_active=is_active if is_active is not None else None
        )
        
        service = SubjectService(db)
        service.update_subject(current_user, subject_id, subject_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Subject updated successfully!"}
        return RedirectResponse(url="/admin/subjects", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/admin/subjects/{subject_id}/edit", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error updating subject: {str(e)}"}
        return RedirectResponse(url=f"/admin/subjects/{subject_id}/edit", status_code=302)


@router.post("/subjects/{subject_id}/delete")
async def delete_subject(
    subject_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a subject."""
    try:
        service = SubjectService(db)
        service.delete_subject(current_user, subject_id)
        request.session["flash_message"] = {"type": "success", "message": "Subject deleted successfully!"}
        return RedirectResponse(url="/admin/subjects", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/admin/subjects", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error deleting subject: {str(e)}"}
        return RedirectResponse(url="/admin/subjects", status_code=302)

