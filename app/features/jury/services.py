from sqlalchemy.orm import Session
from app.features.ideas.models import Idea
from app.features.jury.models import Evaluation
from app.features.jury.schemas import EvaluationRequest
from app.core.exceptions import ResourceNotFoundError

def process_jury_evaluation_card(db: Session, idea_id: str, reviewer_id: str, req: EvaluationRequest) -> dict:
    """Saves multi-metric jury scorecards and records the mathematical mean onto the parent idea."""
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise ResourceNotFoundError("Target idea record could not be located.")
        
    composite_average = (req.innovation_score + req.feasibility_score + req.market_score + req.scalability_score) / 4.0
    
    evaluation_record = Evaluation(
        idea_id=idea_id,
        reviewer_id=reviewer_id,
        innovation_score=req.innovation_score,
        feasibility_score=req.feasibility_score,
        market_score=req.market_score,
        scalability_score=req.scalability_score,
        comments=req.comments
    )
    db.add(evaluation_record)
    
    idea.evaluation_score = composite_average
    idea.reviewer_notes = req.comments
    idea.status = "Under Review" # Status auto-update on evaluation
    
    db.commit()
    return {"success": True, "average_score": composite_average}