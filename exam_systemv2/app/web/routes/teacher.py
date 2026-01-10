from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import timezone
import traceback
from app.db.session import get_db
from app.services.question_service import QuestionService
from app.services.exam_service import ExamService
from app.services.assignment_service import AssignmentService
from app.services.grading_service import GradingService
from app.services.teacher_profile_service import TeacherProfileService
from app.services.subject_service import SubjectService
from app.core.deps import require_role
from app.models.user import User, UserRole
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.schemas.exam import ExamCreate, ExamUpdate, ExamQuestionCreate
from app.schemas.assignment import AssignmentCreate
from app.schemas.teacher_profile import TeacherProfileCreate, TeacherProfileUpdate
from app.models.exam import ExamStatus
from app.web.templates_helper import render_template

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def teacher_dashboard(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Teacher dashboard."""
    try:
        question_service = QuestionService(db)
        exam_service = ExamService(db)
        questions, _ = question_service.list_questions(current_user, skip=0, limit=10)
        exams, _ = exam_service.list_exams(current_user, skip=0, limit=10)
        
        # Convert to list if needed and handle empty cases
        if not questions:
            questions = []
        if not exams:
            exams = []
        
        # Get statistics
        from app.services.grading_service import GradingService
        from app.repositories.exam_repository import ExamRepository
        grading_service = GradingService(db)
        exam_repo = ExamRepository(db)
        
        # Calculate overall statistics (optimized - batch queries to avoid N+1)
        from app.models.attempt import Attempt, AttemptStatus
        from app.models.result import Result
        
        # Get all attempts for teacher's exams in one query
        exam_ids = [exam.id for exam in exams] if exams else []
        if exam_ids:
            all_attempts = db.query(Attempt).filter(Attempt.exam_id.in_(exam_ids)).all()
            submitted_attempts = [a for a in all_attempts if a.status == AttemptStatus.SUBMITTED]
            total_attempts = len(submitted_attempts)
            
            # Get all results in one query
            attempt_ids = [a.id for a in submitted_attempts]
            if attempt_ids:
                all_results = db.query(Result).filter(Result.attempt_id.in_(attempt_ids)).all()
                # Create a dict for quick lookup
                results_by_attempt = {r.attempt_id: r for r in all_results}
                all_exams_dict = {exam.id: exam for exam in exams}
                
                total_passed = 0
                total_failed = 0
                for attempt in submitted_attempts:
                    result = results_by_attempt.get(attempt.id)
                    if result:
                        exam_obj = all_exams_dict.get(attempt.exam_id)
                        if exam_obj:
                            pass_score = exam_obj.pass_score if exam_obj.pass_score is not None else 50
                            if result.percentage >= pass_score:
                                total_passed += 1
                            else:
                                total_failed += 1
            else:
                total_passed = 0
                total_failed = 0
        else:
            total_attempts = 0
            total_passed = 0
            total_failed = 0
        
        statistics = {
            'total_questions': len(questions),
            'total_exams': len(exams),
            'total_attempts': total_attempts,
            'total_passed': total_passed,
            'total_failed': total_failed
        }
            
        return render_template(
            "teacher/dashboard.html",
            request=request, 
            user=current_user, 
            questions=questions, 
            exams=exams,
            statistics=statistics
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")


@router.get("/questions", response_class=HTMLResponse)
async def list_questions(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    search: str = None,
    tags: str = None,
    difficulty: int = None,
    type: str = None,
    page: int = 1
):
    """List questions with filtering and pagination."""
    try:
        from typing import Optional
        
        service = QuestionService(db)
        
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        
        # Parse question type
        question_type = None
        if type:
            if type == "multiple_choice":
                from app.models.question import QuestionType
                question_type = QuestionType.MULTIPLE_CHOICE
            elif type == "true_false":
                from app.models.question import QuestionType
                question_type = QuestionType.TRUE_FALSE
        
        # Pagination
        per_page = 20
        skip = (page - 1) * per_page
        
        questions, total = service.list_questions(
            current_user, 
            skip=skip, 
            limit=per_page,
            search=search,
            tags=tag_list,
            difficulty=difficulty,
            type=question_type
        )
        
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        
        # Format questions with tags for template
        questions_data = []
        for question in questions or []:
            tags_list = [tag.tag for tag in question.tags] if hasattr(question, 'tags') and question.tags else []
            questions_data.append({
                'id': question.id,
                'title': question.title,
                'body': question.body,
                'type': question.type,
                'difficulty': question.difficulty,
                'tags': tags_list,
                'tags_display': ', '.join(tags_list) if tags_list else 'No tags'
            })
        
        return render_template(
            "teacher/questions/list.html",
            request=request, 
            user=current_user, 
            questions=questions_data,
            search=search or "",
            tags_filter=tags or "",
            difficulty_filter=difficulty,
            type_filter=type or "",
            page=page,
            total_pages=total_pages,
            total=total,
            per_page=per_page
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading questions: {str(e)}")


@router.get("/questions/{question_id}/edit", response_class=HTMLResponse)
async def edit_question_page(
    request: Request,
    question_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Edit question page."""
    try:
        service = QuestionService(db)
        question = service.get_question(current_user, question_id)
        
        # Format tags for template (comma-separated string)
        tags_list = [tag.tag for tag in question.tags] if hasattr(question, 'tags') and question.tags else []
        tags_display = ', '.join(tags_list) if tags_list else ''
        
        # Create question dict with formatted tags
        # Convert type enum to string value for template
        type_value = question.type.value if hasattr(question.type, 'value') else str(question.type)
        question_data = {
            'id': question.id,
            'title': question.title,
            'body': question.body,
            'difficulty': question.difficulty,
            'type': question.type,
            'type_value': type_value,  # Add type_value for template
            'question_type': type_value,  # Add question_type for template compatibility
            'explanation': question.explanation or '',
            'options': question.options if hasattr(question, 'options') and question.options else [],
            'tags': tags_list,
            'tags_display': tags_display
        }
        
        # Get form data from session if available (for error recovery)
        form_data = request.session.get("form_data", {})
        # Clear form data from session after reading
        if "form_data" in request.session:
            del request.session["form_data"]
        # Merge form_data with question_data if available (form_data takes precedence)
        if form_data:
            question_data.update(form_data)
        
        return render_template(
            "teacher/questions/edit.html",
            request=request, user=current_user, question=question_data
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error loading question: {str(e)}")


@router.post("/questions/{question_id}/edit")
async def update_question(
    request: Request,
    question_id: int,
    title: str = Form(...),
    body: str = Form(...),
    difficulty: int = Form(...),
    question_type: str = Form(...),
    explanation: str = Form(None),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update question."""
    try:
        from app.models.question import QuestionType
        from app.schemas.question import QuestionUpdate, QuestionOptionCreate
        
        # Parse question type
        if question_type == "multiple_choice":
            qtype = QuestionType.MULTIPLE_CHOICE
        elif question_type == "true_false":
            qtype = QuestionType.TRUE_FALSE
        else:
            qtype = QuestionType.MULTIPLE_CHOICE
        
        # Parse options from form
        form_data = await request.form()
        
        # Parse tags first (needed for error handling)
        tags_str = form_data.get("tags", "")
        
        options = []
        
        # For True/False, handle separately - always use true_false_correct
        if qtype == QuestionType.TRUE_FALSE:
            # For True/False, we need to get which one is correct from form
            true_false_correct = form_data.get("true_false_correct", "true")
            if true_false_correct == "true":
                options.append(QuestionOptionCreate(text="True", is_correct=True))
                options.append(QuestionOptionCreate(text="False", is_correct=False))
            else:
                options.append(QuestionOptionCreate(text="True", is_correct=False))
                options.append(QuestionOptionCreate(text="False", is_correct=True))
        else:
            # For Multiple Choice, parse options from form
            option_texts = form_data.getlist("option_text")
            
            # Check which options are marked as correct using indexed checkboxes
            for i, text in enumerate(option_texts):
                if text.strip():
                    # Check if this specific option index is marked as correct
                    is_correct = form_data.get(f"option_correct_{i}", "") == "on"
                    options.append(QuestionOptionCreate(text=text.strip(), is_correct=is_correct))
        
        # Validate: At least one option must be correct
        if not any(opt.is_correct for opt in options):
            # Save form data to session for preservation
            request.session["form_data"] = {
                "title": title,
                "body": body,
                "difficulty": difficulty,
                "question_type": question_type,
                "explanation": explanation or "",
                "tags": tags_str or "",
                "options": [{"text": opt.text, "is_correct": opt.is_correct} for opt in options]
            }
            request.session["flash_message"] = {"type": "error", "message": "At least one option must be marked as correct!"}
            return RedirectResponse(url=f"/teacher/questions/{question_id}/edit", status_code=302)
        
        # Validate: Multiple choice questions need at least 2 options
        if qtype == QuestionType.MULTIPLE_CHOICE and len(options) < 2:
            # Save form data to session for preservation
            request.session["form_data"] = {
                "title": title,
                "body": body,
                "difficulty": difficulty,
                "question_type": question_type,
                "explanation": explanation or "",
                "tags": tags_str or "",
                "options": [{"text": opt.text, "is_correct": opt.is_correct} for opt in options]
            }
            request.session["flash_message"] = {"type": "error", "message": "Multiple choice questions must have at least 2 options!"}
            return RedirectResponse(url=f"/teacher/questions/{question_id}/edit", status_code=302)
        
        # Parse tags into list
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        
        # Update question
        question_data = QuestionUpdate(
            title=title,
            body=body,
            difficulty=difficulty,
            explanation=explanation if explanation else None,
            options=options,
            tags=tags
        )
        
        service = QuestionService(db)
        service.update_question(current_user, question_id, question_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Question updated successfully!"}
        return RedirectResponse(url="/teacher/questions", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Save form data to session for preservation
        form_data = await request.form()
        request.session["form_data"] = {
            "title": title,
            "body": body,
            "difficulty": difficulty,
            "question_type": question_type,
            "explanation": explanation or "",
            "tags": form_data.get("tags", "") or "",
            "options": []
        }
        request.session["flash_message"] = {"type": "error", "message": f"Error updating question: {str(e)}"}
        return RedirectResponse(url=f"/teacher/questions/{question_id}/edit", status_code=302)


@router.post("/questions/{question_id}/delete")
async def delete_question(
    question_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a question."""
    try:
        service = QuestionService(db)
        service.delete_question(current_user, question_id)
        request.session["flash_message"] = {"type": "success", "message": "Question deleted successfully!"}
        return RedirectResponse(url="/teacher/questions", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error deleting question: {str(e)}")


@router.get("/questions/new", response_class=HTMLResponse)
async def new_question_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))
):
    """New question page."""
    # Get form data from session if available (for error recovery)
    form_data = request.session.get("form_data", {})
    # Clear form data from session after reading
    if "form_data" in request.session:
        del request.session["form_data"]
    return render_template(
        "teacher/questions/new.html",
        request=request, user=current_user, form_data=form_data
    )


@router.post("/questions/new")
async def create_question(
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    difficulty: int = Form(...),
    question_type: str = Form(...),
    explanation: str = Form(None),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create question with options and tags."""
    try:
        from app.models.question import QuestionType
        from app.schemas.question import QuestionCreate, QuestionOptionCreate
        
        # Parse question type
        if question_type == "multiple_choice":
            qtype = QuestionType.MULTIPLE_CHOICE
        elif question_type == "true_false":
            qtype = QuestionType.TRUE_FALSE
        else:
            qtype = QuestionType.MULTIPLE_CHOICE
        
        # Parse options from form
        form_data = await request.form()
        
        # Parse tags first (needed for error handling)
        tags_str = form_data.get("tags", "")
        
        options = []
        
        # For True/False, handle separately
        if qtype == QuestionType.TRUE_FALSE:
            # For True/False, we need to get which one is correct from form
            true_false_correct = form_data.get("true_false_correct", "true")
            if true_false_correct == "true":
                options.append(QuestionOptionCreate(text="True", is_correct=True))
                options.append(QuestionOptionCreate(text="False", is_correct=False))
            else:
                options.append(QuestionOptionCreate(text="True", is_correct=False))
                options.append(QuestionOptionCreate(text="False", is_correct=True))
        else:
            # For Multiple Choice, parse options from form
            option_texts = form_data.getlist("option_text")
            
            # Check which options are marked as correct using indexed checkboxes
            for i, text in enumerate(option_texts):
                if text.strip():
                    # Check if this specific option index is marked as correct
                    is_correct = form_data.get(f"option_correct_{i}", "") == "on"
                    options.append(QuestionOptionCreate(text=text.strip(), is_correct=is_correct))
        
        # Validate: At least one option must be correct
        if not any(opt.is_correct for opt in options):
            # Save form data to session for preservation
            request.session["form_data"] = {
                "title": title,
                "body": body,
                "difficulty": difficulty,
                "question_type": question_type,
                "explanation": explanation or "",
                "tags": tags_str or "",
                "options": [{"text": opt.text, "is_correct": opt.is_correct} for opt in options]
            }
            request.session["flash_message"] = {"type": "error", "message": "At least one option must be marked as correct!"}
            return RedirectResponse(url="/teacher/questions/new", status_code=302)
        
        # Validate: Multiple choice questions need at least 2 options
        if qtype == QuestionType.MULTIPLE_CHOICE and len(options) < 2:
            # Save form data to session for preservation
            request.session["form_data"] = {
                "title": title,
                "body": body,
                "difficulty": difficulty,
                "question_type": question_type,
                "explanation": explanation or "",
                "tags": tags_str or "",
                "options": [{"text": opt.text, "is_correct": opt.is_correct} for opt in options]
            }
            request.session["flash_message"] = {"type": "error", "message": "Multiple choice questions must have at least 2 options!"}
            return RedirectResponse(url="/teacher/questions/new", status_code=302)
        
        # Validate difficulty before creating QuestionCreate
        if not (1 <= difficulty <= 5):
            request.session["form_data"] = {
                "title": title,
                "body": body,
                "difficulty": difficulty,
                "question_type": question_type,
                "explanation": explanation or "",
                "tags": tags_str or "",
                "options": [{"text": opt.text, "is_correct": opt.is_correct} for opt in options]
            }
            request.session["flash_message"] = {"type": "error", "message": "Difficulty level must be between 1 and 5!"}
            return RedirectResponse(url="/teacher/questions/new", status_code=302)
        
        # Parse tags into list
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        
        # Create question
        question_data = QuestionCreate(
            title=title,
            body=body,
            difficulty=difficulty,
            type=qtype,
            explanation=explanation if explanation else None,
            options=options,
            tags=tags
        )
        
        service = QuestionService(db)
        service.create_question(current_user, question_data)
        
        # Set success message
        request.session["flash_message"] = {"type": "success", "message": "Question created successfully!"}
        return RedirectResponse(url="/teacher/questions", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Save form data to session for preservation
        form_data = await request.form()
        request.session["form_data"] = {
            "title": title,
            "body": body,
            "difficulty": difficulty,
            "question_type": question_type,
            "explanation": explanation or "",
            "tags": form_data.get("tags", "") or "",
            "options": []
        }
        request.session["flash_message"] = {"type": "error", "message": f"Error creating question: {str(e)}"}
        return RedirectResponse(url="/teacher/questions/new", status_code=302)


@router.get("/exams", response_class=HTMLResponse)
async def list_exams(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
    search: str = None,
    status: str = None
):
    """List exams with filtering."""
    try:
        service = ExamService(db)
        exams, _ = service.list_exams(current_user, skip=0, limit=1000)
        
        # Apply client-side filtering (since service doesn't support it yet)
        filtered_exams = exams or []
        
        if search:
            search_lower = search.lower()
            filtered_exams = [
                exam for exam in filtered_exams 
                if search_lower in exam.name.lower() or 
                   (exam.description and search_lower in exam.description.lower())
            ]
        
        if status:
            from app.models.exam import ExamStatus
            status_enum = None
            if status.upper() == "DRAFT":
                status_enum = ExamStatus.DRAFT
            elif status.upper() == "PUBLISHED":
                status_enum = ExamStatus.PUBLISHED
            elif status.upper() == "ARCHIVED":
                status_enum = ExamStatus.ARCHIVED
            
            if status_enum:
                filtered_exams = [exam for exam in filtered_exams if exam.status == status_enum]
        
        return render_template(
            "teacher/exams/list.html",
            request=request, 
            user=current_user, 
            exams=filtered_exams,
            search=search or "",
            status_filter=status or ""
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading exams: {str(e)}")


@router.get("/exams/new", response_class=HTMLResponse)
async def new_exam_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))
):
    """New exam page."""
    return render_template(
        "teacher/exams/new.html",
        request=request, user=current_user
    )


@router.get("/exams/{exam_id}/edit", response_class=HTMLResponse)
async def edit_exam_page(
    request: Request,
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Edit exam page."""
    try:
        service = ExamService(db)
        exam = service.get_exam(current_user, exam_id)
        return render_template(
            "teacher/exams/edit.html",
            request=request, user=current_user, exam=exam
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error loading exam: {str(e)}")


@router.post("/exams/{exam_id}/edit")
async def update_exam_web(
    request: Request,
    exam_id: int,
    name: str = Form(...),
    description: str = Form(None),
    duration_minutes: int = Form(...),
    grading_policy: str = Form(...),
    attempts_allowed: int = Form(1),
    start_at: str = Form(None),
    end_at: str = Form(None),
    pass_score: int = Form(None),
    shuffle_questions: str = Form(None),
    shuffle_options: str = Form(None),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update an exam."""
    try:
        from app.models.exam import GradingPolicy
        from app.schemas.exam import ExamUpdate
        from datetime import datetime
        
        # Parse grading policy
        if grading_policy == "immediate":
            policy = GradingPolicy.IMMEDIATE
        elif grading_policy == "after_end":
            policy = GradingPolicy.AFTER_END
        elif grading_policy == "manual":
            policy = GradingPolicy.MANUAL
        else:
            policy = GradingPolicy.IMMEDIATE
        
        # Parse datetime strings and normalize to UTC naive datetime
        from app.core.utils import parse_form_datetime
        start_at_dt = parse_form_datetime(start_at)
        end_at_dt = parse_form_datetime(end_at)
        
        exam_data = ExamUpdate(
            name=name,
            description=description if description else None,
            duration_minutes=duration_minutes,
            grading_policy=policy,
            attempts_allowed=attempts_allowed,
            start_at=start_at_dt,
            end_at=end_at_dt,
            pass_score=pass_score if pass_score is not None else None,
            shuffle_questions=shuffle_questions == "on",
            shuffle_options=shuffle_options == "on"
        )
        
        service = ExamService(db)
        service.update_exam(current_user, exam_id, exam_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Exam updated successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error updating exam: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}/edit", status_code=302)


@router.post("/exams/new")
async def create_exam(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    duration_minutes: int = Form(...),
    grading_policy: str = Form(...),
    attempts_allowed: int = Form(1),
    start_at: str = Form(None),
    end_at: str = Form(None),
    pass_score: int = Form(None),
    shuffle_questions: str = Form(None),
    shuffle_options: str = Form(None),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new exam."""
    try:
        from app.models.exam import GradingPolicy
        from app.schemas.exam import ExamCreate
        from datetime import datetime
        
        # Parse grading policy
        if grading_policy == "immediate":
            policy = GradingPolicy.IMMEDIATE
        elif grading_policy == "after_end":
            policy = GradingPolicy.AFTER_END
        elif grading_policy == "manual":
            policy = GradingPolicy.MANUAL
        else:
            policy = GradingPolicy.IMMEDIATE
        
        # Parse datetime strings and normalize to UTC naive datetime
        from app.core.utils import parse_form_datetime
        start_at_dt = parse_form_datetime(start_at)
        end_at_dt = parse_form_datetime(end_at)
        
        exam_data = ExamCreate(
            name=name,
            description=description if description else None,
            duration_minutes=duration_minutes,
            grading_policy=policy,
            attempts_allowed=attempts_allowed,
            start_at=start_at_dt,
            end_at=end_at_dt,
            pass_score=pass_score if pass_score is not None else None,
            shuffle_questions=shuffle_questions == "on",
            shuffle_options=shuffle_options == "on"
        )
        
        service = ExamService(db)
        exam = service.create_exam(current_user, exam_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Exam created successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam.id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error creating exam: {str(e)}"}
        return RedirectResponse(url="/teacher/exams/new", status_code=302)


@router.get("/exams/{exam_id}", response_class=HTMLResponse)
async def view_exam(
    request: Request,
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """View exam details."""
    try:
        service = ExamService(db)
        exam = service.get_exam(current_user, exam_id)
        assignment_service = AssignmentService(db)
        assignments, _ = assignment_service.list_assignments(current_user, exam_id=exam_id, skip=0, limit=1000)
        
        # Format exam data
        exam_status = exam.status.value if hasattr(exam.status, 'value') else str(exam.status)
        grading_policy = exam.grading_policy.value if hasattr(exam.grading_policy, 'value') else str(exam.grading_policy)
        
        # Get exam questions
        exam_questions = []
        if hasattr(exam, 'exam_questions') and exam.exam_questions:
            for eq in exam.exam_questions:
                question = service.question_repo.get_by_id(eq.question_id)
                if question:
                    exam_questions.append({
                        'id': eq.id,
                        'question_id': eq.question_id,
                        'question_title': question.title,
                        'question_body': question.body,
                        'points': eq.points,
                        'sort_order': eq.sort_order
                    })
        
        # Get all students for assignment form
        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository(db)
        all_students = user_repo.list_by_role(UserRole.STUDENT)
        
        exam_data = {
            'id': exam.id,
            'name': exam.name,
            'description': exam.description,
            'duration_minutes': exam.duration_minutes,
            'status': exam.status,
            'status_value': exam_status,
            'grading_policy': exam.grading_policy,
            'grading_policy_value': grading_policy,
            'pass_score': exam.pass_score,
            'start_at': exam.start_at,
            'end_at': exam.end_at,
            'attempts_allowed': exam.attempts_allowed,
            'shuffle_questions': exam.shuffle_questions,
            'shuffle_options': exam.shuffle_options
        }
        
        # Get exam results
        from app.services.grading_service import GradingService
        grading_service = GradingService(db)
        exam_results = []
        try:
            results_data = grading_service.get_exam_results(current_user, exam_id)
            for result_item in results_data:
                student = user_repo.get_by_id(result_item["student_id"])
                result = result_item["result"]
                
                # Check if passed
                is_passed = False
                if exam.pass_score is not None:
                    is_passed = result.percentage >= exam.pass_score
                else:
                    is_passed = result.percentage >= 50
                
                exam_results.append({
                    'student_id': result_item["student_id"],
                    'student_username': student.username if student else f"Student {result_item['student_id']}",
                    'attempt_id': result_item["attempt_id"],
                    'earned_points': result.earned_points,
                    'total_points': result.total_points,
                    'percentage': result.percentage,
                    'is_passed': is_passed,
                    'released_at': result.released_at.strftime('%Y-%m-%d %H:%M:%S') if result.released_at and hasattr(result.released_at, 'strftime') else (str(result.released_at) if result.released_at else None)
                })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error loading exam results: {str(e)}")
            # Continue without results if error occurs
        
        return render_template(
            "teacher/exams/view.html",
            request=request, 
            user=current_user, 
            exam=exam_data, 
            assignments=assignments or [],
            exam_questions=exam_questions,
            all_students=all_students or [],
            exam_results=exam_results
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading exam: {str(e)}")


@router.post("/exams/{exam_id}/publish")
async def publish_exam(
    exam_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Publish an exam."""
    try:
        service = ExamService(db)
        service.publish_exam(current_user, exam_id)
        request.session["flash_message"] = {"type": "success", "message": "Exam published successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error publishing exam: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.post("/exams/{exam_id}/assign")
async def assign_students(
    exam_id: int,
    request: Request,
    student_ids: List[int] = Form(...),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Assign students to exam."""
    try:
        # Validate that at least one student is selected
        if not student_ids or len(student_ids) == 0:
            request.session["flash_message"] = {"type": "error", "message": "Please select at least one student to assign."}
            return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
        
        service = AssignmentService(db)
        result = service.bulk_assign_students(current_user, exam_id, student_ids)
        
        # Count how many students were actually assigned (excluding duplicates)
        assigned_count = len(result) if result else 0
        if assigned_count == 0:
            request.session["flash_message"] = {"type": "warning", "message": "No new students were assigned. They may already be assigned to this exam."}
        else:
            request.session["flash_message"] = {"type": "success", "message": f"Successfully assigned {assigned_count} student(s) to the exam!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        from fastapi import HTTPException
        request.session["flash_message"] = {"type": "error", "message": f"Error assigning students: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.post("/exams/{exam_id}/unpublish")
async def unpublish_exam(
    exam_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Unpublish an exam."""
    try:
        service = ExamService(db)
        service.unpublish_exam(current_user, exam_id)
        request.session["flash_message"] = {"type": "success", "message": "Exam unpublished successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error unpublishing exam: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.post("/exams/{exam_id}/archive")
async def archive_exam(
    exam_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Archive an exam."""
    try:
        service = ExamService(db)
        service.archive_exam(current_user, exam_id)
        request.session["flash_message"] = {"type": "success", "message": "Exam archived successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error archiving exam: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.post("/exams/{exam_id}/delete")
async def delete_exam_web(
    exam_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete an exam."""
    try:
        service = ExamService(db)
        service.delete_exam(current_user, exam_id)
        request.session["flash_message"] = {"type": "success", "message": "Exam deleted successfully!"}
        return RedirectResponse(url="/teacher/exams", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error deleting exam: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.post("/exams/{exam_id}/questions/{question_id}/remove")
async def remove_question_from_exam_web(
    exam_id: int,
    question_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Remove a question from an exam."""
    try:
        service = ExamService(db)
        service.remove_question_from_exam(current_user, exam_id, question_id)
        request.session["flash_message"] = {"type": "success", "message": "Question removed from exam!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error removing question: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.get("/exams/{exam_id}/add-question", response_class=HTMLResponse)
async def add_question_to_exam_page(
    request: Request,
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Page to add questions to exam."""
    try:
        service = ExamService(db)
        exam = service.get_exam(current_user, exam_id)
        
        question_service = QuestionService(db)
        questions, _ = question_service.list_questions(current_user, skip=0, limit=1000)
        
        # Filter out questions already in exam
        exam_question_ids = {eq.question_id for eq in exam.exam_questions} if hasattr(exam, 'exam_questions') else set()
        available_questions = [q for q in questions if q.id not in exam_question_ids]
        
        return render_template(
            "teacher/exams/add_question.html",
            request=request,
            user=current_user,
            exam=exam,
            questions=available_questions
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error loading page: {str(e)}")


@router.post("/exams/{exam_id}/add-question")
async def add_question_to_exam_web(
    exam_id: int,
    request: Request,
    question_id: int = Form(...),
    points: int = Form(...),
    sort_order: int = Form(...),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Add a question to an exam."""
    try:
        service = ExamService(db)
        exam_question = ExamQuestionCreate(
            question_id=question_id,
            points=points,
            sort_order=sort_order
        )
        service.add_question_to_exam(current_user, exam_id, exam_question)
        request.session["flash_message"] = {"type": "success", "message": "Question added to exam!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}/add-question", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error adding question: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}/add-question", status_code=302)


@router.get("/exams/{exam_id}/statistics", response_class=HTMLResponse)
async def exam_statistics(
    request: Request,
    exam_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """View exam statistics."""
    try:
        from app.services.grading_service import GradingService
        from app.services.exam_service import ExamService
        from app.repositories.exam_repository import ExamRepository
        from app.repositories.user_repository import UserRepository
        
        exam_service = ExamService(db)
        grading_service = GradingService(db)
        exam_repo = ExamRepository(db)
        user_repo = UserRepository(db)
        
        exam = exam_repo.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get statistics
        stats = grading_service.get_exam_statistics(current_user, exam_id)
        exam_stats = exam_service.get_exam_statistics(current_user, exam_id)
        
        # Get all results with student info
        results_data = grading_service.get_exam_results(current_user, exam_id)
        results_list = []
        passed_count = 0
        failed_count = 0
        
        for result_item in results_data:
            student = user_repo.get_by_id(result_item["student_id"])
            result = result_item["result"]
            
            # Check if passed
            is_passed = False
            if exam.pass_score is not None:
                is_passed = result.percentage >= exam.pass_score
            else:
                is_passed = result.percentage >= 50
            
            if is_passed:
                passed_count += 1
            else:
                failed_count += 1
            
            results_list.append({
                'student_id': result_item["student_id"],
                'student_username': student.username if student else f"Student {result_item['student_id']}",
                'attempt_id': result_item["attempt_id"],
                'earned_points': result.earned_points,
                'total_points': result.total_points,
                'percentage': result.percentage,
                'is_passed': is_passed
            })
        
        # Sort by percentage descending
        results_list.sort(key=lambda x: x['percentage'], reverse=True)
        
        exam_data = {
            'id': exam.id,
            'name': exam.name,
            'pass_score': exam.pass_score
        }
        
        return render_template(
            "teacher/exams/statistics.html",
            request=request,
            user=current_user,
            exam=exam_data,
            statistics=stats,
            exam_statistics=exam_stats,
            results=results_list,
            passed_count=passed_count,
            failed_count=failed_count
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading statistics: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.post("/exams/{exam_id}/release-results")
async def release_results(
    exam_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Release results."""
    try:
        service = GradingService(db)
        service.release_results(current_user, exam_id)
        request.session["flash_message"] = {"type": "success", "message": "Results released successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error releasing results: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


@router.get("/results/{attempt_id}", response_class=HTMLResponse)
async def view_student_result(
    request: Request,
    attempt_id: int,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """View student result with question breakdown. Teachers can view any student's result."""
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
        student_info = None
        
        if result:
            # Get student info
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(db)
            attempt = attempt_data["attempt"]
            student = user_repo.get_by_id(attempt.student_id)
            if student:
                student_info = {
                    'id': student.id,
                    'username': student.username,
                    'email': student.email
                }
            
            # Get exam info for pass score
            from app.repositories.exam_repository import ExamRepository
            exam_repo = ExamRepository(db)
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
            "teacher/result.html",
            request=request, 
            user=current_user, 
            result=result_data,
            exam_data=exam_data,
            student_info=student_info,
            questions=questions_breakdown
        )
    except HTTPException:
        raise
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error loading result: {str(e)}")


@router.post("/exams/{exam_id}/assignments/{assignment_id}/delete")
async def delete_assignment_web(
    exam_id: int,
    assignment_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete an assignment."""
    try:
        service = AssignmentService(db)
        service.delete_assignment(current_user, assignment_id)
        request.session["flash_message"] = {"type": "success", "message": "Assignment removed successfully!"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error removing assignment: {str(e)}"}
        return RedirectResponse(url=f"/teacher/exams/{exam_id}", status_code=302)


# Teacher Profile Routes
@router.get("/profile", response_class=HTMLResponse)
async def view_profile(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """View teacher profile."""
    try:
        profile_service = TeacherProfileService(db)
        profile = profile_service.get_profile(current_user)
        return render_template(
            "teacher/profile.html",
            request=request, user=current_user, profile=profile
        )
    except HTTPException as e:
        if e.status_code == 404:
            # Profile doesn't exist yet, redirect to create
            return RedirectResponse(url="/teacher/profile/edit", status_code=302)
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        return RedirectResponse(url="/teacher/dashboard", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading profile: {str(e)}"}
        return RedirectResponse(url="/teacher/dashboard", status_code=302)


@router.get("/profile/edit", response_class=HTMLResponse)
async def edit_profile_page(
    request: Request,
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Edit profile page."""
    try:
        profile_service = TeacherProfileService(db)
        subject_service = SubjectService(db)
        
        # Get all active subjects for selection
        subjects = subject_service.list_subjects(active_only=True)
        
        # Try to get existing profile
        default_first_name = None
        default_last_name = None
        try:
            profile = profile_service.get_profile(current_user)
            existing_subject_ids = [s.id for s in profile.subjects]
        except HTTPException as e:
            if e.status_code == 404:
                profile = None
                existing_subject_ids = []
                # Auto-extract first_name and last_name from username
                # Username format: "firstname.lastname" or "firstname_lastname" or just "firstname"
                username_parts = current_user.username.replace('_', '.').split('.')
                if len(username_parts) >= 2:
                    default_first_name = username_parts[0].capitalize()
                    default_last_name = username_parts[-1].capitalize()
                elif len(username_parts) >= 1:
                    default_first_name = username_parts[0].capitalize()
                    default_last_name = ""
            else:
                raise
        
        return render_template(
            "teacher/profile_edit.html",
            request=request, 
            user=current_user, 
            profile=profile,
            subjects=subjects,
            existing_subject_ids=existing_subject_ids,
            default_first_name=default_first_name,
            default_last_name=default_last_name
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error loading profile edit page: {str(e)}"}
        return RedirectResponse(url="/teacher/dashboard", status_code=302)


@router.post("/profile/edit")
async def update_profile(
    request: Request,
    first_name: str = Form(None),
    last_name: str = Form(None),
    bio: str = Form(None),
    phone: str = Form(None),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update teacher profile."""
    try:
        profile_service = TeacherProfileService(db)
        
        # Get selected subject IDs from form
        form_data = await request.form()
        subject_ids = [int(id) for id in form_data.getlist("subject_ids") if id]
        
        # Auto-extract first_name and last_name from username if not provided
        if not first_name or not last_name:
            username_parts = current_user.username.replace('_', '.').split('.')
            if not first_name and len(username_parts) >= 1:
                first_name = username_parts[0].capitalize()
            if not last_name and len(username_parts) >= 2:
                last_name = username_parts[-1].capitalize()
            elif not last_name:
                last_name = ""  # Allow empty last name if can't extract
        
        # Check if profile exists
        try:
            existing_profile = profile_service.get_profile(current_user)
            # Update existing profile
            profile_data = TeacherProfileUpdate(
                first_name=first_name.strip() if first_name else None,
                last_name=last_name.strip() if last_name else None,
                bio=bio.strip() if bio else None,
                phone=phone.strip() if phone else None,
                subject_ids=subject_ids
            )
            profile = profile_service.update_profile(current_user, profile_data)
        except HTTPException:
            # Create new profile
            profile_data = TeacherProfileCreate(
                first_name=first_name.strip() if first_name else None,
                last_name=last_name.strip() if last_name else None,
                bio=bio.strip() if bio else None,
                phone=phone.strip() if phone else None,
                subject_ids=subject_ids
            )
            profile = profile_service.create_or_update_profile(current_user, profile_data)
        
        request.session["flash_message"] = {"type": "success", "message": "Profile updated successfully!"}
        # Clear form data from session
        if "form_data" in request.session:
            del request.session["form_data"]
        return RedirectResponse(url="/teacher/profile", status_code=302)
    except HTTPException as e:
        request.session["flash_message"] = {"type": "error", "message": str(e.detail)}
        request.session["form_data"] = {
            "first_name": first_name,
            "last_name": last_name,
            "bio": bio,
            "phone": phone
        }
        return RedirectResponse(url="/teacher/profile/edit", status_code=302)
    except Exception as e:
        import traceback
        traceback.print_exc()
        request.session["flash_message"] = {"type": "error", "message": f"Error updating profile: {str(e)}"}
        request.session["form_data"] = {
            "first_name": first_name,
            "last_name": last_name,
            "bio": bio,
            "phone": phone
        }
        return RedirectResponse(url="/teacher/profile/edit", status_code=302)

