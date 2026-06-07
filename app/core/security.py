# from datetime import datetime, timedelta, timezone
# from typing import Optional
# from passlib.context import CryptContext
# import jwt
# from app.config import settings

# # Configure Passlib to use salted Bcrypt for robust credential encryption
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     """
#     Hashes a plain text password using Bcrypt with a cryptographically secure random salt.
#     """
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Verifies a plain text credential password input against a saved Bcrypt string hash.
#     """
#     return pwd_context.verify(plain_password, hashed_password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Generates a secure JSON Web Token containing claims like user_id and authorization roles.
#     """
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
#     to_encode.update({"exp": int(expire.timestamp())})
#     return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)





# def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
#     """
#     Generates a secure JSON Web Token using time limits defined in .env.
#     """
#     to_encode = data.copy()
    
#     # Logic: Use provided delta if passed, otherwise fallback to .env settings
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     to_encode.update({"exp": int(expire.timestamp())})
    
#     return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)



from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
import jwt
from app.config import settings

# Configure Passlib to use salted Bcrypt for robust credential encryption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using Bcrypt with a cryptographically secure random salt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text credential password input against a saved Bcrypt string hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JSON Web Token containing claims like user_id, roles and token_type.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": int(expire.timestamp()),
        "token_type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure refresh JSON Web Token containing claims like user_id and token_type.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({
        "exp": int(expire.timestamp()),
        "token_type": "refresh"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)