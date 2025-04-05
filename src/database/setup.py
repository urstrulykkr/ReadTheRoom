from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create base class for declarative models
Base = declarative_base()

class RedditPost(Base):
    __tablename__ = 'reddit_posts'

    # Primary key and unique identifiers
    id = Column(String, primary_key=True)
    permalink = Column(String, unique=True)
    
    # Post metadata
    title = Column(String)
    author = Column(String)
    subreddit = Column(String)
    created_utc = Column(DateTime)
    
    # Post content
    selftext = Column(Text)
    url = Column(String)
    
    # Post statistics
    score = Column(Integer)
    num_comments = Column(Integer)
    upvote_ratio = Column(Float)
    
    # Post flags
    is_self = Column(Boolean)
    is_video = Column(Boolean)
    stickied = Column(Boolean)
    over_18 = Column(Boolean)
    spoiler = Column(Boolean)
    
    # Moderation metadata
    link_flair_text = Column(String, nullable=True)
    moderation_status = Column(String, default='unmoderated')
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    # Create database URL
    DATABASE_URL = "postgresql://localhost/reddit_mod_db"
    # Or if you created a specific user:
    # DATABASE_URL = "postgresql://postgres:postgres@localhost/reddit_mod_db"
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(bind=engine)
    
    return SessionLocal()

if __name__ == "__main__":
    init_db() 