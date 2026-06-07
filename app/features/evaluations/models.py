# import uuid
# from datetime import datetime, timezone
# from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from app.database import Base

# def generate_uuid() -> str:
#     """Generates a secure string UUID for metric row tracking."""
#     return str(uuid.uuid4())

# class Evaluation(Base):
#     __tablename__ = "evaluations"

#     id = Column(String, primary_key=True, default=generate_uuid, index=True)
#     idea_id = Column(String, ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
#     reviewer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
#     # Quantitative Analytical Grading Vectors
#     innovation_score = Column(Integer, nullable=False)
#     feasibility_score = Column(Integer, nullable=False)
#     market_score = Column(Integer, nullable=False)
#     scalability_score = Column(Integer, nullable=False)
    
#     comments = Column(String, nullable=True)
#     evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

#     # Relational Mappings
#     idea = relationship("Idea", back_populates="evaluations")


import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    """Generates a secure string UUID for metric row tracking."""
    return str(uuid.uuid4())

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    idea_id = Column(String(36), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Quantitative Analytical Grading Vectors
    innovation_score = Column(Integer, nullable=False)
    feasibility_score = Column(Integer, nullable=False)
    market_score = Column(Integer, nullable=False)
    scalability_score = Column(Integer, nullable=False)
    
    comments = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relational Mappings
    idea = relationship("Idea", back_populates="evaluations")