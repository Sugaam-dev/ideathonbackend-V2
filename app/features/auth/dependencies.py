# from typing import List
# import jwt
# from fastapi import Request, Depends
# from sqlalchemy.orm import Session

# from app.config import settings
# from app.database import get_db
# from app.core.exceptions import AuthError, PermissionDeniedError
# from app.features.auth.models import User


# # =====================================================================
# # 🔐 AUTH: GET CURRENT USER
# # =====================================================================

# def get_current_user(
#     request: Request,
#     db: Session = Depends(get_db)
# ) -> User:
#     """
#     Extracts JWT from HttpOnly cookie, validates it,
#     and fetches the corresponding user from DB.
#     """

#     # 1. Get cookie
#     token = request.cookies.get("access_token")

#     if not token:
#         raise AuthError("Authentication required. Session cookie missing.")

#     try:
#         # 2. Decode JWT directly (NO "Bearer " prefix anymore)
#         payload = jwt.decode(
#             token,
#             settings.SECRET_KEY,
#             algorithms=[settings.ALGORITHM]
#         )

#         user_id = payload.get("sub")

#         if not user_id:
#             raise AuthError("Invalid session token payload.")

#         # 3. FIX: convert to int if your DB uses integer IDs
#         try:
#             user_id = int(user_id)
#         except ValueError:
#             pass  # keep as string if UUID system

#     except jwt.ExpiredSignatureError:
#         raise AuthError("Session expired. Please login again.")

#     except jwt.InvalidTokenError:
#         raise AuthError("Invalid authentication token.")

#     # 4. Fetch user
#     user = db.query(User).filter(User.id == user_id).first()

#     if not user:
#         raise AuthError("User associated with this session does not exist.")

#     return user


# # =====================================================================
# # 🔐 ROLE-BASED ACCESS CONTROL
# # =====================================================================

# class RoleChecker:
#     """
#     Enforces role-based access control for protected routes.
#     """

#     def __init__(self, allowed_roles: List[str]):
#         self.allowed_roles = allowed_roles

#     def __call__(self, current_user: User = Depends(get_current_user)) -> User:
#         if current_user.role not in self.allowed_roles:
#             raise PermissionDeniedError(
#                 "Access denied. Your role privileges are insufficient."
#             )
#         return current_user


# # Global role guards
# require_admin = RoleChecker(["ADMIN"])
# require_jury_or_admin = RoleChecker(["ADMIN", "JURY"])



from typing import List
import jwt
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.core.exceptions import AuthError, PermissionDeniedError, ProfileIncompleteError
from app.features.auth.models import User

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts JWT from HttpOnly cookie, validates it,
    and fetches the corresponding user from DB.
    """
    token = request.cookies.get("access_token")

    if not token:
        raise AuthError("Authentication required. Session cookie missing.")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        token_type = payload.get("token_type")
        
        if not user_id:
            raise AuthError("Invalid session token payload.")
            
        if token_type and token_type != "access":
            raise AuthError("Invalid token type. Access token expected.")

    except jwt.ExpiredSignatureError:
        raise AuthError("Session expired. Please login again.")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid authentication token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthError("User associated with this session does not exist.")

    return user

class RoleChecker:
    """Enforces role-based access control for protected routes."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise PermissionDeniedError(
                "Access denied. Your role privileges are insufficient."
            )
        return current_user

# Global role guards
require_admin = RoleChecker(["ADMIN"])
require_jury_or_admin = RoleChecker(["ADMIN", "JURY"])

def require_completed_profile(current_user: User = Depends(get_current_user)) -> User:
    """
    Enforces profile completeness. Users logging in via Google OAuth must
    submit missing fields (e.g. phone, department, organization) before using 
    application APIs.
    """
    if not current_user.is_profile_complete:
        raise ProfileIncompleteError(
            "Account profile updates pending. Please update your details to access the portal features."
        )
    return current_user