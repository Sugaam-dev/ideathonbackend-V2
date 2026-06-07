# import re
# from typing import Optional
# from pydantic import BaseModel, EmailStr, Field, field_validator

# class RegisterRequest(BaseModel):
#     name: str = Field(..., min_length=2, max_length=100)
#     email: EmailStr
#     # Validates phone as E.164 format or simple digit string (10-20 chars)
#     phone: str = Field(..., pattern=r"^\+?[0-9]{10,20}$") 
#     organization: Optional[str] = None
#     internship_id: Optional[str] = None
#     department: Optional[str] = None
#     linkedin: Optional[str] = None
#     password: str = Field(..., min_length=8, max_length=128)

#     @field_validator("password")
#     @classmethod
#     def validate_password_complexity(cls, v: str) -> str:
#         if not re.search(r"[A-Z]", v):
#             raise ValueError("Password must contain at least one uppercase letter")
#         if not re.search(r"[0-9]", v):
#             raise ValueError("Password must contain at least one digit")
#         if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
#             raise ValueError("Password must contain at least one special character")
#         return v

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class PasswordChangeRequest(BaseModel):
#     old_password: str
#     new_password: str = Field(..., min_length=8, max_length=128)

#     @field_validator("new_password")
#     @classmethod
#     def validate_password_complexity(cls, v: str) -> str:
#         if not re.search(r"[A-Z]", v):
#             raise ValueError("New password must contain at least one uppercase letter")
#         if not re.search(r"[0-9]", v):
#             raise ValueError("New password must contain at least one digit")
#         if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
#             raise ValueError("New password must contain at least one special character")
#         return v

# class UserResponse(BaseModel):
#     id: str
#     name: str
#     email: EmailStr
#     phone: Optional[str] = None
#     organization: Optional[str] = None
#     department: Optional[str] = None
#     role: str

#     class Config:
#         from_attributes = True



from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    organization: Optional[str] = None
    internship_id: Optional[str] = None
    department: Optional[str] = None
    linkedin: Optional[str] = None
    password: str = Field(..., min_length=8)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+?[0-9\- \(\)]{10,20}$", v):
            raise ValueError("Invalid phone number format. Please provide a valid 10-20 digit number.")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    old_password: Optional[str] = None
    new_password: str = Field(..., min_length=8)

class ProfileUpdateRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    organization: Optional[str] = Field(None, min_length=2, max_length=100)
    internship_id: Optional[str] = Field(None, min_length=2, max_length=50)
    department: Optional[str] = Field(None, min_length=2, max_length=50)
    linkedin: Optional[str] = Field(None, min_length=5, max_length=150)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+?[0-9\- \(\)]{10,20}$", v):
            raise ValueError("Invalid phone number format. Please provide a valid 10-20 digit number.")
        return v

    @field_validator("linkedin")
    @classmethod
    def validate_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(("http://", "https://", "www.linkedin.com")):
            raise ValueError("Invalid LinkedIn URL format. Must start with http://, https://, or www.linkedin.com")
        return v

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    organization: Optional[str] = None
    internship_id: Optional[str] = None
    department: Optional[str] = None
    linkedin: Optional[str] = None
    resume_filename: Optional[str] = None
    role: str
    is_profile_complete: bool
    has_password: bool

    class Config:
        from_attributes = True
        extra = "ignore"