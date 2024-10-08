from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    Date,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    url = Column(String(255), unique=True)
    rating = Column(Float)
    rating_count = Column(Integer)
    review_count = Column(Integer)
    description = Column(Text)
    genres = Column(JSON, nullable=True)
    pages = Column(Integer)
    release_date = Column(Date)
    currently_reading = Column(Integer)
    want_to_read = Column(Integer)
