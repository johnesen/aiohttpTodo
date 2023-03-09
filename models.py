from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///todo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(150))
    created_at = Column(DateTime)
    user = Column(String(50))
    is_done = Column(Boolean)
    is_deleted = Column(Boolean)

    def __init__(self, user, title, description, created_at, is_done, is_deleted):
        self.user = user
        self.title = title
        self.description = description
        self.created_at = created_at
        self.is_done = is_done
        self.is_deleted = is_deleted
