# # from fastapi import APIRouter, Depends, Response, status, BackgroundTasks, Cookie, HTTPException, Request
# # from sqlalchemy.orm import Session
# # from pydantic import BaseModel, EmailStr, Field
# # import secrets
# # from typing import Optional
# # from fastapi.responses import RedirectResponse

# # from app.database import get_db
# # from app.features.auth.schemas import RegisterRequest, LoginRequest, PasswordChangeRequest, UserResponse
# # from app.features.auth import services
# # from app.features.auth.dependencies import get_current_user
# # # Import the limiter from your main app instance
# # from app.main import limiter 

# # router = APIRouter(prefix="/api/auth", tags=["System Authentication Manager"])

# # # =====================================================================
# # # 📋 Pydantic Validation Schemas
# # # =====================================================================

# # class OtpVerificationRequest(BaseModel):
# #     email: EmailStr
# #     otp_code: str


# # class ForgotPasswordRequest(BaseModel):
# #     email: EmailStr


# # class ResetPasswordSubmit(BaseModel):
# #     email: EmailStr
# #     otp_code: str
# #     new_password: str = Field(..., min_length=8)


# # # =====================================================================
# # # 🔐 Core Authentication Endpoints
# # # =====================================================================

# # @router.post("/register", status_code=status.HTTP_202_ACCEPTED)
# # @limiter.limit("3/minute")  # Limit: 3 registrations per minute per IP
# # def register(req: RegisterRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
# #     services.create_user_account(db, req, background_tasks)
# #     return {"message": "Account initialized. Please check your inbox for your 6-digit activation code."}

# # @router.post("/verify-otp", response_model=UserResponse)
# # @limiter.limit("5/minute")
# # def verify_otp(req: OtpVerificationRequest, request: Request, response: Response, db: Session = Depends(get_db)):
# #     verified_user = services.verify_registration_otp_token(db, req.email, req.otp_code)
# #     services.set_session_cookie(response, verified_user)
# #     return verified_user


# # @router.post("/login", response_model=UserResponse)
# # @limiter.limit("5/minute")  # Limit: 5 login attempts per minute per IP
# # def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
# #     user = services.authenticate_user(db, req)
# #     services.set_session_cookie(response, user)
# #     return user


# # @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
# # def logout(response: Response, current_user=Depends(get_current_user)):
# #     response.delete_cookie(
# #         key="access_token",
# #         httponly=True,
# #         secure=False,
# #         samesite="lax",
# #         path="/"
# #     )
# #     return

# # @router.get("/me", response_model=UserResponse)
# # def get_my_profile(current_user=Depends(get_current_user)):
# #     return current_user


# # @router.put("/change-password", status_code=status.HTTP_200_OK)
# # def change_password(
# #     req: PasswordChangeRequest,
# #     current_user=Depends(get_current_user),
# #     db: Session = Depends(get_db)
# # ):
# #     services.change_user_password(db, current_user.id, req)
# #     return {"message": "Your profile password has been updated successfully."}


# # # =====================================================================
# # # 🔄 Password Recovery Flow
# # # =====================================================================

# # @router.post("/forgot-password", status_code=status.HTTP_200_OK)
# # @limiter.limit("3/minute")
# # def forgot_password(req: ForgotPasswordRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
# #     services.initiate_forgot_password_workflow(db, req.email, background_tasks)
# #     return {"message": "If the email is verified on our platform, an authorization code has been dispatched."}

# # @router.post("/reset-password", status_code=status.HTTP_200_OK)
# # def reset_password(req: ResetPasswordSubmit, db: Session = Depends(get_db)):
# #     services.execute_forgot_password_reset(db, req.email, req.otp_code, req.new_password)
# #     return {"message": "Your security password has been overwritten successfully. Please return to login."}


# # # =====================================================================
# # # 🌐 Google OAuth Operations
# # # =====================================================================

# # @router.get("/google/login")
# # def get_google_auth_link(response: Response):
# #     secure_state = secrets.token_urlsafe(32)
# #     auth_url = services.get_google_auth_url(secure_state)

# #     response.set_cookie(
# #     key="oauth_state",
# #     value=secure_state,
# #     httponly=True,
# #     secure=False,
# #     samesite="lax",
# #     max_age=300,
# #     path="/"
# # )

# #     return {"auth_url": auth_url}


# # # =====================================================================
# # # ✅ GOOGLE CALLBACK
# # # =====================================================================

# # @router.get("/google/callback")
# # async def process_google_auth_handshake(
# #     code: str,
# #     state: str,
# #     oauth_state: Optional[str] = Cookie(None),
# #     db: Session = Depends(get_db)
# # ):
# #     # Verify OAuth state (CSRF protection)
# #     if not oauth_state or state != oauth_state:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Security state signature token verification failed. Unauthorized handshake."
# #         )

# #     # Get/Create Google user
# #     user = await services.process_google_callback(code, db)

# #     # Create redirect response
# #     redirect_response = RedirectResponse(
# #         url="http://localhost:5173/dashboard",
# #         status_code=status.HTTP_303_SEE_OTHER
# #     )

# #     # Set access token cookie on redirect response
# #     services.set_session_cookie(redirect_response, user)

# #     # Remove oauth state cookie
# #     redirect_response.delete_cookie(
# #         key="oauth_state",
# #         path="/"
# #     )

# #     return redirect_response


# import os
# import secrets
# from typing import Optional
# from fastapi import APIRouter, Depends, Response, status, BackgroundTasks, Cookie, HTTPException, Request, Form, UploadFile, File
# from fastapi.responses import RedirectResponse, FileResponse
# from sqlalchemy.orm import Session
# from pydantic import BaseModel, EmailStr, Field

# from app.database import get_db
# from app.config import settings
# from app.features.auth.schemas import (
#     RegisterRequest, LoginRequest, PasswordChangeRequest, UserResponse, ProfileUpdateRequest
# )
# from app.features.auth import services
# from app.features.auth.dependencies import get_current_user
# from app.core.rate_limiter import limiter
# from app.features.auth.models import User

# router = APIRouter(prefix="/api/auth", tags=["System Authentication Manager"])

# # =====================================================================
# # 📋 Pydantic Validation Schemas
# # =====================================================================

# class OtpVerificationRequest(BaseModel):
#     email: EmailStr
#     otp_code: str


# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr


# class ResetPasswordSubmit(BaseModel):
#     email: EmailStr
#     otp_code: str
#     new_password: str = Field(..., min_length=8)


# # =====================================================================
# # 🔐 Core Authentication Endpoints
# # =====================================================================

# @router.post("/register", status_code=status.HTTP_202_ACCEPTED)
# @limiter.limit("5/minute")
# def register(
#     request: Request,
#     background_tasks: BackgroundTasks,
#     name: str = Form(...),
#     email: EmailStr = Form(...),
#     phone: str = Form(...),
#     password: str = Form(...),
#     organization: Optional[str] = Form(None),
#     department: Optional[str] = Form(None),
#     linkedin: Optional[str] = Form(None),
#     resume: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     req = RegisterRequest(
#         name=name,
#         email=email,
#         phone=phone,
#         organization=organization,
#         department=department,
#         linkedin=linkedin,
#         password=password
#     )
#     services.create_user_account(db, req, resume, background_tasks)
#     return {"message": "Account initialized. Please check your inbox for your 6-digit activation code."}


# @router.post("/verify-otp", response_model=UserResponse)
# @limiter.limit("10/minute")
# def verify_otp(req: OtpVerificationRequest, request: Request, response: Response, db: Session = Depends(get_db)):
#     verified_user = services.verify_registration_otp_token(db, req.email, req.otp_code)
#     services.set_session_cookie(response, verified_user)
#     return verified_user


# @router.post("/login", response_model=UserResponse)
# @limiter.limit("5/minute")
# def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
#     user = services.authenticate_user(db, req)
#     services.set_session_cookie(response, user)
#     return user


# @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
# def logout(response: Response, current_user=Depends(get_current_user)):
#     response.delete_cookie(
#         key="access_token",
#         httponly=True,
#         secure=False,
#         samesite="lax",
#         path="/"
#     )
#     response.delete_cookie(
#         key="refresh_token",
#         httponly=True,
#         secure=False,
#         samesite="lax",
#         path="/"
#     )
#     return

# @router.get("/me", response_model=UserResponse)
# def get_my_profile(current_user=Depends(get_current_user)):
#     return current_user


# @router.put("/change-password", status_code=status.HTTP_200_OK)
# def change_password(
#     req: PasswordChangeRequest,
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     services.change_user_password(db, current_user.id, req)
#     return {"message": "Your profile password has been updated successfully."}


# # =====================================================================
# # 👤 Profile Update Flow (For complete info manually after Google Auth)
# # =====================================================================

# # app/features/auth/router.py

# @router.put("/profile/update", response_model=UserResponse)
# def update_profile(
#     phone: str = Form(...),
#     organization: str = Form(...),
#     department: str = Form(...),
#     linkedin: Optional[str] = Form(None),
#     resume: Optional[UploadFile] = File(None),  # Parses the resume file
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Updates missing details and marks user profile completion status as True."""
#     req = ProfileUpdateRequest(
#         phone=phone,
#         organization=organization,
#         department=department,
#         linkedin=linkedin
#     )
#     updated_user = services.update_user_profile(db, current_user, req, resume)
#     return updated_user

# # =====================================================================
# # 📂 Resume Management Endpoints
# # =====================================================================

# @router.get("/resume/download")
# def download_resume(current_user: User = Depends(get_current_user)):
#     """Downloads/streams user's uploaded resume file from server disk."""
#     if not current_user.resume_filename:
#         raise HTTPException(status_code=404, detail="No resume uploaded for this profile.")
    
#     filepath = os.path.join(settings.UPLOAD_DIR, current_user.resume_filename)
#     if not os.path.exists(filepath):
#         raise HTTPException(status_code=404, detail="Physical resume file could not be found.")

#     clean_filename = current_user.resume_filename.split("_resume")[1] if "_resume" in current_user.resume_filename else current_user.resume_filename
#     return FileResponse(
#         filepath,
#         media_type="application/octet-stream",
#         filename=clean_filename
#     )


# @router.delete("/resume/delete", response_model=UserResponse)
# def delete_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     """Deletes user's resume attachment."""
#     return services.delete_user_resume(db, current_user)


# # =====================================================================
# # 🔄 Token Refresh Flow
# # =====================================================================

# @router.post("/refresh", response_model=UserResponse)
# def refresh(
#     response: Response,
#     refresh_token: Optional[str] = Cookie(None),
#     db: Session = Depends(get_db)
# ):
#     """Refreshes the access token using the refresh token cookie and issues rotated tokens."""
#     return services.refresh_tokens_workflow(db, refresh_token, response)


# # =====================================================================
# # 🔄 Password Recovery Flow
# # =====================================================================

# @router.post("/forgot-password", status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# def forgot_password(req: ForgotPasswordRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     services.initiate_forgot_password_workflow(db, req.email, background_tasks)
#     return {"message": "If the email is verified on our platform, an authorization code has been dispatched."}


# @router.post("/reset-password", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# def reset_password(req: ResetPasswordSubmit, request: Request, db: Session = Depends(get_db)):
#     services.execute_forgot_password_reset(db, req.email, req.otp_code, req.new_password)
#     return {"message": "Your security password has been overwritten successfully. Please return to login."}


# # =====================================================================
# # 🌐 Google OAuth Operations
# # =====================================================================

# @router.get("/google/login")
# def get_google_auth_link(response: Response):
#     secure_state = secrets.token_urlsafe(32)
#     auth_url = services.get_google_auth_url(secure_state)

#     response.set_cookie(
#         key="oauth_state",
#         value=secure_state,
#         httponly=True,
#         secure=False,
#         samesite="lax",
#         max_age=300,
#         path="/"
#     )

#     return {"auth_url": auth_url}


# # =====================================================================
# # ✅ GOOGLE CALLBACK
# # =====================================================================

# @router.get("/google/callback")
# async def process_google_auth_handshake(
#     code: str,
#     state: str,
#     oauth_state: Optional[str] = Cookie(None),
#     db: Session = Depends(get_db)
# ):
#     # Verify OAuth state (CSRF protection)
#     if not oauth_state or state != oauth_state:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Security state signature token verification failed. Unauthorized handshake."
#         )

#     # Get/Create Google user
#     user = await services.process_google_callback(code, db)

#     # Create redirect response to frontend dashboard URL from configurations
#     redirect_response = RedirectResponse(
#         url=settings.FRONTEND_DASHBOARD_URL,
#         status_code=status.HTTP_303_SEE_OTHER
#     )

#     # Set access token cookie on redirect response
#     services.set_session_cookie(redirect_response, user)

#     # Remove oauth state cookie
#     redirect_response.delete_cookie(
#         key="oauth_state",
#         path="/"
#     )

#     return redirect_response


import os
import secrets
import io
from typing import Optional
from fastapi import APIRouter, Depends, Response, status, BackgroundTasks, Cookie, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.config import settings
from app.features.auth.schemas import (
    RegisterRequest, LoginRequest, PasswordChangeRequest, UserResponse, ProfileUpdateRequest
)
from app.features.auth import services
from app.features.auth.dependencies import get_current_user
from app.core.rate_limiter import limiter
from app.features.auth.models import User, Resume

router = APIRouter(prefix="/api/auth", tags=["System Authentication Manager"])

# =====================================================================
# 📋 Pydantic Validation Schemas
# =====================================================================

class OtpVerificationRequest(BaseModel):
    email: EmailStr
    otp_code: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordSubmit(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str = Field(..., min_length=8)


# =====================================================================
# 🔐 Core Authentication Endpoints
# =====================================================================

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
def register(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    organization: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    linkedin: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    req = RegisterRequest(
        name=name,
        email=email,
        phone=phone,
        organization=organization,
        department=department,
        linkedin=linkedin,
        password=password
    )
    services.create_user_account(db, req, resume, background_tasks)
    return {"message": "Account initialized. Please check your inbox for your 6-digit activation code."}


@router.post("/verify-otp", response_model=UserResponse)
@limiter.limit("10/minute")
def verify_otp(req: OtpVerificationRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    verified_user = services.verify_registration_otp_token(db, req.email, req.otp_code)
    services.set_session_cookie(response, verified_user)
    return verified_user


@router.post("/login", response_model=UserResponse)
@limiter.limit("5/minute")
def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = services.authenticate_user(db, req)
    services.set_session_cookie(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, current_user=Depends(get_current_user)):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )
    return

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user=Depends(get_current_user)):
    return current_user


@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    req: PasswordChangeRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    services.change_user_password(db, current_user.id, req)
    return {"message": "Your profile password has been updated successfully."}


# =====================================================================
# 👤 Profile Update Flow (For complete info manually after Google Auth)
# =====================================================================

@router.put("/profile/update", response_model=UserResponse)
def update_profile(
    phone: str = Form(...),
    organization: str = Form(...),
    department: str = Form(...),
    linkedin: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates missing details and marks user profile completion status as True."""
    req = ProfileUpdateRequest(
        phone=phone,
        organization=organization,
        department=department,
        linkedin=linkedin
    )
    updated_user = services.update_user_profile(db, current_user, req, resume)
    return updated_user

# =====================================================================
# 📂 Resume Management Endpoints
# =====================================================================

@router.get("/resume/download")
def download_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Downloads/streams user's uploaded resume file directly from database."""
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded for this profile.")
    
    file_stream = io.BytesIO(resume.file_data)
    clean_filename = current_user.resume_filename or "resume.pdf"
    
    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'}
    )


@router.delete("/resume/delete", response_model=UserResponse)
def delete_resume(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletes user's resume attachment from database."""
    return services.delete_user_resume(db, current_user)


# =====================================================================
# 🔄 Token Refresh Flow
# =====================================================================

@router.post("/refresh", response_model=UserResponse)
def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Refreshes the access token using the refresh token cookie and issues rotated tokens."""
    return services.refresh_tokens_workflow(db, refresh_token, response)


# =====================================================================
# 🔄 Password Recovery Flow
# =====================================================================

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def forgot_password(req: ForgotPasswordRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    services.initiate_forgot_password_workflow(db, req.email, background_tasks)
    return {"message": "If the email is verified on our platform, an authorization code has been dispatched."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def reset_password(req: ResetPasswordSubmit, request: Request, db: Session = Depends(get_db)):
    services.execute_forgot_password_reset(db, req.email, req.otp_code, req.new_password)
    return {"message": "Your security password has been overwritten successfully. Please return to login."}


# =====================================================================
# 🌐 Google OAuth Operations
# =====================================================================

@router.get("/google/login")
def get_google_auth_link(response: Response):
    secure_state = secrets.token_urlsafe(32)
    auth_url = services.get_google_auth_url(secure_state)

    response.set_cookie(
        key="oauth_state",
        value=secure_state,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=300,
        path="/"
    )

    return {"auth_url": auth_url}


# =====================================================================
# ✅ GOOGLE CALLBACK
# =====================================================================

@router.get("/google/callback")
async def process_google_auth_handshake(
    code: str,
    state: str,
    oauth_state: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # Verify OAuth state (CSRF protection)
    if not oauth_state or state != oauth_state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security state signature token verification failed. Unauthorized handshake."
        )

    # Get/Create Google user
    user = await services.process_google_callback(code, db)

    # Create redirect response to frontend dashboard URL from configurations
    redirect_response = RedirectResponse(
        url=settings.FRONTEND_DASHBOARD_URL,
        status_code=status.HTTP_303_SEE_OTHER
    )

    # Set access token cookie on redirect response
    services.set_session_cookie(redirect_response, user)

    # Remove oauth state cookie
    redirect_response.delete_cookie(
        key="oauth_state",
        path="/"
    )

    return redirect_response