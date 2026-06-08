# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     PORT: int = 8000
#     COOKIE_SECURE: bool = False  # Central switch for HTTPS secure cookies
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     DATABASE_URL: str
#     UPLOAD_DIR: str = "uploads"
#     FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
#     # Frontend Dashboard URL (Loaded dynamically from your .env)
#     FRONTEND_DASHBOARD_URL: str
    
#     # Google OAuth Configuration
#     GOOGLE_CLIENT_ID: str
#     GOOGLE_CLIENT_SECRET: str
#     GOOGLE_REDIRECT_URI: str

#     # SMTP Email Configuration Keys
#     SMTP_HOST: str
#     SMTP_PORT: int = 587
#     SMTP_USERNAME: str
#     SMTP_PASSWORD: str
#     SMTP_FROM_EMAIL: str
    
#     # System Master Admin Seeding Credentials
#     ADMIN_EMAIL: str
#     ADMIN_DEFAULT_PASSWORD: str

#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 7

#     class Config:
#         env_file = ".env"
#         extra = "ignore"

# settings = Settings()


# for multiple email for mail sending


from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    COOKIE_SECURE: bool = False  # Central switch for HTTPS secure cookies
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    UPLOAD_DIR: str = "uploads"
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Frontend Dashboard URL (Loaded dynamically from your .env)
    FRONTEND_DASHBOARD_URL: str
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # SMTP Email Configuration Keys (Supports multiple rotating accounts)
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAMES: str    
    SMTP_PASSWORDS: str    
    
    # System Master Admin Seeding Credentials
    ADMIN_EMAIL: str
    ADMIN_DEFAULT_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()