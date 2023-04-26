# Import SQLAlchemy modules
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite database URL
SQLALCHEMY_DATABASE_URL = 'sqlite:///./database/db.db'

# Create a database engine object
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Use this argument to avoid threading issues with SQLite
)

# Create a session-maker object to provide a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative SQLAlchemy models
Base = declarative_base()

# Create all tables defined in SQLAlchemy models
Base.metadata.create_all(bind=engine)


# Define an asynchronous function to get a database session
async def get_db():
    db = SessionLocal()
    try:
        yield db  # Return the session to the calling function
    finally:
        db.close()  # Close the session when it is no longer needed
