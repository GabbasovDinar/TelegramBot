from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager

from config import DATABASE_URL

# Creating a database engine
engine = create_engine(DATABASE_URL)

# Creating a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Defining a base class for models
Base = declarative_base()


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
