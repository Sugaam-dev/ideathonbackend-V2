# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# from datetime import datetime


# # =========================
# # IDEA CREATE / UPDATE REQUEST
# # =========================
# class IdeaCreateOrUpdateRequest(BaseModel):
#     title: str = Field(..., min_length=10, max_length=1200)
#     problem_statement: str = Field(..., min_length=80, max_length=6000)
#     proposed_solution: str = Field(..., min_length=80, max_length=30000)

#     category: str
#     target_audience: str
#     current_stage: str

#     market_opportunity: Optional[str] = Field(None, min_length=50, max_length=3000)
#     competitive_advantage: Optional[str] = Field(None, min_length=50, max_length=3000)
#     revenue_model: Optional[str] = None
#     business_impact: Optional[str] = Field(None, min_length=50, max_length=3000)
#     scalability: Optional[str] = Field(None, min_length=50, max_length=3000)
#     tech_requirements: Optional[str] = Field(None, min_length=30)

#     figma_link: Optional[str] = None
#     github_link: Optional[str] = None
#     drive_link: Optional[str] = None
#     demo_url: Optional[str] = None


# # =========================
# # ATTACHMENT RESPONSE
# # =========================
# class AttachmentResponse(BaseModel):
#     id: str
#     original_name: str
#     file_size: int
#     uploaded_at: datetime

#     class Config:
#         from_attributes = True


# # =========================
# # 🔥 NEW: EVALUATION BREAKDOWN
# # =========================
# class EvaluationBreakdown(BaseModel):
#     reviewer_id: str

#     innovation_score: int
#     feasibility_score: int
#     market_score: int
#     scalability_score: int

#     comments: Optional[str] = None


# # =========================
# # IDEA RESPONSE (FULL POWER VERSION)
# # =========================
# class IdeaResponse(BaseModel):
#     id: str
#     submitter_order_number: int

#     # 🔥 NEW: Submitter Details for Admin Dashboard
#     submitter_name: str
#     submitter_email: str
#     submitter_organization: Optional[str] = None

#     title: str
#     category: str
#     status: str
#     current_stage: str

#     problem_statement: str
#     proposed_solution: str
#     target_audience: str

#     # Business fields
#     market_opportunity: Optional[str]
#     competitive_advantage: Optional[str]
#     revenue_model: Optional[str]
#     business_impact: Optional[str]
#     scalability: Optional[str]
#     tech_requirements: Optional[str]

#     # External links
#     figma_link: Optional[str]
#     github_link: Optional[str]
#     drive_link: Optional[str]
#     demo_url: Optional[str]

#     # Evaluation summary
#     evaluation_score: Optional[float] = None
#     reviewer_notes: Optional[str] = None

#     # 🔥 NEW: FULL JUDGE MARKS
#     evaluations: List[EvaluationBreakdown] = Field(default_factory=list)

#     submitted_at: datetime

#     # Attachments
#     attachments: List[AttachmentResponse] = Field(default_factory=list)

#     class Config:
#         from_attributes = True


# # =========================
# # EVALUATION REQUEST
# # =========================
# class EvaluationCreateRequest(BaseModel):
#     innovation_score: int = Field(..., ge=1, le=10)
#     feasibility_score: int = Field(..., ge=1, le=10)
#     market_score: int = Field(..., ge=1, le=10)
#     scalability_score: int = Field(..., ge=1, le=10)

#     comments: Optional[str] = None


# # =========================
# # EVALUATION RESPONSE
# # =========================
# class EvaluationResponse(BaseModel):
#     success: bool
#     idea_id: str
#     status: str
#     evaluation_score: Optional[float]
#     message: str


# # =========================
# # ADMIN STATS RESPONSE
# # =========================
# class AdminStatsResponse(BaseModel):
#     total_participants: int
#     total_ideas: int
#     shortlisted: int
#     under_review: int
#     selected: int

#     by_category: List[Dict[str, Any]] = Field(default_factory=list)



from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
# =========================
# IDEA CREATE / UPDATE REQUEST
# =========================
class IdeaCreateOrUpdateRequest(BaseModel):
    title: str = Field(..., min_length=10, max_length=1200)
    problem_statement: str = Field(..., min_length=80, max_length=6000)
    proposed_solution: str = Field(..., min_length=80, max_length=30000)
    category: str
    target_audience: str
    current_stage: str
    market_opportunity: Optional[str] = Field(None, min_length=50, max_length=3000)
    competitive_advantage: Optional[str] = Field(None, min_length=50, max_length=3000)
    revenue_model: Optional[str] = None
    business_impact: Optional[str] = Field(None, min_length=50, max_length=3000)
    scalability: Optional[str] = Field(None, min_length=50, max_length=3000)
    tech_requirements: Optional[str] = Field(None, min_length=30)
    figma_link: Optional[str] = None
    github_link: Optional[str] = None
    drive_link: Optional[str] = None
    demo_url: Optional[str] = None
# =========================
# ATTACHMENT RESPONSE
# =========================
class AttachmentResponse(BaseModel):
    id: str
    original_name: str
    file_size: int
    uploaded_at: datetime
    class Config:
        from_attributes = True
# =========================
# 🔥 NEW: EVALUATION BREAKDOWN
# =========================
class EvaluationBreakdown(BaseModel):
    reviewer_id: str
    innovation_score: int
    feasibility_score: int
    market_score: int
    scalability_score: int
    comments: Optional[str] = None
# =========================
# IDEA RESPONSE (FULL POWER VERSION)
# =========================
class IdeaResponse(BaseModel):
    id: str
    submitter_order_number: int
    # 🔥 NEW: Submitter Details for Admin Dashboard
    submitter_name: str
    submitter_email: str
    submitter_organization: Optional[str] = None
    title: str
    category: str
    status: str
    current_stage: str
    problem_statement: str
    proposed_solution: str
    target_audience: str
    # Business fields
    market_opportunity: Optional[str]
    competitive_advantage: Optional[str]
    revenue_model: Optional[str]
    business_impact: Optional[str]
    scalability: Optional[str]
    tech_requirements: Optional[str]
    # External links
    figma_link: Optional[str]
    github_link: Optional[str]
    drive_link: Optional[str]
    demo_url: Optional[str]
    # Evaluation summary
    evaluation_score: Optional[float] = None
    reviewer_notes: Optional[str] = None
    # 🔥 NEW: FULL JUDGE MARKS
    evaluations: List[EvaluationBreakdown] = Field(default_factory=list)
    submitted_at: datetime
    # Attachments
    attachments: List[AttachmentResponse] = Field(default_factory=list)
    class Config:
        from_attributes = True
# =========================
# EVALUATION REQUEST
# =========================
class EvaluationCreateRequest(BaseModel):
    innovation_score: int = Field(..., ge=1, le=10)
    feasibility_score: int = Field(..., ge=1, le=10)
    market_score: int = Field(..., ge=1, le=10)
    scalability_score: int = Field(..., ge=1, le=10)
    comments: Optional[str] = None
# =========================
# EVALUATION RESPONSE
# =========================
class EvaluationResponse(BaseModel):
    success: bool
    idea_id: str
    status: str
    evaluation_score: Optional[float]
    message: str
# =========================
# ADMIN STATS RESPONSE
# =========================
class AdminStatsResponse(BaseModel):
    total_participants: int
    total_ideas: int
    shortlisted: int
    under_review: int
    selected: int
    by_category: List[Dict[str, Any]] = Field(default_factory=list)
# ==========================================
# 🔥 NEW: ADMINISTRATIVE USER AUDITING SCHEMAS
# ==========================================
class AdminUserIdeaSummary(BaseModel):
    id: str
    title: str
    category: str
    status: str
    submitted_at: datetime
    class Config:
        from_attributes = True
class AdminUserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_profile_complete: bool
    ideas_count: int
    created_at: datetime
    class Config:
        from_attributes = True
class AdminUserDetailResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    internship_id: Optional[str] = None
    department: Optional[str] = None
    linkedin: Optional[str] = None
    role: str
    is_profile_complete: bool
    created_at: datetime
    # Resume metadata
    resume_filename: Optional[str] = None
    has_resume: bool
    # User's submissions list
    ideas: List[AdminUserIdeaSummary] = Field(default_factory=list)
    class Config:
        from_attributes = True
