from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class RedditPost(Base):
    __tablename__ = 'reddit_posts'

    # Primary and unique identifiers
    id = Column(String(10), primary_key=True)  # Reddit post IDs are typically 6-8 chars
    permalink = Column(String(500), unique=True, nullable=False)
    
    # Post metadata
    title = Column(String(300), nullable=False)  # Reddit titles have max length
    author = Column(String(100), nullable=False)
    subreddit = Column(String(100), nullable=False)
    created_utc = Column(DateTime, nullable=False)
    
    # Content
    selftext = Column(Text)
    url = Column(String(2000))  # URLs can be long
    
    # Statistics
    score = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)
    upvote_ratio = Column(Float)
    
    # Flags
    is_self = Column(Boolean, default=False)
    is_video = Column(Boolean, default=False)
    stickied = Column(Boolean, default=False)
    over_18 = Column(Boolean, default=False)
    spoiler = Column(Boolean, default=False)
    
    # Moderation data
    link_flair_text = Column(String(200))
    moderation_status = Column(String(50), default='unmoderated', 
                             nullable=False)
    
    # Timestamps
    first_seen = Column(DateTime, server_default=func.now(), nullable=False)
    last_updated = Column(DateTime, server_default=func.now(), 
                         onupdate=func.now(), nullable=False)

    # Indexes for frequent queries
    __table_args__ = (
        Index('idx_created_utc', created_utc.desc()),
        Index('idx_subreddit_status', subreddit, moderation_status),
        Index('idx_author', author),
    )

    def __repr__(self):
        return f"<RedditPost(id='{self.id}', title='{self.title[:30]}...', subreddit='{self.subreddit}')>" 