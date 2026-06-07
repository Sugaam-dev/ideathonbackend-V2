import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import BackgroundTasks
from app.core import email
from app.core.exceptions import ResourceNotFoundError, BadRequestError
from app.features.auth.models import User
from app.features.ideas.models import Idea
from app.features.ideas.services import calculate_portfolio_serial_number
from app.features.evaluations.models import Evaluation
from app.features.evaluations.schemas import EvaluationRequest
def fetch_platform_metrics(db: Session) -> Dict[str, Any]:
    """Compiles platform-wide interaction analytical metrics for administrative dashboards."""
    total_users = db.query(User).filter(User.role == "PARTICIPANT").count()
    total_ideas = db.query(Idea).count()
    shortlisted = db.query(Idea).filter(Idea.status == "Shortlisted").count()
    under_review = db.query(Idea).filter(Idea.status == "Under Review").count()
    selected = db.query(Idea).filter(Idea.status == "Selected").count()
    
    category_groupings = (
        db.query(Idea.category, func.count(Idea.id).label("count"))
        .group_by(Idea.category)
        .all()
    )
    
    return {
        "total_participants": total_users,
        "total_ideas": total_ideas,
        "shortlisted": shortlisted,
        "under_review": under_review,
        "selected": selected,
        "by_category": [{"category": r[0], "count": r[1]} for r in category_groupings]
    }

def filter_ideas_for_admin(db: Session, status: Optional[str], category: Optional[str], search: Optional[str]) -> List[Dict[str, Any]]:
    """Applies robust sorting and multi-field query strings across global submissions portfolio."""
    query = db.query(Idea).join(User, User.id == Idea.user_id)
    
    if status:
        query = query.filter(Idea.status == status)
    if category:
        query = query.filter(Idea.category == category)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Idea.title.like(search_pattern)) | 
            (User.name.like(search_pattern))
        )
        
    ideas_list = query.order_by(Idea.submitted_at.desc()).all()
    compiled_results = []
    
    for idea in ideas_list:
        submitter = db.query(User).filter(User.id == idea.user_id).first()
        order_num = calculate_portfolio_serial_number(db, idea.user_id, idea.id)
        
        item = idea.__dict__.copy()
        item["submitter_order_number"] = order_num
        item["submitter_name"] = submitter.name if submitter else "Deleted Account"
        item["submitter_email"] = submitter.email if submitter else "N/A"
        item["organization"] = submitter.organization if submitter else None
        item["department"] = submitter.department if submitter else None
        item["attachments"] = idea.attachments
        compiled_results.append(item)
        
    return compiled_results

def dispatch_status_update_email(background_tasks: BackgroundTasks, participant_name: str, participant_email: str, idea_title: str, target_status: str) -> None:
    """Dispatches background HTML update alerts to keep competitors connected with operational milestones."""
    subject = f"Portal Update: Your Idea Status is now '{target_status}'"
    html_layout = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2b6cb0;">Hello {participant_name}!</h2>
            <p>The steering panel has updated the review metrics for your project entry on the <strong>PMRG Ideathon Portal</strong>.</p>
            <p>Your idea submission titled <strong>"{idea_title}"</strong> has been advanced into the following operational stage:</p>
            <div style="margin: 20px 0; padding: 15px; background: #ebf8ff; border-left: 4px solid #3182ce; font-size: 1.1em;">
                <strong>Current Phase:</strong> {target_status}
            </div>
            <p>Please log in to your interactive participant dashboard to view panel comment updates or upcoming milestone targets.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;" />
            <p style="font-size: 0.9em; color: #718096;">This is an automated system dispatch. Please do not reply directly to this mail string.</p>
        </body>
    </html>
    """
    background_tasks.add_task(email.send_transactional_email, participant_email, subject, html_layout)

def execute_idea_lifecycle_transition(db: Session, idea_id: str, status_flag: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Updates tracking status tags and schedules background user alert notifications."""
    valid_milestones = ["Submitted", "Under Review", "Shortlisted", "Interview Scheduled", "Selected", "Incubation Phase", "Closed"]
    if status_flag not in valid_milestones:
        raise BadRequestError("The requested lifecycle status indicator configuration token is invalid.")
        
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Target idea record could not be located in database files.")
        
    idea.status = status_flag
    db.commit()
    
    submitter = db.query(User).filter(User.id == idea.user_id).first()
    if submitter:
        dispatch_status_update_email(background_tasks, submitter.name, submitter.email, idea.title, status_flag)
        
    return {"success": True, "status": status_flag}


def process_jury_evaluation_card(db: Session, idea_id: str, reviewer_id: str, req: EvaluationRequest) -> Dict[str, Any]:
    """
    Saves multi-metric scorecards, recalculates global average, 
    and returns a response matching the EvaluationResponse schema.
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Target idea record could not be located.")
        
    # 1. Update/Create logic for the evaluation
    existing_eval = db.query(Evaluation).filter(
        Evaluation.idea_id == idea_id, 
        Evaluation.reviewer_id == reviewer_id
    ).first()
    
    if existing_eval:
        existing_eval.innovation_score = req.innovation_score
        existing_eval.feasibility_score = req.feasibility_score
        existing_eval.market_score = req.market_score
        existing_eval.scalability_score = req.scalability_score
        existing_eval.comments = req.comments
    else:
        new_eval = Evaluation(
            id=str(uuid.uuid4()),
            idea_id=idea_id,
            reviewer_id=reviewer_id,
            **req.model_dump()
        )
        db.add(new_eval)
        # Flush ensures the new evaluation is visible for the calculation below
        db.flush() 
    
    # 2. Correct Math: Sum of all metrics for all judges / (total judges * 4)
    all_evals = db.query(Evaluation).filter(Evaluation.idea_id == idea_id).all()
    if all_evals:
        total_sum = sum(e.innovation_score + e.feasibility_score + e.market_score + e.scalability_score for e in all_evals)
        global_avg = total_sum / (len(all_evals) * 4.0)
        idea.evaluation_score = round(global_avg, 2)
    
    # 3. Automatic Status Update (Admin-only logic)
    if idea.status == "Submitted":
        idea.status = "Under Review"
    
    idea.reviewer_notes = req.comments
    
    # 4. Commit and Refresh
    db.commit()
    db.refresh(idea)
    
    # 5. Return EXACTLY what EvaluationResponse schema requires
    return {
        "success": True,
        "idea_id": idea.id,
        "status": idea.status,
        "evaluation_score": idea.evaluation_score,
        "message": "Scorecard finalized successfully."
    }

