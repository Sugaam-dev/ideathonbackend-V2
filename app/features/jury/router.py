from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.database import get_db
from app.features.auth.models import User
from app.features.auth.dependencies import require_jury_or_admin
from app.features.jury import services
from app.features.jury.schemas import EvaluationRequest, EvaluationResponse
from app.features.ideas.schemas import IdeaResponse

jury_router = APIRouter(prefix="/api/jury", tags=["Jury Evaluation Panel"])

@jury_router.get("/ideas", response_model=List[IdeaResponse])
def get_all_ideas(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db=Depends(get_db),
    user: User = Depends(require_jury_or_admin)
):
    # Logic moved from filter_ideas_for_admin to jury/services.py
    return services.filter_ideas_for_jury(db, status=status, category=category, search=search)

@jury_router.post("/{idea_id}/evaluate", response_model=EvaluationResponse)
def submit_evaluation(
    idea_id: str,
    req: EvaluationRequest,
    db=Depends(get_db),
    user: User = Depends(require_jury_or_admin)
):
    return services.process_jury_evaluation_card(db, idea_id, user.id, req)