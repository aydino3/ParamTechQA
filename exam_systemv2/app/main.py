from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    AppException
)
from app.core.rate_limit import RateLimitMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.routes import auth as api_auth, questions, exams, attempts, results, admin as api_admin, assignments
from app.web.routes import auth as web_auth, teacher, student, admin
import os

setup_logging()

app = FastAPI(title="Online Exam System", version="1.0.0")

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Middleware (order matters - rate limit should be first)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=300,  # Increased for development
    requests_per_hour=10000   # Increased for development
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Mount static files if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# API routes
app.include_router(api_auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(exams.router, prefix="/api/exams", tags=["exams"])
app.include_router(attempts.router, prefix="/api/attempts", tags=["attempts"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(api_admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["assignments"])

# Web routes
app.include_router(web_auth.router, tags=["web"])
app.include_router(teacher.router, prefix="/teacher", tags=["teacher"])
app.include_router(student.router, prefix="/student", tags=["student"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint - redirect to login."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/login")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

