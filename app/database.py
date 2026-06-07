# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings

# # Construct the local SQLite connection string
# DATABASE_URL = f"sqlite:///{settings.DB_PATH}"

# # check_same_thread=False is strictly required to permit SQLite's multi-threading model
# engine = create_engine(
#     DATABASE_URL, 
#     connect_args={"check_same_thread": False}
# )

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

# Establish MySQL database engine connection
engine = create_engine(DATABASE_URL)

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