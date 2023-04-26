# Import SQLAlchemy modules
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_db_settings

db_settings = get_db_settings()


# Create a database engine object
engine = create_engine(
    "postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}".format(
        db_username=db_settings.DB_USERNAME,
        db_password=db_settings.DB_PASSWORD,
        db_host=db_settings.DB_HOST,
        db_port=db_settings.DB_PORT,
        db_name=db_settings.DB_NAME
    ),
    echo=True
)

# Create a session-maker object to provide a database session
Session = sessionmaker(engine)

# Create a base class for declarative models
Base = declarative_base()


async def get_db():
    db = Session()
    try:
        yield db  # Return the session to the calling function
    finally:
        db.close()  # Close the session when it is no longer needed
