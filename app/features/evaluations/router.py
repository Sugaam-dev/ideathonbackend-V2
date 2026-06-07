from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.features.auth.models import User
from app.features.auth.dependencies import require_admin, require_jury_or_admin
from app.features.evaluations.schemas import EvaluationRequest, StatusUpdateRequest, SystemStatsResponse
from app.features.evaluations import services

router = APIRouter(prefix="/api/admin", tags=["Administrative Evaluation Panels"])

@router.get("/stats", response_model=SystemStatsResponse)
def get_global_hackathon_statistics(
    admin: User = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Compiles platform engagement summaries for administrative dashboard viewports."""
    return services.fetch_platform_metrics(db)

@router.get("/ideas")
def get_all_submitted_ideas(
    status: Optional[str] = Query(None), 
    category: Optional[str] = Query(None), 
    search: Optional[str] = Query(None), 
    admin: User = Depends(require_jury_or_admin), 
    db: Session = Depends(get_db)
):
    """Provides system-wide text lookup and structural column filtering for evaluation panels."""
    return services.filter_ideas_for_admin(db, status, category, search)

@router.put("/ideas/{idea_id}/status")
def update_submission_lifecycle_state(
    idea_id: str, 
    req: StatusUpdateRequest, 
    background_tasks: BackgroundTasks, 
    admin: User = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Updates an idea's status flag and dispatches an automated notification email to the participant."""
    return services.execute_idea_lifecycle_transition(db, idea_id, req.status, background_tasks)

@router.post("/ideas/{idea_id}/evaluate", status_code=status.HTTP_201_CREATED)
def evaluate_idea_submission(
    idea_id: str, 
    req: EvaluationRequest, 
    admin: User = Depends(require_admin), # RESTRICTED TO ADMIN
    db: Session = Depends(get_db)
):
    return services.process_jury_evaluation_card(db, idea_id, admin.id, req)