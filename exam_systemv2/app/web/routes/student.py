from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Any
from datetime import timezone
import json
from app.db.session import get_db
from app.services.assignment_service import AssignmentService
from app.services.attempt_service import AttemptService
from app.services.grading_service import GradingService
from app.services.student_service import StudentService
from app.core.deps import require_role
from app.models.user import User, UserRole
from app.web.templates_helper import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def student_dashboard(
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
    filter_status: str = None,
    search: str = None,
    sort_by: str = "date",
    sort_order: str = "desc"
):
    """Student dashboard with filtering and search."""
    try:
        from app.repositories.assignment_repository import AssignmentRepository
        from app.repositories.exam_repository import ExamRepository
        from app.repositories.attempt_repository import AttemptRepository
        from app.repositories.result_repository import ResultRepository
        from app.models.assignment import AssignmentStatus
        from app.models.attempt import Attempt, AttemptStatus
        
        assignment_repo = AssignmentRepository(db)
        exam_repo = ExamRepository(db)
        attempt_repo = AttemptRepository(db)
        result_repo = ResultRepository(db)
        student_service = StudentService(db)
        
        assignments = assignment_repo.list_by_student(current_user.id)
        
        # Get statistics
        stats = student_service.get_student_statistics(current_user)
        
        # Calculate average score from graded exams (optimized to avoid N+1 queries)
        # An assignment is considered "completed" if it has a submitted attempt with a released result
        # Get all attempts for this student in one query
        all_attempts = attempt_repo.list_by_student(current_user.id)
        submitted_attempts = {a.id: a for a in all_attempts if a.status == AttemptStatus.SUBMITTED}
        
        # Get all results for submitted attempts in one query
        attempt_ids = list(submitted_attempts.keys())
        all_results = {}
        if attempt_ids:
            results = result_repo.get_by_attempt_ids(attempt_ids)
            all_results = {r.attempt_id: r for r in results if r.released_at}
        
        # Build exam_id -> latest attempt mapping
        # Normalize datetime for comparison
        from app.core.utils import normalize_datetime_to_utc_aware
        
        exam_attempts_map = {}
        for attempt in submitted_attempts.values():
            exam_id = attempt.exam_id
            if exam_id not in exam_attempts_map:
                exam_attempts_map[exam_id] = attempt
            else:
                # Compare normalized datetimes
                current_started = normalize_datetime_to_utc_aware(attempt.started_at)
                existing_started = normalize_datetime_to_utc_aware(exam_attempts_map[exam_id].started_at)
                if current_started and existing_started and current_started > existing_started:
                    exam_attempts_map[exam_id] = attempt
        
        # Calculate completed assignments and average score
        completed_assignments = []
        total_percentage = 0
        count = 0
        
        for assignment in assignments:
            if assignment.exam_id in exam_attempts_map:
                latest_attempt = exam_attempts_map[assignment.exam_id]
                if latest_attempt.id in all_results:
                    completed_assignments.append(assignment)
                    total_percentage += all_results[latest_attempt.id].percentage
                    count += 1
        
        average_score = round(total_percentage / count, 2) if count > 0 else 0
        
        # Get upcoming exams
        upcoming = student_service.get_upcoming_exams(current_user)
        
        # Add exam names and attempt_ids to assignments
        assignments_data = []
        for assignment in assignments:
            try:
                exam = exam_repo.get_by_id(assignment.exam_id)
                status_value = assignment.status.value if hasattr(assignment.status, 'value') else str(assignment.status)
                assigned_at_str = assignment.assigned_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(assignment.assigned_at, 'strftime') else str(assignment.assigned_at)
                
                # Find attempt for this assignment
                attempt = attempt_repo.get_active_by_assignment(assignment.id)
                if not attempt:
                    attempt = db.query(Attempt).filter(
                        Attempt.assignment_id == assignment.id
                    ).order_by(Attempt.started_at.desc()).first()
                
                assignments_data.append({
                    'id': assignment.id,
                    'exam_id': assignment.exam_id,
                    'exam_name': exam.name if exam else f"Exam {assignment.exam_id}",
                    'status': assignment.status,
                    'status_value': status_value,
                    'assigned_at': assigned_at_str,
                    'attempt_id': attempt.id if attempt else None
                })
            except Exception as e:
                continue
        
        # Apply filters
        if filter_status and filter_status != "all":
            assignments_data = [a for a in assignments_data if a['status_value'].upper() == filter_status.upper()]
        
        # Apply search
        if search:
            search_lower = search.lower()
            assignments_data = [a for a in assignments_data if search_lower in a['exam_name'].lower()]
        
        # Apply sorting
        if sort_by == "name":
            assignments_data.sort(key=lambda x: x['exam_name'].lower(), reverse=(sort_order == "desc"))
        else:  # date
            assignments_data.sort(key=lambda x: x['assigned_at'], reverse=(sort_order == "desc"))
        
        return render_template(
            "student/dashboard.html",
            request=request,
            user=current_user,
            assignments=assignments_data,
            statistics=stats,
            average_score=average_score,
            upcoming_exams=upcoming,
            filter_status=filter_status or "all",
            search=search or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")


@router.get("/exams", response_class=HTMLResponse)
async def list_exams(
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """List assigned exams."""
    try:
        from app.repositories.assignment_repository import AssignmentRepository
        from app.repositories.exam_repository import ExamRepository
        
        assignment_repo = AssignmentRepository(db)
        exam_repo = ExamRepository(db)
        
        assignments = assignment_repo.list_by_student(current_user.id)
        
        from app.repositories.attempt_repository import AttemptRepository
        attempt_repo = AttemptRepository(db)
        
        assignments_data = []
        for assignment in assignments:
            try:
                exam = exam_repo.get_by_id(assignment.exam_id)
                
                # Find attempt for this assignment
                attempt = attempt_repo.get_active_by_assignment(assignment.id)
                if not attempt:
                    from app.models.attempt import Attempt
                    attempt = db.query(Attempt).filter(
                        Attempt.assignment_id == assignment.id
                    ).order_by(Attempt.started_at.desc()).first()
                
                # Determine status value based on assignment and attempt status
                status_value = assignment.status.value if hasattr(assignment.status, 'value') else str(assignment.status)
                
                # Map to display-friendly status
                if attempt:
                    if attempt.status == AttemptStatus.SUBMITTED:
                        from app.repositories.result_repository import ResultRepository
                        result_repo = ResultRepository(db)
                        result = result_repo.get_by_attempt_id(attempt.id)
                        if result and result.released_at:
                            status_value = "COMPLETED"  # Show as completed if result is released
                        else:
                            status_value = "SUBMITTED"
                    elif attempt.status == AttemptStatus.IN_PROGRESS:
                        status_value = "IN_PROGRESS"
                    else:
                        status_value = status_value.upper()
                elif status_value.upper() == "ASSIGNED":
                    status_value = "ASSIGNED"
                else:
                    status_value = status_value.upper()
                
                assignments_data.append({
                    'id': assignment.id,
                    'exam_id': assignment.exam_id,
                    'exam_name': exam.name if exam else f"Exam {assignment.exam_id}",
                    'status': assignment.status,
                    'status_value': status_value,
                    'assigned_at': assignment.assigned_at,
                    'attempt_id': attempt.id if attempt else None
                })
            except:
                continue
        
        return render_template(
            "student/exams/list.html",
            request=request, user=current_user, assignments=assignments_data
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading exams: {str(e)}")


@router.post("/exams/{assignment_id}/start")
async def start_exam(
    assignment_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Start an exam."""
    try:
        service = AttemptService(db)
        attempt = service.start_attempt(current_user, assignment_id)
        request.session["flash_message"] = {"type": "success", "message": "Exam started successfully!"}
        return RedirectResponse(url=f"/student/attempts/{attempt.id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/student/dashboard", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error starting exam: {str(e)}"}
        return RedirectResponse(url="/student/dashboard", status_code=302)


@router.get("/attempts/{attempt_id}", response_class=HTMLResponse)
async def view_attempt(
    request: Request,
    attempt_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """View attempt with questions."""
    try:
        from app.models.attempt import AttemptStatus
        from app.core.time import time_provider
        
        service = AttemptService(db)
        data = service.get_attempt_with_questions(current_user, attempt_id)
        
        # Format datetime for template
        # Convert naive UTC datetimes to ISO format for JavaScript Date parsing
        attempt = data["attempt"]
        from datetime import timezone as tz
        # started_at and ends_at are stored as naive UTC, add 'Z' suffix for ISO format
        started_at_str = attempt.started_at.strftime('%Y-%m-%dT%H:%M:%SZ') if hasattr(attempt.started_at, 'strftime') else str(attempt.started_at)
        ends_at_str = attempt.ends_at.strftime('%Y-%m-%dT%H:%M:%SZ') if hasattr(attempt.ends_at, 'strftime') else str(attempt.ends_at)
        status_value = attempt.status.value if hasattr(attempt.status, 'value') else str(attempt.status)
        
        # Check if attempt is submitted - if so, redirect to results
        if attempt.status == AttemptStatus.SUBMITTED:
            request.session["flash_message"] = {"type": "info", "message": "This attempt has already been submitted. Redirecting to results..."}
            return RedirectResponse(url=f"/student/results/{attempt_id}", status_code=302)
        
        # Check if time has expired
        # attempt.ends_at is stored as naive UTC, convert both to timezone-aware UTC for comparison
        now = time_provider.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)
        
        if attempt.status == AttemptStatus.IN_PROGRESS and attempt.ends_at:
            # attempt.ends_at is stored as naive UTC, convert to timezone-aware UTC
            ends_at_normalized = attempt.ends_at.replace(tzinfo=timezone.utc)
            
            if now > ends_at_normalized:
                # Time expired, attempt should have been auto-submitted
                # Redirect to results if available, otherwise show error
                from app.services.grading_service import GradingService
                grading_service = GradingService(db)
                try:
                    result = grading_service.get_result(current_user, attempt_id)
                    if result:
                        request.session["flash_message"] = {"type": "warning", "message": "Time expired. Your exam was automatically submitted."}
                        return RedirectResponse(url=f"/student/results/{attempt_id}", status_code=302)
                except:
                    pass
                request.session["flash_message"] = {"type": "error", "message": "Time has expired for this attempt. Please contact your teacher."}
                return RedirectResponse(url="/student/dashboard", status_code=302)
        
        attempt_data = {
            'id': attempt.id,
            'started_at': started_at_str,
            'ends_at': ends_at_str,
            'status': attempt.status,
            'status_value': status_value
        }
        
        return render_template(
            "student/attempt.html",
            request=request, user=current_user, attempt=attempt_data, questions=data["questions"]
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading attempt: {str(e)}")


@router.post("/attempts/{attempt_id}/answer")
async def save_answer(
    attempt_id: int,
    request: Request,
    snapshot_id: int = Form(...),
    selected_option: str = Form(...),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Save an answer."""
    try:
        service = AttemptService(db)
        try:
            selected = json.loads(selected_option)
        except (json.JSONDecodeError, ValueError):
            selected = selected_option
        service.save_answer(current_user, attempt_id, snapshot_id, selected)
        # Don't redirect, just return success (for AJAX calls)
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"status": "success"})
    except HTTPException as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"status": "error", "message": str(e.detail)}, status_code=e.status_code)
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"status": "error", "message": f"Error saving answer: {str(e)}"}, status_code=500)


@router.post("/attempts/{attempt_id}/submit")
async def submit_attempt(
    attempt_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Submit attempt."""
    try:
        attempt_service = AttemptService(db)
        
        # Save all answers from form before submitting
        try:
            form_data = await request.form()
            for key, value in form_data.items():
                if key.startswith('answer_'):
                    try:
                        # Parse snapshot_id from key format: "answer_{snapshot_id}"
                        parts = key.split('_')
                        if len(parts) >= 2:
                            snapshot_id = int(parts[1])
                            selected_option = value
                            if selected_option:  # Only save if value is not empty
                                attempt_service.save_answer(current_user, attempt_id, snapshot_id, selected_option)
                    except (ValueError, IndexError, TypeError) as e:
                        import logging
                        logging.getLogger(__name__).warning(f"Error parsing answer form field {key}: {str(e)}")
                        continue
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error parsing form data: {str(e)}")
            # Continue even if form parsing fails - answers may have been saved via AJAX
        
        # Submit the attempt
        attempt = attempt_service.submit_attempt(current_user, attempt_id)
        
        # Auto-grade if policy is IMMEDIATE
        grading_service = GradingService(db)
        try:
            grading_service.grade_attempt(attempt_id)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error auto-grading attempt {attempt_id}: {str(e)}")
            # Grade later if needed - don't fail the submission
        
        return RedirectResponse(url=f"/student/results/{attempt_id}", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error submitting attempt: {str(e)}")


@router.get("/results/{attempt_id}", response_class=HTMLResponse)
async def view_result(
    request: Request,
    attempt_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """View result with question breakdown."""
    try:
        service = GradingService(db)
        result = service.get_result(current_user, attempt_id)
        
        # Get attempt with questions for breakdown
        from app.services.attempt_service import AttemptService
        attempt_service = AttemptService(db)
        attempt_data = attempt_service.get_attempt_with_questions(current_user, attempt_id)
        
        result_data = None
        questions_breakdown = []
        exam_data = None
        is_passed = False
        
        if result:
            # Get exam info for pass score
            from app.repositories.exam_repository import ExamRepository
            exam_repo = ExamRepository(db)
            attempt = attempt_data["attempt"]
            exam = exam_repo.get_by_id(attempt.exam_id)
            
            if exam:
                # Check if passed
                if exam.pass_score is not None:
                    is_passed = result.percentage >= exam.pass_score
                else:
                    # Default: 50% if no pass_score set
                    is_passed = result.percentage >= 50
                
                exam_data = {
                    'id': exam.id,
                    'name': exam.name,
                    'pass_score': exam.pass_score
                }
            
            released_at_str = result.released_at.strftime('%Y-%m-%d %H:%M:%S') if result.released_at and hasattr(result.released_at, 'strftime') else (str(result.released_at) if result.released_at else None)
            result_data = {
                'id': result.id,
                'attempt_id': result.attempt_id,
                'earned_points': result.earned_points,
                'total_points': result.total_points,
                'percentage': result.percentage,
                'released_at': released_at_str,
                'is_passed': is_passed
            }
            
            # Build question breakdown
            if attempt_data and "questions" in attempt_data:
                for q in attempt_data["questions"]:
                    # Determine if answer is correct
                    is_correct = False
                    correct_answer_id = q.get("correct_answer")
                    correct_answer_text = q.get("correct_answer_text")
                    
                    if q.get("answer") and correct_answer_id is not None:
                        # Compare selected answer with correct answer
                        if str(q.get("answer")) == str(correct_answer_id):
                            is_correct = True
                    
                    questions_breakdown.append({
                        'title': q.get("question_title", ""),
                        'body': q.get("question_body", ""),
                        'points': q.get("points", 0),
                        'selected_answer': q.get("answer"),
                        'correct_answer': correct_answer_id,
                        'correct_answer_text': correct_answer_text,
                        'is_correct': is_correct,
                        'options': q.get("options", [])
                    })
        
        return render_template(
            "student/result.html",
            request=request, 
            user=current_user, 
            result=result_data,
            exam_data=exam_data,
            questions=questions_breakdown
        )
    except HTTPException:
        raise
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading result: {str(e)}")


@router.get("/profile", response_class=HTMLResponse)
async def view_profile(
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """View and edit profile."""
    try:
        from app.services.user_service import UserService
        service = UserService(db)
        user_data = service.get_user(current_user, current_user.id)
        
        return render_template(
            "student/profile.html",
            request=request,
            user=current_user,
            user_data=user_data
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading profile: {str(e)}"}
        return RedirectResponse(url="/student/dashboard", status_code=302)


@router.post("/profile")
async def update_profile(
    request: Request,
    email: str = Form(None),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Update profile email."""
    try:
        from app.services.user_service import UserService
        from app.schemas.user import UserUpdate
        
        service = UserService(db)
        user_data = UserUpdate(email=email if email else None)
        service.update_user(current_user, current_user.id, user_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Profile updated successfully!"}
        return RedirectResponse(url="/student/profile", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error updating profile: {str(e)}"}
        return RedirectResponse(url="/student/profile", status_code=302)


@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Change password page."""
    return render_template(
        "student/change_password.html",
        request=request,
        user=current_user
    )


@router.post("/change-password")
async def change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """Change password."""
    try:
        # Validate passwords match
        if new_password != confirm_password:
            request.session["flash_message"] = {"type": "error", "message": "New passwords do not match"}
            return RedirectResponse(url="/student/change-password", status_code=302)
        
        # Validate password length
        if len(new_password) < 6:
            request.session["flash_message"] = {"type": "error", "message": "Password must be at least 6 characters long"}
            return RedirectResponse(url="/student/change-password", status_code=302)
        
        from app.services.user_service import UserService
        service = UserService(db)
        service.change_password(current_user, old_password, new_password)
        
        request.session["flash_message"] = {"type": "success", "message": "Password changed successfully!"}
        return RedirectResponse(url="/student/profile", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": e.detail}
        return RedirectResponse(url="/student/change-password", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error changing password: {str(e)}"}
        return RedirectResponse(url="/student/change-password", status_code=302)


@router.get("/results", response_class=HTMLResponse)
async def list_results(
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """List all results for the student."""
    try:
        from app.repositories.exam_repository import ExamRepository
        
        grading_service = GradingService(db)
        results_data = grading_service.get_student_results(current_user, current_user.id)
        
        exam_repo = ExamRepository(db)
        results_list = []
        
        for result_item in results_data:
            exam = exam_repo.get_by_id(result_item["exam_id"])
            result = result_item["result"]
            
            released_at_str = None
            if result.released_at:
                released_at_str = result.released_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(result.released_at, 'strftime') else str(result.released_at)
            
            # Check if passed
            is_passed = False
            if exam and exam.pass_score is not None:
                is_passed = result.percentage >= exam.pass_score
            else:
                # Default: 50% if no pass_score set
                is_passed = result.percentage >= 50
            
            results_list.append({
                'attempt_id': result_item["attempt_id"],
                'exam_id': result_item["exam_id"],
                'exam_name': exam.name if exam else f"Exam {result_item['exam_id']}",
                'earned_points': result.earned_points,
                'total_points': result.total_points,
                'percentage': result.percentage,
                'released_at': released_at_str,
                'is_passed': is_passed
            })
        
        # Sort by released_at descending (most recent first)
        results_list.sort(key=lambda x: x['released_at'] or '', reverse=True)
        
        return render_template(
            "student/results.html",
            request=request,
            user=current_user,
            results=results_list
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading results: {str(e)}"}
        return RedirectResponse(url="/student/dashboard", status_code=302)


@router.get("/statistics", response_class=HTMLResponse)
async def view_statistics(
    request: Request,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """View student statistics."""
    try:
        service = StudentService(db)
        stats = service.get_student_statistics(current_user)
        upcoming = service.get_upcoming_exams(current_user)
        
        return render_template(
            "student/statistics.html",
            request=request,
            user=current_user,
            statistics=stats,
            upcoming_exams=upcoming
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading statistics: {str(e)}"}
        return RedirectResponse(url="/student/dashboard", status_code=302)


@router.get("/exams/{exam_id}/details", response_class=HTMLResponse)
async def exam_details(
    request: Request,
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """View exam details before starting."""
    try:
        from app.repositories.exam_repository import ExamRepository
        from app.repositories.assignment_repository import AssignmentRepository
        
        exam_repo = ExamRepository(db)
        assignment_repo = AssignmentRepository(db)
        
        exam = exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Check if student has assignment for this exam
        assignments = assignment_repo.list_by_student(current_user.id)
        assignment = next((a for a in assignments if a.exam_id == exam_id), None)
        
        if not assignment:
            raise HTTPException(status_code=403, detail="You are not assigned to this exam")
        
        # Get exam questions count
        exam_questions = exam_repo.get_exam_questions(exam_id)
        question_count = len(exam_questions)
        
        # Get student's attempts for this exam to show attempts used/remaining
        from app.repositories.attempt_repository import AttemptRepository
        attempt_repo = AttemptRepository(db)
        student_attempts = attempt_repo.list_by_student(current_user.id)
        exam_attempts = [a for a in student_attempts if a.exam_id == exam_id]
        attempts_used = len(exam_attempts)
        attempts_remaining = max(0, exam.attempts_allowed - attempts_used)
        
        # Format dates
        start_at_str = exam.start_at.strftime('%Y-%m-%d %H:%M:%S') if exam.start_at and hasattr(exam.start_at, 'strftime') else (str(exam.start_at) if exam.start_at else 'Not set')
        end_at_str = exam.end_at.strftime('%Y-%m-%d %H:%M:%S') if exam.end_at and hasattr(exam.end_at, 'strftime') else (str(exam.end_at) if exam.end_at else 'Not set')
        
        # Get grading policy text
        grading_policy_text = exam.grading_policy.value if hasattr(exam.grading_policy, 'value') else str(exam.grading_policy)
        
        exam_data = {
            'id': exam.id,
            'name': exam.name,
            'description': exam.description or 'No description provided',
            'duration_minutes': exam.duration_minutes,
            'start_at': start_at_str,
            'end_at': end_at_str,
            'attempts_allowed': exam.attempts_allowed,
            'attempts_used': attempts_used,
            'attempts_remaining': attempts_remaining,
            'grading_policy': grading_policy_text,
            'pass_score': exam.pass_score,
            'question_count': question_count,
            'assignment_id': assignment.id,
            'status': exam.status.value if hasattr(exam.status, 'value') else str(exam.status)
        }
        
        return render_template(
            "student/exam_details.html",
            request=request,
            user=current_user,
            exam=exam_data
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading exam details: {str(e)}"}
        return RedirectResponse(url="/student/dashboard", status_code=302)


@router.get("/exams/{exam_id}/attempts", response_class=HTMLResponse)
async def exam_attempts_history(
    request: Request,
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db)
):
    """View all attempts for a specific exam."""
    try:
        from app.repositories.exam_repository import ExamRepository
        from app.repositories.assignment_repository import AssignmentRepository
        
        exam_repo = ExamRepository(db)
        assignment_repo = AssignmentRepository(db)
        
        exam = exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Check if student has assignment for this exam
        assignments = assignment_repo.list_by_student(current_user.id)
        assignment = next((a for a in assignments if a.exam_id == exam_id), None)
        
        if not assignment:
            raise HTTPException(status_code=403, detail="You are not assigned to this exam")
        
        student_service = StudentService(db)
        attempts_history = student_service.get_exam_attempts_history(current_user, exam_id)
        
        return render_template(
            "student/attempts_history.html",
            request=request,
            user=current_user,
            exam=exam,
            attempts=attempts_history
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading attempts history: {str(e)}"}
        return RedirectResponse(url="/student/dashboard", status_code=302)

