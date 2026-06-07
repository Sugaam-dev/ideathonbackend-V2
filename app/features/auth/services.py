# import secrets
# import httpx
# import jwt
# import os
# import uuid
# from typing import Optional

# from datetime import datetime, timedelta, timezone
# from sqlalchemy.orm import Session
# from fastapi import Response, BackgroundTasks, UploadFile 
# from app.config import settings
# from app.core import security, email
# from app.core.exceptions import (
#     DuplicateResourceError, AuthError, ResourceNotFoundError, 
#     BadRequestError, PermissionDeniedError, UserNotRegisteredError,
#     IncorrectPasswordError
# )
# from app.features.auth.models import User, Resume
# from app.features.auth.schemas import (
#     RegisterRequest, LoginRequest, PasswordChangeRequest, ProfileUpdateRequest
# )

# # =====================================================================
# # 🛠️ Helper Utilities & Email Dispatches
# # =====================================================================

# def generate_secure_otp() -> str:
#     """Generates a highly random 6-digit numerical string token."""
#     return f"{secrets.randbelow(900000) + 100000}"


# def dispatch_registration_otp_email(background_tasks: BackgroundTasks, to_email: str, user_name: str, otp: str) -> None:
#     """Compiles clean transactional HTML structure containing the validation code."""
#     subject = f"Verification Token: {otp} - PMRG Ideathon Portal"
#     html_content = f"""
#     <html>
#         <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
#             <h2 style="color: #2b6cb0;">Verify Your Account</h2>
#             <p>Hello {user_name},</p>
#             <p>Thank you for initiating your application process. Please utilize the 6-digit One-Time Password below to activate your account registration status:</p>
#             <div style="margin: 20px 0; padding: 15px; background: #f7fafc; border: 1px dashed #cbd5e0; font-size: 1.8em; font-weight: bold; text-align: center; color: #2b6cb0; letter-spacing: 5px;">
#                 {otp}
#             </div>
#             <p style="color: #e53e3e;"><strong>This code is strictly active for 5 minutes.</strong></p>
#             <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
#             <p style="font-size: 0.8em; color: #718096;">If you did not initiate this registration request, please disregard this automated notification.</p>
#         </body>
#     </html>
#     """
#     background_tasks.add_task(email.send_transactional_email, to_email, subject, html_content)


# def dispatch_recovery_otp_email(background_tasks: BackgroundTasks, to_email: str, user_name: str, otp: str) -> None:
#     """Compiles clean transactional HTML structure containing the password recovery verification code."""
#     subject = f"Password Recovery Code: {otp} - PMRG Ideathon Portal"
#     html_content = f"""
#     <html>
#         <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
#             <h2 style="color: #c53030;">Password Reset Request</h2>
#             <p>Hello {user_name},</p>
#             <p>We received a request to reset the password associated with your account. Use the authorization code below to submit your new password credentials:</p>
#             <div style="margin: 20px 0; padding: 15px; background: #fff5f5; border: 1px dashed #feb2b2; font-size: 1.8em; font-weight: bold; text-align: center; color: #c53030; letter-spacing: 5px;">
#                 {otp}
#             </div>
#             <p style="color: #e53e3e;"><strong>This recovery code will expire in 5 minutes.</strong></p>
#             <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
#             <p style="font-size: 0.8em; color: #718096;">If you did not make this request, your password remains completely secure. You can safely ignore this alert.</p>
#         </body>
#     </html>
#     """
#     background_tasks.add_task(email.send_transactional_email, to_email, subject, html_content)


# # =====================================================================
# # 🔐 Core Authentication Workflows
# # =====================================================================

# def create_user_account(db: Session, req: RegisterRequest, resume: Optional[UploadFile], background_tasks: BackgroundTasks) -> User:
#     existing_user = db.query(User).filter(User.email == req.email).first()
#     if existing_user:
#         if existing_user.is_active:
#             raise DuplicateResourceError("This email address is already verified and registered.")
#         db.delete(existing_user)
#         db.commit()
#     generated_otp = generate_secure_otp()
#     expiry_horizon = datetime.now(timezone.utc) + timedelta(minutes=5)
#     new_user = User(
#         name=req.name,
#         email=req.email,
#         phone=req.phone,
#         organization=req.organization,
#         internship_id=req.internship_id,
#         department=req.department,
#         linkedin=req.linkedin,
#         password_hash=security.hash_password(req.password),
#         role="PARTICIPANT",
#         is_active=False,
#         otp_code=generated_otp,
#         otp_expires_at=expiry_horizon,
#         is_profile_complete=True
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
    
#     # Save resume file directly in database if uploaded
#     if resume and resume.filename:
#         file_bytes = resume.file.read()
#         new_resume = Resume(
#             id=str(uuid.uuid4()),
#             user_id=new_user.id,
#             file_data=file_bytes
#         )
#         db.add(new_resume)
#         new_user.resume_filename = resume.filename
#         db.commit()
        
#     dispatch_registration_otp_email(background_tasks, req.email, req.name, generated_otp)
#     return new_user

# def verify_registration_otp_token(db: Session, email_str: str, entered_otp: str) -> User:
#     """Validates token accuracy and timestamps before changing active status parameters."""
#     user = db.query(User).filter(User.email == email_str).first()
#     if not user:
#         raise ResourceNotFoundError("No pending transaction configuration profile associated with this email.")
        
#     if user.is_active:
#         raise BadRequestError("This profile structure is already verified and completely operational.")
        
#     if user.otp_code != entered_otp:
#         raise AuthError("The code entered is invalid. Please double-check your credentials and try again.")
        
#     if datetime.now(timezone.utc) > user.otp_expires_at.replace(tzinfo=timezone.utc):
#         raise AuthError("Your verification token window has expired. Please launch a fresh registration sequence.")
        
#     user.is_active = True
#     user.otp_code = None
#     user.otp_expires_at = None
#     db.commit()
#     db.refresh(user)
#     return user


# def authenticate_user(db: Session, req: LoginRequest) -> User:
#     """Validates login credentials, ensuring verified state triggers match."""
#     try:
#         user = db.query(User).filter(User.email == req.email).first()
#         if not user:
#             raise UserNotRegisteredError("This email address is not registered on our platform.")
            
#         if not user.is_active:
#             raise PermissionDeniedError("Account not verified. Please finalize your pending activation process.")
            
#         if not user.password_hash or not security.verify_password(req.password, user.password_hash):
#             raise IncorrectPasswordError("The password you entered is incorrect. Please try again.")
            
#         return user
#     except (UserNotRegisteredError, PermissionDeniedError, IncorrectPasswordError):
#         # Explicitly re-raise custom operational errors
#         raise
#     except Exception as e:
#         # Catch other potential database or system failures
#         raise BadRequestError(f"Authentication process failed: {str(e)}")


# def set_session_cookie(response: Response, user: User) -> None:
#     # 1. Generate access token
#     access_token = security.create_access_token(
#         data={"sub": str(user.id), "role": user.role}
#     )
#     # 2. Generate refresh token
#     refresh_token = security.create_refresh_token(
#         data={"sub": str(user.id)}
#     )
    
#     # 3. Expirations in seconds
#     access_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
#     refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

#     # 4. SameSite policy based on HTTPS configuration
#     samesite_policy = "none" if settings.COOKIE_SECURE else "lax"

#     # 5. Set access token cookie
#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         httponly=True,
#         secure=settings.COOKIE_SECURE,
#         samesite=samesite_policy,
#         max_age=access_max_age,
#         path="/"
#     )

#     # 6. Set refresh token cookie
#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,
#         secure=settings.COOKIE_SECURE,
#         samesite=samesite_policy,
#         max_age=refresh_max_age,
#         path="/"
#     )

# # =====================================================================
# # 🔄 Password Operations & Recovery Management
# # =====================================================================

# def change_user_password(db: Session, user_id: str, req: PasswordChangeRequest) -> None:
#     """Verifies old credentials and overwrites data layers with a fresh password hash."""
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user or not user.password_hash:
#         raise AuthError("User profile identification reference missing.")

#     if not security.verify_password(req.old_password, user.password_hash):
#         raise AuthError("Your current password calculation does not match our records.")

#     user.password_hash = security.hash_password(req.new_password)
#     db.commit()


# def initiate_forgot_password_workflow(db: Session, email_str: str, background_tasks: BackgroundTasks) -> None:
#     """Generates a transient 5-minute recovery token and emails it to verified users."""
#     user = db.query(User).filter(User.email == email_str).first()
    
#     if user and user.is_active:
#         generated_otp = generate_secure_otp()
#         expiry_horizon = datetime.now(timezone.utc) + timedelta(minutes=5)
        
#         user.otp_code = generated_otp
#         user.otp_expires_at = expiry_horizon
#         db.commit()
        
#         dispatch_recovery_otp_email(background_tasks, user.email, user.name, generated_otp)


# def execute_forgot_password_reset(db: Session, email_str: str, entered_otp: str, new_password_str: str) -> None:
#     """Validates the recovery token parameters and permanently updates the user password."""
#     user = db.query(User).filter(User.email == email_str).first()
#     if not user or not user.is_active:
#         raise ResourceNotFoundError("Account parameters missing or inactive.")
        
#     if not user.otp_code or user.otp_code != entered_otp:
#         raise AuthError("The recovery validation token provided is invalid.")
        
#     if datetime.now(timezone.utc) > user.otp_expires_at.replace(tzinfo=timezone.utc):
#         raise AuthError("Your validation window expired. Please initiate a fresh password recovery email.")
        
#     user.password_hash = security.hash_password(new_password_str)
#     user.otp_code = None
#     user.otp_expires_at = None
#     db.commit()

# # =====================================================================
# # 👤 Profile Completeness Service updates
# # =====================================================================

# def update_user_profile(db: Session, user: User, req: ProfileUpdateRequest, resume: Optional[UploadFile] = None) -> User:
#     user.phone = req.phone
#     user.organization = req.organization
#     user.internship_id = req.internship_id
#     user.department = req.department
#     user.linkedin = req.linkedin
#     user.is_profile_complete = True
    
#     # Save/Update resume file in database if uploaded
#     if resume and resume.filename:
#         file_bytes = resume.file.read()
#         if user.resume:
#             user.resume.file_data = file_bytes
#             user.resume_filename = resume.filename
#         else:
#             new_resume = Resume(
#                 id=str(uuid.uuid4()),
#                 user_id=user.id,
#                 file_data=file_bytes
#             )
#             db.add(new_resume)
#             user.resume_filename = resume.filename
            
#     db.commit()
#     db.refresh(user)
#     return user

# def delete_user_resume(db: Session, user: User) -> User:
#     """Removes a user's resume attachment and cleans up database records."""
#     if user.resume:
#         db.delete(user.resume)
#         user.resume_filename = None
#         db.commit()
#         db.refresh(user)
#     return user

# # =====================================================================
# # 🔄 Refresh Tokens Workflow
# # =====================================================================

# def refresh_tokens_workflow(db: Session, refresh_token: str, response: Response) -> User:
#     """
#     Decodes the refresh token, validates it, fetches the user,
#     and rotates both the access and refresh tokens.
#     """
#     if not refresh_token:
#         raise AuthError("Refresh token missing from request.")

#     try:
#         payload = jwt.decode(
#             refresh_token,
#             settings.SECRET_KEY,
#             algorithms=[settings.ALGORITHM]
#         )

#         user_id = payload.get("sub")
#         token_type = payload.get("token_type")

#         if not user_id:
#             raise AuthError("Invalid refresh token payload.")
            
#         if token_type != "refresh":
#             raise AuthError("Invalid token type. Refresh token expected.")

#     except jwt.ExpiredSignatureError:
#         raise AuthError("Refresh token has expired. Please log in again.")
#     except jwt.InvalidTokenError:
#         raise AuthError("Invalid refresh token.")

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise AuthError("User associated with this refresh token does not exist.")

#     if not user.is_active:
#         raise PermissionDeniedError("Account not verified. Please finalize your pending activation process.")

#     # Rotate tokens and set new cookies
#     set_session_cookie(response, user)
#     return user

# # =====================================================================
# # 🌐 Google OAuth Operations Framework Namespace
# # =====================================================================

# def get_google_auth_url(state: str) -> str:
#     """Builds authorization consent landing redirect paths bound to system secrets."""
#     base_url = "https://accounts.google.com/o/oauth2/v2/auth"
#     params = {
#         "client_id": settings.GOOGLE_CLIENT_ID,
#         "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#         "response_type": "code",
#         "scope": "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
#         "state": state,
#         "access_type": "offline",
#         "prompt": "select_account"
#     }
#     return f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())


# def process_google_callback(code: str, db: Session) -> User:
#     """Exchanges code metadata directly, bypassing verification flows because Google acts as the verifier."""
#     token_url = "https://oauth2.googleapis.com/token"
#     payload = {
#         "code": code,
#         "client_id": settings.GOOGLE_CLIENT_ID,
#         "client_secret": settings.GOOGLE_CLIENT_SECRET,
#         "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#         "grant_type": "authorization_code"
#     }
    
#     # Using synchronous httpx.Client to prevent event loop blocking on DB queries
#     with httpx.Client() as client:
#         token_response = client.post(token_url, data=payload)
#         if token_response.status_code != 200:
#             raise AuthError("Failed token code validation exchange step with Google.")
            
#         tokens = token_response.json()
#         access_token = tokens.get("access_token")
        
#         profile_response = client.get(
#             "https://www.googleapis.com/oauth2/v2/userinfo", 
#             headers={"Authorization": f"Bearer {access_token}"}
#         )
#         if profile_response.status_code != 200:
#             raise AuthError("Failed profile attributes retrieval operations from Google.")
            
#         profile_data = profile_response.json()
#         email_addr = profile_data.get("email")
#         name_str = profile_data.get("name")
        
#         user = db.query(User).filter(User.email == email_addr).first()
#         if not user:
#             # First-time Google login: create account with complete=False
#             user = User(
#                 name=name_str,
#                 email=email_addr,
#                 phone="Google OAuth Verified",
#                 role="PARTICIPANT",
#                 is_active=True,
#                 is_profile_complete=False  # Must complete profile manually
#             )
#             db.add(user)
#             db.commit()
#             db.refresh(user)
            
#         if not user.is_active:
#             user.is_active = True
#             db.commit()
            
#         return user

import secrets
import httpx
import jwt
import os
import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import Response, BackgroundTasks, UploadFile 
from app.config import settings
from app.core import security, email
from app.core.exceptions import (
    DuplicateResourceError, AuthError, ResourceNotFoundError, 
    BadRequestError, PermissionDeniedError, UserNotRegisteredError,
    IncorrectPasswordError
)
from app.features.auth.models import User, Resume
from app.features.auth.schemas import (
    RegisterRequest, LoginRequest, PasswordChangeRequest, ProfileUpdateRequest
)
# =====================================================================
# 🛠️ Helper Utilities & Email Dispatches
# =====================================================================
def generate_secure_otp() -> str:
    """Generates a highly random 6-digit numerical string token."""
    return f"{secrets.randbelow(900000) + 100000}"
def dispatch_registration_otp_email(background_tasks: BackgroundTasks, to_email: str, user_name: str, otp: str) -> None:
    """Compiles clean transactional HTML structure containing the validation code."""
    subject = f"Verification Token: {otp} - PMRG Ideathon Portal"
    html_content = f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="background-color: #f3f4f6; padding: 32px 16px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Verify Your Email</h1>
                        <p style="color: #e0e7ff; margin: 8px 0 0 0; font-size: 14px;">PMRG Ideathon Portal</p>
                    </div>
                    <!-- Content -->
                    <div style="padding: 32px 24px; color: #1f2937; line-height: 1.6;">
                        <p style="margin-top: 0; font-size: 16px;">Hello <strong>{user_name}</strong>,</p>
                        <p style="font-size: 15px; color: #4b5563;">Thank you for registering on our platform! To activate your account and verify your email address, please use the 6-digit One-Time Password (OTP) below:</p>
                        
                        <!-- OTP Box -->
                        <div style="margin: 32px 0; padding: 20px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; text-align: center;">
                            <span style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #4f46e5; font-family: 'Courier New', Courier, monospace;">{otp}</span>
                        </div>
                        
                        <p style="font-size: 14px; color: #dc2626; font-weight: 600; margin: 0 0 16px 0;">⚠️ This code is strictly active for 5 minutes.</p>
                        <p style="font-size: 14px; color: #6b7280; margin: 0;">If you did not initiate this request, you can safely ignore this email.</p>
                    </div>
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                        <p style="margin: 0 0 6px 0;">&copy; 2026 PMRG Solutions. All rights reserved.</p>
                        <p style="margin: 0;">This is an automated security system notification.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    background_tasks.add_task(email.send_transactional_email, to_email, subject, html_content)
def dispatch_recovery_otp_email(background_tasks: BackgroundTasks, to_email: str, user_name: str, otp: str) -> None:
    """Compiles clean transactional HTML structure containing the password recovery verification code."""
    subject = f"Password Recovery Code: {otp} - PMRG Ideathon Portal"
    html_content = f"""
    <html>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="background-color: #f3f4f6; padding: 32px 16px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #e5e7eb;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #ef4444 0%, #f97316 100%); padding: 32px 24px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Reset Your Password</h1>
                        <p style="color: #ffe4e6; margin: 8px 0 0 0; font-size: 14px;">PMRG Ideathon Portal</p>
                    </div>
                    <!-- Content -->
                    <div style="padding: 32px 24px; color: #1f2937; line-height: 1.6;">
                        <p style="margin-top: 0; font-size: 16px;">Hello <strong>{user_name}</strong>,</p>
                        <p style="font-size: 15px; color: #4b5563;">We received a request to reset the password for your account. Please use the authorization code below to submit your new password credentials:</p>
                        
                        <!-- OTP Box -->
                        <div style="margin: 32px 0; padding: 20px; background-color: #fff5f5; border: 1px solid #fee2e2; border-radius: 8px; text-align: center;">
                            <span style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #ef4444; font-family: 'Courier New', Courier, monospace;">{otp}</span>
                        </div>
                        
                        <p style="font-size: 14px; color: #dc2626; font-weight: 600; margin: 0 0 16px 0;">⚠️ This recovery code will expire in 5 minutes.</p>
                        <p style="font-size: 14px; color: #6b7280; margin: 0;">If you did not request a password reset, your account remains completely secure. You can safely ignore this alert.</p>
                    </div>
                    <!-- Footer -->
                    <div style="background-color: #f9fafb; padding: 24px; text-align: center; font-size: 12px; color: #9ca3af; border-top: 1px solid #f3f4f6;">
                        <p style="margin: 0 0 6px 0;">&copy; 2026 PMRG Solutions. All rights reserved.</p>
                        <p style="margin: 0;">This is an automated security system notification.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    background_tasks.add_task(email.send_transactional_email, to_email, subject, html_content)
# =====================================================================
# 🔐 Core Authentication Workflows
# =====================================================================
def create_user_account(db: Session, req: RegisterRequest, resume: Optional[UploadFile], background_tasks: BackgroundTasks) -> User:
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        if existing_user.is_active:
            raise DuplicateResourceError("This email address is already verified and registered.")
        db.delete(existing_user)
        db.commit()
    generated_otp = generate_secure_otp()
    expiry_horizon = datetime.now(timezone.utc) + timedelta(minutes=5)
    new_user = User(
        name=req.name,
        email=req.email,
        phone=req.phone,
        organization=req.organization,
        internship_id=req.internship_id,
        department=req.department,
        linkedin=req.linkedin,
        password_hash=security.hash_password(req.password),
        role="PARTICIPANT",
        is_active=False,
        otp_code=generated_otp,
        otp_expires_at=expiry_horizon,
        is_profile_complete=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Save resume file directly in database if uploaded
    if resume and resume.filename:
        file_bytes = resume.file.read()
        new_resume = Resume(
            id=str(uuid.uuid4()),
            user_id=new_user.id,
            file_data=file_bytes
        )
        db.add(new_resume)
        new_user.resume_filename = resume.filename
        db.commit()
        
    dispatch_registration_otp_email(background_tasks, req.email, req.name, generated_otp)
    return new_user
def verify_registration_otp_token(db: Session, email_str: str, entered_otp: str) -> User:
    """Validates token accuracy and timestamps before changing active status parameters."""
    user = db.query(User).filter(User.email == email_str).first()
    if not user:
        raise ResourceNotFoundError("No pending transaction configuration profile associated with this email.")
        
    if user.is_active:
        raise BadRequestError("This profile structure is already verified and completely operational.")
        
    if user.otp_code != entered_otp:
        raise AuthError("The code entered is invalid. Please double-check your credentials and try again.")
        
    if datetime.now(timezone.utc) > user.otp_expires_at.replace(tzinfo=timezone.utc):
        raise AuthError("Your verification token window has expired. Please launch a fresh registration sequence.")
        
    user.is_active = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)
    return user
def authenticate_user(db: Session, req: LoginRequest) -> User:
    """Validates login credentials, ensuring verified state triggers match."""
    try:
        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            raise UserNotRegisteredError("This email address is not registered on our platform.")
            
        if not user.is_active:
            raise PermissionDeniedError("Account not verified. Please finalize your pending activation process.")
            
        if not user.password_hash or not security.verify_password(req.password, user.password_hash):
            raise IncorrectPasswordError("The password you entered is incorrect. Please try again.")
            
        return user
    except (UserNotRegisteredError, PermissionDeniedError, IncorrectPasswordError):
        # Explicitly re-raise custom operational errors
        raise
    except Exception as e:
        # Catch other potential database or system failures
        raise BadRequestError(f"Authentication process failed: {str(e)}")
def set_session_cookie(response: Response, user: User) -> None:
    # 1. Generate access token
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    # 2. Generate refresh token
    refresh_token = security.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # 3. Expirations in seconds
    access_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    samesite_policy = "none" if settings.COOKIE_SECURE else "lax"
    # 4. Set access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=samesite_policy,
        max_age=access_max_age,
        path="/"
    )
    # 5. Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=samesite_policy,
        max_age=refresh_max_age,
        path="/"
    )
# =====================================================================
# 🔄 Password Operations & Recovery Management
# =====================================================================
def change_user_password(db: Session, user_id: str, req: PasswordChangeRequest) -> None:
    """Verifies old credentials and overwrites data layers with a fresh password hash."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.password_hash:
        raise AuthError("User profile identification reference missing.")
    if not security.verify_password(req.old_password, user.password_hash):
        raise AuthError("Your current password calculation does not match our records.")
    user.password_hash = security.hash_password(req.new_password)
    db.commit()
def initiate_forgot_password_workflow(db: Session, email_str: str, background_tasks: BackgroundTasks) -> None:
    """Generates a transient 5-minute recovery token and emails it to verified users."""
    user = db.query(User).filter(User.email == email_str).first()
    
    if user and user.is_active:
        generated_otp = generate_secure_otp()
        expiry_horizon = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        user.otp_code = generated_otp
        user.otp_expires_at = expiry_horizon
        db.commit()
        
        dispatch_recovery_otp_email(background_tasks, user.email, user.name, generated_otp)
def execute_forgot_password_reset(db: Session, email_str: str, entered_otp: str, new_password_str: str) -> None:
    """Validates the recovery token parameters and permanently updates the user password."""
    user = db.query(User).filter(User.email == email_str).first()
    if not user or not user.is_active:
        raise ResourceNotFoundError("Account parameters missing or inactive.")
        
    if not user.otp_code or user.otp_code != entered_otp:
        raise AuthError("The recovery validation token provided is invalid.")
        
    if datetime.now(timezone.utc) > user.otp_expires_at.replace(tzinfo=timezone.utc):
        raise AuthError("Your validation window expired. Please initiate a fresh password recovery email.")
        
    user.password_hash = security.hash_password(new_password_str)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
# =====================================================================
# 👤 Profile Completeness Service updates
# =====================================================================
def update_user_profile(db: Session, user: User, req: ProfileUpdateRequest, resume: Optional[UploadFile] = None) -> User:
    user.phone = req.phone
    user.organization = req.organization
    user.internship_id = req.internship_id
    user.department = req.department
    user.linkedin = req.linkedin
    user.is_profile_complete = True
    
    # Save/Update resume file in database if uploaded
    if resume and resume.filename:
        file_bytes = resume.file.read()
        if user.resume:
            user.resume.file_data = file_bytes
            user.resume_filename = resume.filename
        else:
            new_resume = Resume(
                id=str(uuid.uuid4()),
                user_id=user.id,
                file_data=file_bytes
            )
            db.add(new_resume)
            user.resume_filename = resume.filename
            
    db.commit()
    db.refresh(user)
    return user
def delete_user_resume(db: Session, user: User) -> User:
    """Removes a user's resume attachment and cleans up database records."""
    if user.resume:
        db.delete(user.resume)
        user.resume_filename = None
        db.commit()
        db.refresh(user)
    return user
# =====================================================================
# 🔄 Refresh Tokens Workflow
# =====================================================================
def refresh_tokens_workflow(db: Session, refresh_token: str, response: Response) -> User:
    """
    Decodes the refresh token, validates it, fetches the user,
    and rotates both the access and refresh tokens.
    """
    if not refresh_token:
        raise AuthError("Refresh token missing from request.")
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        token_type = payload.get("token_type")
        if not user_id:
            raise AuthError("Invalid refresh token payload.")
            
        if token_type != "refresh":
            raise AuthError("Invalid token type. Refresh token expected.")
    except jwt.ExpiredSignatureError:
        raise AuthError("Refresh token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid refresh token.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthError("User associated with this refresh token does not exist.")
    if not user.is_active:
        raise PermissionDeniedError("Account not verified. Please finalize your pending activation process.")
    # Rotate tokens and set new cookies
    set_session_cookie(response, user)
    return user
# =====================================================================
# 🌐 Google OAuth Operations Framework Namespace
# =====================================================================
def get_google_auth_url(state: str) -> str:
    """Builds authorization consent landing redirect paths bound to system secrets."""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    return f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
def process_google_callback(code: str, db: Session) -> User:
    """Exchanges code metadata directly, bypassing verification flows because Google acts as the verifier."""
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    with httpx.Client() as client:
        token_response = client.post(token_url, data=payload)
        if token_response.status_code != 200:
            raise AuthError("Failed token code validation exchange step with Google.")
            
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        profile_response = client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if profile_response.status_code != 200:
            raise AuthError("Failed profile attributes retrieval operations from Google.")
            
        profile_data = profile_response.json()
        email_addr = profile_data.get("email")
        name_str = profile_data.get("name")
        
        user = db.query(User).filter(User.email == email_addr).first()
        if not user:
            # First-time Google login: create account with complete=False
            user = User(
                name=name_str,
                email=email_addr,
                phone="Google OAuth Verified",
                role="PARTICIPANT",
                is_active=True,
                is_profile_complete=False  # Must complete profile manually
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        if not user.is_active:
            user.is_active = True
            db.commit()
            
        return user
