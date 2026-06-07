# # import uuid
# # from datetime import datetime, timezone
# # from sqlalchemy import Column, String, DateTime, Boolean
# # from app.database import Base

# # def generate_uuid() -> str:
# #     """Generates a secure string UUID for primary keys."""
# #     return str(uuid.uuid4())

# # class User(Base):
# #     __tablename__ = "users"
    
# #     id = Column(String, primary_key=True, default=generate_uuid, index=True)
# #     name = Column(String, nullable=False)
# #     email = Column(String, unique=True, index=True, nullable=False)
# #     phone = Column(String, nullable=False)
# #     organization = Column(String, nullable=True)
# #     internship_id = Column(String, nullable=True)
# #     department = Column(String, nullable=True)
# #     linkedin = Column(String, nullable=True)
# #     password_hash = Column(String, nullable=True)  
# #     role = Column(String, default="PARTICIPANT", nullable=False)  # "ADMIN", "JURY", "PARTICIPANT"
# #     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
# #     # NEW: OTP Verification Tracking Matrix Columns
# #     is_active = Column(Boolean, default=False, nullable=False)
# #     otp_code = Column(String, nullable=True)
# #     otp_expires_at = Column(DateTime, nullable=True)


# import uuid
# from datetime import datetime, timezone
# from sqlalchemy import Column, String, DateTime, Boolean
# from app.database import Base

# def generate_uuid() -> str:
#     """Generates a secure string UUID for primary keys."""
#     return str(uuid.uuid4())

# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(String, primary_key=True, default=generate_uuid, index=True)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     phone = Column(String, nullable=False)
#     organization = Column(String, nullable=True)
#     internship_id = Column(String, nullable=True)
#     department = Column(String, nullable=True)
#     linkedin = Column(String, nullable=True)
#     password_hash = Column(String, nullable=True)  
#     resume_filename = Column(String, nullable=True)
#     role = Column(String, default="PARTICIPANT", nullable=False)  # "ADMIN", "JURY", "PARTICIPANT"
#     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
#     # OTP Verification tracking columns
#     is_active = Column(Boolean, default=False, nullable=False)
#     otp_code = Column(String, nullable=True)
#     otp_expires_at = Column(DateTime, nullable=True)

#     # Google OAuth Profile validation column
#     is_profile_complete = Column(Boolean, default=True, nullable=False)

#     @property
#     def has_password(self) -> bool:
#         """Helper property to check if the user has registered a password."""
#         return self.password_hash is not None


import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, LargeBinary
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    """Generates a secure string UUID for primary keys."""
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=False)
    organization = Column(String(255), nullable=True)
    internship_id = Column(String(100), nullable=True)
    department = Column(String(255), nullable=True)
    linkedin = Column(String(500), nullable=True)
    password_hash = Column(String(255), nullable=True)  
    resume_filename = Column(String(255), nullable=True)
    role = Column(String(50), default="PARTICIPANT", nullable=False)  # "ADMIN", "JURY", "PARTICIPANT"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # OTP Verification tracking columns
    is_active = Column(Boolean, default=False, nullable=False)
    otp_code = Column(String(50), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

    # Google OAuth Profile validation column
    is_profile_complete = Column(Boolean, default=True, nullable=False)

    # Relationship to the heavy Resume binary model
    resume = relationship(
        "Resume",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @property
    def has_password(self) -> bool:
        """Helper property to check if the user has registered a password."""
        return self.password_hash is not None


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    # Uses standard LargeBinary with a MySQL specific LONGBLOB variant for files up to 4GB
    file_data = Column(LargeBinary().with_variant(LONGBLOB, "mysql"), nullable=False)

    # Relationship back to the User model
    user = relationship("User", back_populates="resume")