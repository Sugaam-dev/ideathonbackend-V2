from typing import List, Optional
import io
from fastapi import APIRouter, Depends, status, Query, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.features.auth.models import User
from app.features.auth.dependencies import require_admin, require_completed_profile
from app.features.ideas.schemas import (
    IdeaResponse,
    EvaluationCreateRequest,
    AdminStatsResponse,
    EvaluationResponse,
    AdminUserResponse,
    AdminUserDetailResponse,
    PaginatedEmailLogsResponse
)
# Import services
from app.features.ideas import services as idea_services
from app.features.evaluations import services as eval_services
admin_router = APIRouter(
    prefix="/api/admin/ideas",
    tags=["Administrative Control Panel"],
    dependencies=[Depends(require_completed_profile)]
)
# Request model for status updates
class StatusUpdateRequest(BaseModel):
    status: str
@admin_router.get("/stats", response_model=AdminStatsResponse)
def get_portal_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return idea_services.fetch_administrative_dashboard_metrics(db)
@admin_router.get("", response_model=List[IdeaResponse])
def get_global_submissions_pool(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return idea_services.fetch_global_submissions_pool(
        db,
        category=category,
        status=status,
        search=search
    )
@admin_router.post(
    "/{idea_id}/evaluate",
    status_code=status.HTTP_201_CREATED,
    response_model=EvaluationResponse
)
def submit_project_scorecard(
    idea_id: str,
    req: EvaluationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Call the correct service function from the evaluations module
    return eval_services.process_jury_evaluation_card(
        db,
        idea_id,
        current_user.id,
        req
    )
@admin_router.patch("/{idea_id}/status", response_model=IdeaResponse)
def update_project_pipeline_status(
    idea_id: str,
    req: StatusUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return idea_services.modify_submission_pipeline_status(
        db, idea_id, req.status, background_tasks
    )
# =====================================================================
# 🔥 NEW: ADMINISTRATIVE USER ACCOUNT AUDITING ENDPOINTS
# =====================================================================
@admin_router.get("/users", response_model=List[AdminUserResponse])
def get_all_user_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Retrieves list of all registered portal user accounts with basic metrics."""
    return idea_services.fetch_admin_users_list(db)
@admin_router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
def get_user_account_details(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Retrieves full profile audit log, resume metadata, and ideas submissions list for a target user."""
    return idea_services.fetch_admin_user_details(db, user_id)
@admin_router.get("/users/{user_id}/resume/download")
def download_user_resume(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Downloads/streams a participant user's resume document directly from the database resumes table."""
    file_data, filename = idea_services.download_user_resume_by_admin(db, user_id)
    file_stream = io.BytesIO(file_data)
    
    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
@admin_router.get("/email-logs", response_model=PaginatedEmailLogsResponse)
def get_administrative_email_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Retrieves paginated audit logs of all outgoing email transactions (SMTP rotation/attempts)."""
    return idea_services.fetch_administrative_email_logs(
        db, page=page, limit=limit, status=status, search=search
    )
