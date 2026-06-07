# # app/features/ideas/services.py
# import uuid
# import os
# import io
# from typing import List, Dict, Any, Optional
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from app.config import settings
# from app.core import email
# from fastapi import UploadFile, BackgroundTasks

# # 🗄️ Core Models Division mapping
# from app.features.ideas.models import Idea, Attachment
# from app.features.evaluations.models import Evaluation
# from app.features.auth.models import User

# from app.features.ideas.schemas import IdeaCreateOrUpdateRequest, EvaluationCreateRequest
# from app.core.exceptions import ResourceNotFoundError, PermissionDeniedError, BadRequestError


# def idea_to_response(db: Session, idea: Idea) -> Dict[str, Any]:
#     """Single source of truth for Idea API responses."""
    
#     # Fetch the submitter profile for the administrative dashboard
#     submitter = db.query(User).filter(User.id == idea.user_id).first()

#     attachments = [
#         {
#             "id": a.id,
#             "original_name": a.original_name,
#             "file_size": a.file_size,
#             "uploaded_at": a.uploaded_at
#         }
#         for a in idea.attachments
#     ]

#     evaluations = [
#         {
#             "reviewer_id": e.reviewer_id,
#             "innovation_score": e.innovation_score,
#             "feasibility_score": e.feasibility_score,
#             "market_score": e.market_score,
#             "scalability_score": e.scalability_score,
#             "comments": e.comments
#         }
#         for e in idea.evaluations
#     ]

#     order_num = calculate_portfolio_serial_number(db, idea.user_id, idea.id)

#     return {
#         "id": idea.id,
#         "submitter_order_number": order_num,
        
#         # Submitter Details for Admin Dashboard
#         "submitter_name": submitter.name if submitter else "Anonymous",
#         "submitter_email": submitter.email if submitter else "N/A",
#         "submitter_organization": submitter.organization if submitter else "N/A",

#         "title": idea.title,
#         "category": idea.category,
#         "status": idea.status,
#         "current_stage": idea.current_stage,

#         "problem_statement": idea.problem_statement,
#         "proposed_solution": idea.proposed_solution,
#         "target_audience": idea.target_audience,

#         "market_opportunity": idea.market_opportunity,
#         "competitive_advantage": idea.competitive_advantage,
#         "revenue_model": idea.revenue_model,
#         "business_impact": idea.business_impact,
#         "scalability": idea.scalability,
#         "tech_requirements": idea.tech_requirements,

#         "figma_link": idea.figma_link,
#         "github_link": idea.github_link,
#         "drive_link": idea.drive_link,
#         "demo_url": idea.demo_url,

#         "evaluation_score": idea.evaluation_score,
#         "reviewer_notes": idea.reviewer_notes,

#         # FULL JUDGE MARKS
#         "evaluations": evaluations,

#         "submitted_at": idea.submitted_at,

#         "attachments": attachments
#     }

# def notify_admin_new_idea(idea_title: str, user_name: str):
#     subject = "New Innovation Idea Submitted!"
#     html_content = f"<p>A new idea <b>'{idea_title}'</b> was submitted by {user_name}.</p>"
#     email.send_transactional_email(settings.SMTP_FROM_EMAIL, subject, html_content)

# def notify_user_status_update(user_email: str, idea_title: str, new_status: str):
#     subject = "Idea Status Update"
#     html_content = f"<p>The status of your idea <b>'{idea_title}'</b> has been updated to: <b>{new_status}</b>.</p>"
#     email.send_transactional_email(user_email, subject, html_content)

# def calculate_portfolio_serial_number(db: Session, user_id: str, idea_id: str) -> int:
#     """Dynamically computes a user's clean chronological tracker order index count."""
#     user_portfolio = (
#         db.query(Idea.id)
#         .filter(Idea.user_id == user_id)
#         .order_by(Idea.submitted_at.asc())
#         .all()
#     )
#     portfolio_ids = [row[0] for row in user_portfolio]
#     try:
#         return portfolio_ids.index(idea_id) + 1
#     except ValueError:
#         return len(portfolio_ids) + 1


# def fetch_administrative_dashboard_metrics(db: Session) -> Dict[str, Any]:
#     """Compiles global KPI summaries offloading math operations directly to the database layer."""
#     total_users = db.query(User).filter(User.role == "PARTICIPANT").count()
#     total_ideas = db.query(Idea).count()
    
#     shortlisted = db.query(Idea).filter(Idea.status == "Shortlisted").count()
#     under_review = db.query(Idea).filter(Idea.status == "Under Review").count()
#     selected = db.query(Idea).filter(Idea.status == "Selected").count()
    
#     category_counts = (
#         db.query(Idea.category, func.count(Idea.id))
#         .group_by(Idea.category)
#         .all()
#     )
    
#     return {
#         "total_participants": total_users,
#         "total_ideas": total_ideas,
#         "shortlisted": shortlisted,
#         "under_review": under_review,
#         "selected": selected,
#         "by_category": [{"category": r[0], "count": r[1]} for r in category_counts]
#     }


# def fetch_global_submissions_pool(db: Session, category=None, status=None, search=None):
#     query = db.query(Idea).join(User, Idea.user_id == User.id)

#     if category:
#         query = query.filter(Idea.category.ilike(category)) 
        
#     if status:
#         query = query.filter(Idea.status == status)
        
#     if search:
#         pattern = f"%{search}%"
#         query = query.filter(
#             (Idea.title.ilike(pattern)) |
#             (User.name.ilike(pattern))
#         )

#     ideas = query.order_by(Idea.submitted_at.desc()).all()
#     return [idea_to_response(db, idea) for idea in ideas]


# def log_new_participant_idea(db, user_name, user_email, user_id, req, background_tasks, idempotency_key=None):
#     if idempotency_key:
#         existing = db.query(Idea).filter(Idea.idempotency_key == idempotency_key).first()
#         if existing:
#             raise BadRequestError("Duplicate submission blocked.")

#     # 🚨 LIMIT CHECK: A user can submit at most 3 ideas
#     existing_count = db.query(Idea).filter(Idea.user_id == user_id).count()
#     if existing_count >= 3:
#         raise BadRequestError("You have reached the maximum limit of 3 ideas.")

#     idea = Idea(
#         id=str(uuid.uuid4()),
#         user_id=user_id,
#         idempotency_key=idempotency_key,
#         status="Submitted",
#         **req.model_dump()
#     )

#     db.add(idea)
#     db.commit()
#     db.refresh(idea)
    
#     background_tasks.add_task(notify_admin_new_idea, idea.title, user_name)
    
#     return idea_to_response(db, idea)


# async def store_idea_binary_file(db: Session, idea_id: str, user_id: str, is_admin: bool, file: UploadFile) -> Attachment:
#     """Streams incoming file byte strings directly into an isolated database row cell."""
#     idea = db.query(Idea).filter(Idea.id == idea_id).first()
#     if not idea:
#         raise ResourceNotFoundError("Target submission node could not be located.")
        
#     if idea.user_id != user_id and not is_admin:
#         raise PermissionDeniedError("You lack structural authorizations to modify this data space.")
        
#     if not is_admin and idea.status != "Submitted":
#         raise BadRequestError(f"Upload blocked. Assets are frozen in the '{idea.status}' stage.")

#     # 🚨 LIMIT CHECK: An idea can have at most 1 attachment/document
#     existing_attachments = db.query(Attachment).filter(Attachment.idea_id == idea_id).count()
#     if existing_attachments >= 1:
#         raise BadRequestError("This idea already has an attachment. Please delete the existing attachment before uploading a new one.")

#     raw_binary_bytes = await file.read()
#     computed_file_size = len(raw_binary_bytes)

#     unique_file_id = str(uuid.uuid4())
#     _, file_ext = os.path.splitext(file.filename or "")
#     scrambled_filename = f"{unique_file_id}{file_ext}"
    
#     attachment_entry = Attachment(
#         id=unique_file_id,
#         idea_id=idea_id,
#         filename=scrambled_filename,
#         original_name=file.filename or "unnamed_upload",
#         file_size=computed_file_size,
#         file_data=raw_binary_bytes
#     )
#     db.add(attachment_entry)
#     db.commit()
#     db.refresh(attachment_entry)
#     return attachment_entry


# def fetch_participant_portfolio_summary(db, user_id):
#     ideas = db.query(Idea).filter(Idea.user_id == user_id).order_by(Idea.submitted_at.desc()).all()
#     return [idea_to_response(db, idea) for idea in ideas]


# def fetch_single_idea_secured(db, idea_id, user_id, role):
#     idea = db.query(Idea).filter(Idea.id == idea_id).first()
#     if not idea:
#         raise ResourceNotFoundError("Not found.")
#     if role not in ["ADMIN", "JURY"] and idea.user_id != user_id:
#         raise PermissionDeniedError("Access denied.")
#     return idea_to_response(db, idea)


# def modify_submission_pipeline_status(db: Session, idea_id: str, target_status: str, background_tasks: BackgroundTasks):
#     idea = db.query(Idea).filter(Idea.id == idea_id).first()
#     if not idea:
#         raise ResourceNotFoundError("Not found.")
    
#     user = db.query(User).filter(User.id == idea.user_id).first()
    
#     idea.status = target_status
#     db.commit()
#     db.refresh(idea)
    
#     if user and user.email:
#         background_tasks.add_task(notify_user_status_update, user.email, idea.title, target_status)
        
#     return idea_to_response(db, idea)


# def modify_existing_participant_idea(db, idea_id, user_id, is_admin, req):
#     idea = db.query(Idea).filter(Idea.id == idea_id).first()
#     if not idea:
#         raise ResourceNotFoundError("Entry does not exist.")
#     if idea.user_id != user_id and not is_admin:
#         raise PermissionDeniedError("Access denied.")
#     if not is_admin and idea.status != "Submitted":
#         raise BadRequestError("Idea locked after submission.")
#     for key, value in req.model_dump().items():
#         setattr(idea, key, value)
#     db.commit()
#     db.refresh(idea)
#     return idea_to_response(db, idea)

# def delete_idea_attachment(db: Session, attachment_id: str, user_id: str, is_admin: bool):
#     attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
#     if not attachment:
#         raise ResourceNotFoundError("Attachment not found.")

#     idea = db.query(Idea).filter(Idea.id == attachment.idea_id).first()
    
#     if idea.user_id != user_id and not is_admin:
#         raise PermissionDeniedError("Access denied.")
#     if not is_admin and idea.status != "Submitted":
#         raise BadRequestError(f"Delete blocked. Assets are frozen in the '{idea.status}' stage.")

#     db.delete(attachment)
#     db.commit()
#     return {"success": True}



# app/features/ideas/services.py
import uuid
import os
import io
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import settings
from app.core import email
from fastapi import UploadFile, BackgroundTasks
# 🗄️ Core Models Division mapping
from app.features.ideas.models import Idea, Attachment, AttachmentData
from app.features.evaluations.models import Evaluation
from app.features.auth.models import User
from app.features.ideas.schemas import IdeaCreateOrUpdateRequest, EvaluationCreateRequest
from app.core.exceptions import ResourceNotFoundError, PermissionDeniedError, BadRequestError
def idea_to_response(db: Session, idea: Idea) -> Dict[str, Any]:
    """Single source of truth for Idea API responses."""
    
    # Fetch the submitter profile for the administrative dashboard
    submitter = db.query(User).filter(User.id == idea.user_id).first()
    attachments = [
        {
            "id": a.id,
            "original_name": a.original_name,
            "file_size": a.file_size,
            "uploaded_at": a.uploaded_at
        }
        for a in idea.attachments
    ]
    evaluations = [
        {
            "reviewer_id": e.reviewer_id,
            "innovation_score": e.innovation_score,
            "feasibility_score": e.feasibility_score,
            "market_score": e.market_score,
            "scalability_score": e.scalability_score,
            "comments": e.comments
        }
        for e in idea.evaluations
    ]
    order_num = calculate_portfolio_serial_number(db, idea.user_id, idea.id)
    return {
        "id": idea.id,
        "submitter_order_number": order_num,
        
        # Submitter Details for Admin Dashboard
        "submitter_name": submitter.name if submitter else "Anonymous",
        "submitter_email": submitter.email if submitter else "N/A",
        "submitter_organization": submitter.organization if submitter else "N/A",
        "title": idea.title,
        "category": idea.category,
        "status": idea.status,
        "current_stage": idea.current_stage,
        "problem_statement": idea.problem_statement,
        "proposed_solution": idea.proposed_solution,
        "target_audience": idea.target_audience,
        "market_opportunity": idea.market_opportunity,
        "competitive_advantage": idea.competitive_advantage,
        "revenue_model": idea.revenue_model,
        "business_impact": idea.business_impact,
        "scalability": idea.scalability,
        "tech_requirements": idea.tech_requirements,
        "figma_link": idea.figma_link,
        "github_link": idea.github_link,
        "drive_link": idea.drive_link,
        "demo_url": idea.demo_url,
        "evaluation_score": idea.evaluation_score,
        "reviewer_notes": idea.reviewer_notes,
        # FULL JUDGE MARKS
        "evaluations": evaluations,
        "submitted_at": idea.submitted_at,
        "attachments": attachments
    }
def notify_admin_new_idea(idea_title: str, user_name: str):
    subject = "New Innovation Idea Submitted!"
    html_content = f"<p>A new idea <b>'{idea_title}'</b> was submitted by {user_name}.</p>"
    email.send_transactional_email(settings.SMTP_FROM_EMAIL, subject, html_content)
def notify_user_status_update(user_email: str, idea_title: str, new_status: str):
    subject = "Idea Status Update"
    html_content = f"<p>The status of your idea <b>'{idea_title}'</b> has been updated to: <b>{new_status}</b>.</p>"
    email.send_transactional_email(user_email, subject, html_content)
def calculate_portfolio_serial_number(db: Session, user_id: str, idea_id: str) -> int:
    """Dynamically computes a user's clean chronological tracker order index count."""
    user_portfolio = (
        db.query(Idea.id)
        .filter(Idea.user_id == user_id)
        .order_by(Idea.submitted_at.asc())
        .all()
    )
    portfolio_ids = [row[0] for row in user_portfolio]
    try:
        return portfolio_ids.index(idea_id) + 1
    except ValueError:
        return len(portfolio_ids) + 1
def fetch_administrative_dashboard_metrics(db: Session) -> Dict[str, Any]:
    """Compiles global KPI summaries offloading math operations directly to the database layer."""
    total_users = db.query(User).filter(User.role == "PARTICIPANT").count()
    total_ideas = db.query(Idea).count()
    
    shortlisted = db.query(Idea).filter(Idea.status == "Shortlisted").count()
    under_review = db.query(Idea).filter(Idea.status == "Under Review").count()
    selected = db.query(Idea).filter(Idea.status == "Selected").count()
    
    category_counts = (
        db.query(Idea.category, func.count(Idea.id))
        .group_by(Idea.category)
        .all()
    )
    
    return {
        "total_participants": total_users,
        "total_ideas": total_ideas,
        "shortlisted": shortlisted,
        "under_review": under_review,
        "selected": selected,
        "by_category": [{"category": r[0], "count": r[1]} for r in category_counts]
    }
def fetch_global_submissions_pool(db: Session, category=None, status=None, search=None):
    query = db.query(Idea).join(User, Idea.user_id == User.id)
    if category:
        query = query.filter(Idea.category.ilike(category)) 
        
    if status:
        query = query.filter(Idea.status == status)
        
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Idea.title.ilike(pattern)) |
            (User.name.ilike(pattern))
        )
    ideas = query.order_by(Idea.submitted_at.desc()).all()
    return [idea_to_response(db, idea) for idea in ideas]
def log_new_participant_idea(db, user_name, user_email, user_id, req, background_tasks, idempotency_key=None):
    if idempotency_key:
        existing = db.query(Idea).filter(Idea.idempotency_key == idempotency_key).first()
        if existing:
            raise BadRequestError("Duplicate submission blocked.")
    # 🚨 LIMIT CHECK: A user can submit at most 3 ideas
    existing_count = db.query(Idea).filter(Idea.user_id == user_id).count()
    if existing_count >= 3:
        raise BadRequestError("You have reached the maximum limit of 3 ideas.")
    idea = Idea(
        id=str(uuid.uuid4()),
        user_id=user_id,
        idempotency_key=idempotency_key,
        status="Submitted",
        **req.model_dump()
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    
    background_tasks.add_task(notify_admin_new_idea, idea.title, user_name)
    
    return idea_to_response(db, idea)
async def store_idea_binary_file(db: Session, idea_id: str, user_id: str, is_admin: bool, file: UploadFile) -> Attachment:
    """Streams incoming file byte strings directly into an isolated database row cell."""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Target submission node could not be located.")
        
    if idea.user_id != user_id and not is_admin:
        raise PermissionDeniedError("You lack structural authorizations to modify this data space.")
        
    if not is_admin and idea.status != "Submitted":
        raise BadRequestError(f"Upload blocked. Assets are frozen in the '{idea.status}' stage.")
    # 🚨 LIMIT CHECK: An idea can have at most 1 attachment/document
    existing_attachments = db.query(Attachment).filter(Attachment.idea_id == idea_id).count()
    if existing_attachments >= 1:
        raise BadRequestError("This idea already has an attachment. Please delete the existing attachment before uploading a new one.")
    raw_binary_bytes = await file.read()
    computed_file_size = len(raw_binary_bytes)
    unique_file_id = str(uuid.uuid4())
    _, file_ext = os.path.splitext(file.filename or "")
    scrambled_filename = f"{unique_file_id}{file_ext}"
    
    attachment_entry = Attachment(
        id=unique_file_id,
        idea_id=idea_id,
        filename=scrambled_filename,
        original_name=file.filename or "unnamed_upload",
        file_size=computed_file_size
    )
    db.add(attachment_entry)
    db.flush()  # Generate primary key ID for Attachment
    
    binary_entry = AttachmentData(
        id=str(uuid.uuid4()),
        attachment_id=attachment_entry.id,
        file_data=raw_binary_bytes
    )
    db.add(binary_entry)
    db.commit()
    db.refresh(attachment_entry)
    return attachment_entry
def fetch_participant_portfolio_summary(db, user_id):
    ideas = db.query(Idea).filter(Idea.user_id == user_id).order_by(Idea.submitted_at.desc()).all()
    return [idea_to_response(db, idea) for idea in ideas]
def fetch_single_idea_secured(db, idea_id, user_id, role):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Not found.")
    if role not in ["ADMIN", "JURY"] and idea.user_id != user_id:
        raise PermissionDeniedError("Access denied.")
    return idea_to_response(db, idea)
def modify_submission_pipeline_status(db: Session, idea_id: str, target_status: str, background_tasks: BackgroundTasks):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Not found.")
    
    user = db.query(User).filter(User.id == idea.user_id).first()
    
    idea.status = target_status
    db.commit()
    db.refresh(idea)
    
    if user and user.email:
        background_tasks.add_task(notify_user_status_update, user.email, idea.title, target_status)
        
    return idea_to_response(db, idea)
def modify_existing_participant_idea(db, idea_id, user_id, is_admin, req):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Entry does not exist.")
    if idea.user_id != user_id and not is_admin:
        raise PermissionDeniedError("Access denied.")
    if not is_admin and idea.status != "Submitted":
        raise BadRequestError("Idea locked after submission.")
    for key, value in req.model_dump().items():
        setattr(idea, key, value)
    db.commit()
    db.refresh(idea)
    return idea_to_response(db, idea)
def delete_idea_attachment(db: Session, attachment_id: str, user_id: str, is_admin: bool):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise ResourceNotFoundError("Attachment not found.")
    idea = db.query(Idea).filter(Idea.id == attachment.idea_id).first()
    
    if idea.user_id != user_id and not is_admin:
        raise PermissionDeniedError("Access denied.")
    if not is_admin and idea.status != "Submitted":
        raise BadRequestError(f"Delete blocked. Assets are frozen in the '{idea.status}' stage.")
    db.delete(attachment)
    db.commit()
    return {"success": True}
# =====================================================================
# 🔥 NEW: ADMINISTRATIVE USER AUDITING GATEWAY SERVICES
# =====================================================================
def fetch_admin_users_list(db: Session) -> List[Dict[str, Any]]:
    """Lists all registered users in the database alongside their submitted ideas count."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        idea_count = db.query(Idea).filter(Idea.user_id == u.id).count()
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_profile_complete": u.is_profile_complete,
            "ideas_count": idea_count,
            "created_at": u.created_at
        })
    return result
def fetch_admin_user_details(db: Session, user_id: str) -> Dict[str, Any]:
    """Retrieves full details of a specific user including their ideas submissions list."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise ResourceNotFoundError("Target user account does not exist.")
    
    ideas = db.query(Idea).filter(Idea.user_id == user_id).order_by(Idea.submitted_at.desc()).all()
    ideas_list = [
        {
            "id": idea.id,
            "title": idea.title,
            "category": idea.category,
            "status": idea.status,
            "submitted_at": idea.submitted_at
        }
        for idea in ideas
    ]
    
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "organization": u.organization,
        "internship_id": u.internship_id,
        "department": u.department,
        "linkedin": u.linkedin,
        "role": u.role,
        "is_profile_complete": u.is_profile_complete,
        "created_at": u.created_at,
        "resume_filename": u.resume_filename,
        "has_resume": u.resume_filename is not None,
        "ideas": ideas_list
    }
def download_user_resume_by_admin(db: Session, user_id: str) -> tuple:
    """Retrieves user's resume binary content from DB resumes table for administrative audit download."""
    u = db.query(User).filter(User.id == user_id).first()
    if not u or not u.resume_filename:
        raise ResourceNotFoundError("No resume uploaded for this profile account.")
    
    from app.features.auth.models import Resume
    resume = db.query(Resume).filter(Resume.user_id == user_id).first()
    if not resume:
        raise ResourceNotFoundError("Resume binary data could not be found in database.")
        
    return resume.file_data, u.resume_filename
