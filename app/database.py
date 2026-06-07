


# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings

# # MySQL database connection URL loading
# DATABASE_URL = settings.DATABASE_URL

# # Establish MySQL database engine connection
# engine = create_engine(DATABASE_URL)

# # Thread-isolated session factory for generating clean database transactions
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Declarative base engine that maps all your feature-wise Python classes into database tables
# Base = declarative_base()

# def get_db():
#     """
#     Yields an active database session context to an individual API route,
#     ensuring transactions close out automatically when the HTTP request lifecycle ends.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# MySQL database connection URL loading
DATABASE_URL = settings.DATABASE_URL

# Establish MySQL database engine connection with optimized production connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Keep up to 20 connections open per worker process
    max_overflow=30,       # Allow scaling up to 50 connections under sudden peak loads
    pool_recycle=3600,     # Recycle connections older than 1 hour to prevent timeout disconnects
    pool_pre_ping=True     # Check connection health before using it (prevents "MySQL went away" errors)
)

# Thread-isolated session factory for generating clean database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base engine that maps all your feature-wise Python classes into database tables
Base = declarative_base()

def get_db():
    """
    Yields an active database session context to an individual API route,
    ensuring transactions close out automatically when the HTTP request lifecycle ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()