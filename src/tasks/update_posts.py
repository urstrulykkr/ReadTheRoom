import schedule
import time
from src.database.db_handler import DatabaseHandler
from app import reddit, format_post
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_unmoderated_posts():
    """Fetch and update unmoderated posts"""
    try:
        db = DatabaseHandler()
        subreddit = reddit.subreddit('mod')
        
        posts = []
        for post in subreddit.mod.unmoderated(limit=100):
            try:
                post_data = format_post(post)
                posts.append(post_data)
            except Exception as e:
                logger.error(f"Error processing post {post.id}: {e}")
                continue
        
        db.bulk_upsert_posts(posts)
        logger.info(f"Updated {len(posts)} unmoderated posts")
    
    except Exception as e:
        logger.error(f"Error updating unmoderated posts: {e}")

def run_scheduler():
    """Run the scheduler"""
    # Update posts every 5 minutes
    schedule.every(5).minutes.do(update_unmoderated_posts)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler() 