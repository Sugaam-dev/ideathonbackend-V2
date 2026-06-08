import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.core import security
from app.core.handlers import register_exception_handlers
from app.core.rate_limiter import limiter

# Import separate feature space router entrypoints
from app.features.auth.router import router as auth_router
from app.features.ideas.router import router as ideas_router
from app.features.ideas.admin_router import admin_router as ideas_admin_router  
from app.features.evaluations.router import router as evaluations_router  

# Import database models to ensure structured migrations on initialization
from app.features.auth.models import User, EmailLog
from app.features.ideas.models import Idea, Attachment
from app.features.evaluations.models import Evaluation

def seed_default_administrator_account() -> None:
    """Provisions base administration account on database setup using parameters from configurations."""
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin_exists:
            master_admin = User(
                name="PMRG Admin",
                email=settings.ADMIN_EMAIL,
                phone="0000000000",
                organization="PMRG Solution",
                password_hash=security.hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                role="ADMIN",
                is_active=True,
                is_profile_complete=True  # Seeds the master admin with completed profile
            )
            db.add(master_admin)
            db.commit()
            print("[System Boot Sync] Base administration credentials provisioned successfully from configuration keys.")
    except Exception as e:
        print(f"[System Boot Error] Failed to synchronize administrator row seed: {str(e)}")
    finally:
        db.close()

# 1. Execute physical table building across your database server safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[System Boot Sync] Table creation skipped/handled by another worker: {e}")

# 2. Run seed logic to establish the system super-user safely
try:
    seed_default_administrator_account()
except Exception as e:
    print(f"[System Boot Sync] Admin seeding skipped/handled by another worker: {e}")

# 3. Instantiate the core FastAPI application instance
app = FastAPI(
    title="PMRG Ideathon Portal",
    version="2.0.0",
    description="Secure Modular Enterprise Hackathon Platform Architecture"
)

# 4. Attach Rate Limiter and Exception Handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
register_exception_handlers(app)

# 5. Configure cross-origin policies (CORS) to accept incoming secure cookie headers
# Stripping whitespaces to guarantee clear array parsing profiles
origin_permissions_list = [origin.strip() for origin in settings.FRONTEND_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_permissions_list,
    allow_credentials=True,  # CRITICAL: Authorizes browser HttpOnly cookie transit handling
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Bind routers into clean structural API gateway namespaces
app.include_router(auth_router)
app.include_router(ideas_router)
app.include_router(ideas_admin_router)  
app.include_router(evaluations_router)  

@app.get("/", tags=["Root Monitoring Check"])
def health_check_index():
    return {"status": "online", "system": "PMRG Ideathon Portal Backend v2.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)