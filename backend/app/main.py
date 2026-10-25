from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from app.config.database import Base, engine, ensure_email_otp_columns

from app.models import (
    User,
    Course,
    Lesson,
    Progress,
    Interview,
    Resume,
    Placement
)

from app.routes.auth_routes import router as auth_router
from app.routes.learning_routes import router as learning_router
from app.routes.interview_routes import router as interview_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.resume_routes import router as resume_router
from app.routes.placement_routes import router as placement_router
from app.routes.admin_routes import router as admin_router
from app.routes.progress_routes import router as progress_router
from app.routers.jev_placement import router as jev_placement_router
from app.routes.topic_routes import router as topic_router
from app.routes.question_routes import router as question_router

from app.middleware.error_middleware import (
    http_exception_handler,
    general_exception_handler,
    request_validation_exception_handler,
)
from app.routes import student_interview_skill_routes
from app.routes import interview_ai_routes
from app.routes.interview_session_routes import router as interview_session_router
from app.routes.mcq_interview_routes import router as mcq_interview_router


Base.metadata.create_all(bind=engine)
ensure_email_otp_columns()


api_app = FastAPI(
    title="CodeSphere API",
    description="Backend API for the CodeSphere student platform",
    version="1.0.0"
)

# Error handlers
api_app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler
)
api_app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler
)
api_app.add_exception_handler(
    Exception,
    general_exception_handler
)


# API Routes
api_app.include_router(auth_router)
api_app.include_router(learning_router)
api_app.include_router(interview_router)
api_app.include_router(dashboard_router)
api_app.include_router(resume_router)
api_app.include_router(placement_router)
api_app.include_router(admin_router)
api_app.include_router(progress_router)
api_app.include_router(jev_placement_router)
api_app.include_router(topic_router)
api_app.include_router(question_router)
api_app.include_router(student_interview_skill_routes.router)
api_app.include_router(interview_ai_routes.router)
api_app.include_router(interview_session_router)
api_app.include_router(mcq_interview_router)


# Serve React frontend static files
FRONTEND_DIST = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "frontend", "dist"
)
FRONTEND_DIST = os.path.abspath(FRONTEND_DIST)

if os.path.exists(FRONTEND_DIST):
    # Serve static assets (JS, CSS, images)
    api_app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets"
    )

    # Catch-all: return index.html for any non-API route (React Router support)
    @api_app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index_file)


app = CORSMiddleware(
    app=api_app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)