from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging
from typing import List, Dict, Optional

from .models import Base, RedditPost
from .config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def process_post_data(self, post_data: Dict) -> Dict:
        """Process and validate post data before database insertion"""
        processed_data = post_data.copy()
        
        # Convert created_utc from ISO format if it's a string
        if isinstance(processed_data.get('created_utc'), str):
            processed_data['created_utc'] = datetime.fromisoformat(
                processed_data['created_utc'].replace('Z', '+00:00')
            )

        # Ensure required fields
        required_fields = ['id', 'title', 'author', 'subreddit']
        for field in required_fields:
            if not processed_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        return processed_data

    def upsert_post(self, post_data: Dict) -> Optional[RedditPost]:
        """Insert or update a single post with error handling"""
        session = self.get_session()
        try:
            processed_data = self.process_post_data(post_data)
            
            # Check if post exists
            post = session.query(RedditPost).filter_by(id=processed_data['id']).first()
            
            if post:
                # Update existing post
                for key, value in processed_data.items():
                    if hasattr(post, key):
                        setattr(post, key, value)
            else:
                # Create new post
                post = RedditPost(**processed_data)
                session.add(post)
            
            session.commit()
            return post

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error for post {post_data.get('id')}: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error upserting post {post_data.get('id')}: {e}")
        finally:
            session.close()
        
        return None

    def bulk_upsert_posts(self, posts_data: List[Dict]) -> int:
        """Bulk insert or update posts with error handling"""
        successful_updates = 0
        
        for post_data in posts_data:
            try:
                if self.upsert_post(post_data):
                    successful_updates += 1
            except Exception as e:
                logger.error(f"Error in bulk upsert for post {post_data.get('id')}: {e}")
                continue
        
        return successful_updates

    def get_unmoderated_posts(self, 
                            subreddit: Optional[str] = None, 
                            limit: int = 100) -> List[RedditPost]:
        """Get unmoderated posts with optional subreddit filter"""
        session = self.get_session()
        try:
            query = session.query(RedditPost)\
                .filter(RedditPost.moderation_status == 'unmoderated')
            
            if subreddit:
                query = query.filter(RedditPost.subreddit == subreddit)
            
            return query.order_by(RedditPost.created_utc.desc())\
                       .limit(limit)\
                       .all()
        finally:
            session.close()

    def get_post_count(self, status=None):
        """Get total number of posts"""
        session = self.get_session()
        try:
            query = session.query(RedditPost)
            if status:
                query = query.filter(RedditPost.moderation_status == status)
            return query.count()
        finally:
            session.close()

    def get_latest_posts(self, limit=5):
        """Get latest posts ordered by created_utc"""
        session = self.get_session()
        try:
            return session.query(RedditPost)\
                .order_by(RedditPost.created_utc.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    def get_subreddit_summary(self):
        """Get summary of posts by subreddit"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            return session.query(
                RedditPost.subreddit,
                func.count(RedditPost.id).label('post_count')
            ).group_by(RedditPost.subreddit).all()
        finally:
            session.close() 