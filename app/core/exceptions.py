# class AuthError(Exception):
#     """Raised when authentication credentials or token validation contexts fail or expire."""
#     def __init__(self, detail: str = "Could not validate authentication credentials"):
#         self.detail = detail

# class PermissionDeniedError(Exception):
#     """Raised when an active identity attempts an operation beyond their role clearances."""
#     def __init__(self, detail: str = "Action forbidden for your current role parameters"):
#         self.detail = detail

# class DuplicateResourceError(Exception):
#     """Raised when unique database row validations are breached (e.g., duplicated registration emails)."""
#     def __init__(self, detail: str = "Requested resource identifier already exists"):
#         self.detail = detail

# class ResourceNotFoundError(Exception):
#     """Raised when a query looks up a missing index entity row."""
#     def __init__(self, detail: str = "The requested database entry does not exist"):
#         self.detail = detail

# class BadRequestError(Exception):
#     """Raised when input validations or business rule conditions fail (e.g., edit locks or file size boundaries)."""
#     def __init__(self, detail: str = "Invalid operational request payload parameters"):
#         self.detail = detail

class BasePortalError(Exception):
    """Base exception class for all custom portal errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class AuthError(BasePortalError):
    """Raised when authentication fails or is required."""
    def __init__(self, message: str = "Authentication required."):
        super().__init__(message, status_code=401)

class TokenRefreshError(AuthError):
    """Raised when refresh token validation or rotation fails."""
    def __init__(self, message: str = "Refresh token invalid or expired."):
        super().__init__(message)

class UserNotRegisteredError(AuthError):
    """Raised when trying to log in with an email that does not exist."""
    def __init__(self, message: str = "This email address is not registered."):
        super().__init__(message)

class IncorrectPasswordError(AuthError):
    """Raised when the password verification fails during login."""
    def __init__(self, message: str = "Incorrect password."):
        super().__init__(message)

class PermissionDeniedError(BasePortalError):
    """Raised when a user does not have sufficient role privileges."""
    def __init__(self, message: str = "Access denied."):
        super().__init__(message, status_code=403)

class ProfileIncompleteError(BasePortalError):
    """Raised when a user logs in via Google and has not completed their profile setup."""
    def __init__(self, message: str = "Google OAuth login success. Profile completion is required to access the platform."):
        super().__init__(message, status_code=403)

class ResourceNotFoundError(BasePortalError):
    """Raised when a requested database row or key is missing."""
    def __init__(self, message: str = "Resource not found."):
        super().__init__(message, status_code=404)

class DuplicateResourceError(BasePortalError):
    """Raised when attempting to create a resource that already exists."""
    def __init__(self, message: str = "Resource already exists."):
        super().__init__(message, status_code=409)

class BadRequestError(BasePortalError):
    """Raised for malformed parameters or workflow execution blocks."""
    def __init__(self, message: str = "Bad request."):
        super().__init__(message, status_code=400)

class RateLimitExceededError(BasePortalError):
    """Raised when a client exceeds rate limits."""
    def __init__(self, message: str = "Too many requests. Rate limit exceeded."):
        super().__init__(message, status_code=429)