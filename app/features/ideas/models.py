# # import uuid
# # from datetime import datetime, timezone
# # from sqlalchemy import (
# #     Column,
# #     String,
# #     Integer,
# #     Float,
# #     ForeignKey,
# #     DateTime,
# #     LargeBinary,
# #     Index
# # )
# # from sqlalchemy.orm import relationship
# # from app.database import Base


# # # =========================
# # # UUID GENERATOR
# # # =========================
# # def generate_uuid() -> str:
# #     return str(uuid.uuid4())


# # # =========================
# # # IDEA MODEL
# # # =========================
# # class Idea(Base):
# #     __tablename__ = "ideas"

# #     id = Column(String, primary_key=True, default=generate_uuid, index=True)

# #     # 🔗 USER RELATION
# #     user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

# #     submitter_order_number = Column(Integer, nullable=True)

# #     # =========================
# #     # CORE IDEA FIELDS
# #     # =========================
# #     title = Column(String, nullable=False, index=True)
# #     problem_statement = Column(String, nullable=False)
# #     proposed_solution = Column(String, nullable=False)

# #     category = Column(String, nullable=False, index=True)
# #     target_audience = Column(String, nullable=False)

# #     # =========================
# #     # BUSINESS CONTEXT
# #     # =========================
# #     market_opportunity = Column(String, nullable=True)
# #     competitive_advantage = Column(String, nullable=True)
# #     revenue_model = Column(String, nullable=True)
# #     current_stage = Column(String, nullable=False, index=True)
# #     business_impact = Column(String, nullable=True)
# #     scalability = Column(String, nullable=True)
# #     tech_requirements = Column(String, nullable=True)

# #     # =========================
# #     # EXTERNAL LINKS
# #     # =========================
# #     figma_link = Column(String, nullable=True)
# #     github_link = Column(String, nullable=True)
# #     drive_link = Column(String, nullable=True)
# #     demo_url = Column(String, nullable=True)

# #     # =========================
# #     # PIPELINE STATUS
# #     # =========================
# #     status = Column(String, default="Submitted", nullable=False, index=True)

# #     evaluation_score = Column(Float, nullable=True)
# #     reviewer_notes = Column(String, nullable=True)

# #     submitted_at = Column(
# #         DateTime,
# #         default=lambda: datetime.now(timezone.utc),
# #         index=True
# #     )

# #     # =========================
# #     # SAFETY CONTROL
# #     # =========================
# #     idempotency_key = Column(String, unique=True, index=True, nullable=True)

# #     # =========================
# #     # RELATIONSHIPS
# #     # =========================
# #     attachments = relationship(
# #         "Attachment",
# #         back_populates="idea",
# #         cascade="all, delete-orphan",
# #         lazy="selectin"
# #     )

# #     evaluations = relationship(
# #         "Evaluation",
# #         back_populates="idea",
# #         cascade="all, delete-orphan",
# #         lazy="selectin"
# #     )


# # # =========================
# # # ATTACHMENT MODEL
# # # =========================
# # class Attachment(Base):
# #     __tablename__ = "attachments"

# #     id = Column(String, primary_key=True, default=generate_uuid, index=True)

# #     idea_id = Column(
# #         String,
# #         ForeignKey("ideas.id", ondelete="CASCADE"),
# #         nullable=False,
# #         index=True
# #     )

# #     filename = Column(String, nullable=False)          # stored filename
# #     original_name = Column(String, nullable=False)     # user uploaded name

# #     file_size = Column(Integer, nullable=False)
# #     uploaded_at = Column(
# #         DateTime,
# #         default=lambda: datetime.now(timezone.utc),
# #         index=True
# #     )

# #     # 🔒 BINARY STORAGE
# #     file_data = Column(LargeBinary, nullable=False)

# #     # RELATIONSHIP
# #     idea = relationship("Idea", back_populates="attachments")


# # # =========================
# # # INDEX OPTIMIZATION (IMPORTANT FOR SCALE)
# # # =========================
# # Index("ix_ideas_user_status", Idea.user_id, Idea.status)
# # Index("ix_ideas_category_status", Idea.category, Idea.status)


# import uuid
# from datetime import datetime, timezone
# from sqlalchemy import (
#     Column,
#     String,
#     Integer,
#     Float,
#     ForeignKey,
#     DateTime,
#     LargeBinary,
#     Index,
#     Text
# )
# from sqlalchemy.dialects.mysql import LONGBLOB
# from sqlalchemy.orm import relationship
# from app.database import Base


# # =========================
# # UUID GENERATOR
# # =========================
# def generate_uuid() -> str:
#     return str(uuid.uuid4())


# # =========================
# # IDEA MODEL
# # =========================
# class Idea(Base):
#     __tablename__ = "ideas"

#     id = Column(String(36), primary_key=True, default=generate_uuid, index=True)

#     # 🔗 USER RELATION
#     user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

#     submitter_order_number = Column(Integer, nullable=True)

#     # =========================
#     # CORE IDEA FIELDS
#     # =========================
#     title = Column(String(255), nullable=False, index=True)
#     problem_statement = Column(Text, nullable=False)
#     proposed_solution = Column(Text, nullable=False)

#     category = Column(String(100), nullable=False, index=True)
#     target_audience = Column(String(500), nullable=False)

#     # =========================
#     # BUSINESS CONTEXT
#     # =========================
#     market_opportunity = Column(Text, nullable=True)
#     competitive_advantage = Column(Text, nullable=True)
#     revenue_model = Column(Text, nullable=True)
#     current_stage = Column(String(100), nullable=False, index=True)
#     business_impact = Column(Text, nullable=True)
#     scalability = Column(Text, nullable=True)
#     tech_requirements = Column(Text, nullable=True)

#     # =========================
#     # EXTERNAL LINKS
#     # =========================
#     figma_link = Column(String(500), nullable=True)
#     github_link = Column(String(500), nullable=True)
#     drive_link = Column(String(500), nullable=True)
#     demo_url = Column(String(500), nullable=True)

#     # =========================
#     # PIPELINE STATUS
#     # =========================
#     status = Column(String(100), default="Submitted", nullable=False, index=True)

#     evaluation_score = Column(Float, nullable=True)
#     reviewer_notes = Column(Text, nullable=True)

#     submitted_at = Column(
#         DateTime,
#         default=lambda: datetime.now(timezone.utc),
#         index=True
#     )

#     # =========================
#     # SAFETY CONTROL
#     # =========================
#     idempotency_key = Column(String(255), unique=True, index=True, nullable=True)

#     # =========================
#     # RELATIONSHIPS
#     # =========================
#     attachments = relationship(
#         "Attachment",
#         back_populates="idea",
#         cascade="all, delete-orphan",
#         lazy="selectin"
#     )

#     evaluations = relationship(
#         "Evaluation",
#         back_populates="idea",
#         cascade="all, delete-orphan",
#         lazy="selectin"
#     )


# # =========================
# # ATTACHMENT MODEL
# # =========================
# class Attachment(Base):
#     __tablename__ = "attachments"

#     id = Column(String(36), primary_key=True, default=generate_uuid, index=True)

#     idea_id = Column(
#         String(36),
#         ForeignKey("ideas.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True
#     )

#     filename = Column(String(255), nullable=False)          # stored filename
#     original_name = Column(String(255), nullable=False)     # user uploaded name

#     file_size = Column(Integer, nullable=False)
#     uploaded_at = Column(
#         DateTime,
#         default=lambda: datetime.now(timezone.utc),
#         index=True
#     )

#     # 🔒 BINARY STORAGE
#     file_data = Column(LargeBinary().with_variant(LONGBLOB, "mysql"), nullable=False)

#     # RELATIONSHIP
#     idea = relationship("Idea", back_populates="attachments")


# # =========================
# # INDEX OPTIMIZATION (IMPORTANT FOR SCALE)
# # =========================
# Index("ix_ideas_user_status", Idea.user_id, Idea.status)
# Index("ix_ideas_category_status", Idea.category, Idea.status)


import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    LargeBinary,
    Index,
    Text
)
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship
from app.database import Base
# =========================
# UUID GENERATOR
# =========================
def generate_uuid() -> str:
    return str(uuid.uuid4())
# =========================
# IDEA MODEL
# =========================
class Idea(Base):
    __tablename__ = "ideas"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    # 🔗 USER RELATION
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    submitter_order_number = Column(Integer, nullable=True)
    # =========================
    # CORE IDEA FIELDS
    # =========================
    title = Column(String(255), nullable=False, index=True)
    problem_statement = Column(Text, nullable=False)
    proposed_solution = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    target_audience = Column(String(500), nullable=False)
    # =========================
    # BUSINESS CONTEXT
    # =========================
    market_opportunity = Column(Text, nullable=True)
    competitive_advantage = Column(Text, nullable=True)
    revenue_model = Column(Text, nullable=True)
    current_stage = Column(String(100), nullable=False, index=True)
    business_impact = Column(Text, nullable=True)
    scalability = Column(Text, nullable=True)
    tech_requirements = Column(Text, nullable=True)
    # =========================
    # EXTERNAL LINKS
    # =========================
    figma_link = Column(String(500), nullable=True)
    github_link = Column(String(500), nullable=True)
    drive_link = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    # =========================
    # PIPELINE STATUS
    # =========================
    status = Column(String(100), default="Submitted", nullable=False, index=True)
    evaluation_score = Column(Float, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    submitted_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    # =========================
    # SAFETY CONTROL
    # =========================
    idempotency_key = Column(String(255), unique=True, index=True, nullable=True)
    # =========================
    # RELATIONSHIPS
    # =========================
    attachments = relationship(
        "Attachment",
        back_populates="idea",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    evaluations = relationship(
        "Evaluation",
        back_populates="idea",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
# =========================
# ATTACHMENT METADATA MODEL
# =========================
class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    idea_id = Column(
        String(36),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    filename = Column(String(255), nullable=False)          # stored filename
    original_name = Column(String(255), nullable=False)     # user uploaded name
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    # RELATIONSHIPS
    idea = relationship("Idea", back_populates="attachments")
    file_data_relation = relationship(
        "AttachmentData",
        uselist=False,
        back_populates="attachment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
# ==================================
# ATTACHMENT BINARY DATA STORAGE
# ==================================
class AttachmentData(Base):
    __tablename__ = "attachment_data"
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    attachment_id = Column(
        String(36),
        ForeignKey("attachments.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    # 🔒 BINARY STORAGE
    # Uses standard LargeBinary with a MySQL specific LONGBLOB variant for files up to 4GB
    file_data = Column(LargeBinary().with_variant(LONGBLOB, "mysql"), nullable=False)
    # RELATIONSHIP
    attachment = relationship("Attachment", back_populates="file_data_relation")
# =========================
# INDEX OPTIMIZATION (IMPORTANT FOR SCALE)
# =========================
Index("ix_ideas_user_status", Idea.user_id, Idea.status)
Index("ix_ideas_category_status", Idea.category, Idea.status)
