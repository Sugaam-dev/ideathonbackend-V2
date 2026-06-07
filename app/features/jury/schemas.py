from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Target workflow phase indicator")

class EvaluationRequest(BaseModel):
    innovation_score: int = Field(..., ge=1, le=10, description="Innovation parameter bounded between 1 and 10")
    feasibility_score: int = Field(..., ge=1, le=10, description="Feasibility parameter bounded between 1 and 10")
    market_score: int = Field(..., ge=1, le=10, description="Market viability parameter bounded between 1 and 10")
    scalability_score: int = Field(..., ge=1, le=10, description="Scalability parameters bounded between 1 and 10")
    comments: Optional[str] = None

class CategoryCountItem(BaseModel):
    category: str
    count: int

class SystemStatsResponse(BaseModel):
    total_participants: int
    total_ideas: int
    shortlisted: int
    under_review: int
    selected: int
    by_category: List[CategoryCountItem]

class EvaluationResponse(BaseModel):
    id: str
    idea_id: str
    reviewer_id: Optional[str]
    innovation_score: int
    feasibility_score: int
    market_score: int
    scalability_score: int
    comments: Optional[str]
    evaluated_at: datetime

    class Config:
        from_attributes = True