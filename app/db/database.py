from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.config import settings

# Create SQLAlchemy engine with the provided DATABASE_URL
engine = create_engine(settings.DATABASE_URL, echo=False)

# Configure a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to retrieve a database session for API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
