from flask import Flask, request, jsonify
from flask_cors import CORS
import praw
import prawcore
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import requests
from src.database.db_handler import DatabaseHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize database handler
db_handler = DatabaseHandler()

def init_reddit():
    """Initialize Reddit API client with connection testing"""
    required_env_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT',
        'REDDIT_USERNAME',
        'REDDIT_PASSWORD'
    ]

    # Check if all required environment variables are set
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise Exception(f"Missing environment variables: {', '.join(missing_vars)}")

    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD')
        )
        
        # Test connection by getting the authenticated user
        username = reddit.user.me()
        logger.info(f"Successfully authenticated as: {username}")
        return reddit
    except prawcore.exceptions.OAuthException as e:
        logger.error(f"Authentication failed: {e}")
        raise Exception("Reddit authentication failed. Check your credentials.")
    except Exception as e:
        logger.error(f"Unexpected error initializing Reddit client: {e}")
        raise

def format_post(post):
    """Format a Reddit post into a clean dictionary"""
    try:
        return {
            'id': post.id,
            'title': post.title,
            'author': str(post.author) if post.author else '[deleted]',
            'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
            'subreddit': str(post.subreddit),
            'permalink': post.permalink,
            'url': post.url,
            'selftext': post.selftext,
            'num_comments': post.num_comments,
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'is_self': post.is_self,
            'is_video': post.is_video,
            'stickied': post.stickied,
            'over_18': post.over_18,
            'spoiler': post.spoiler,
            'link_flair_text': post.link_flair_text
        }
    except Exception as e:
        logger.error(f"Error formatting post {post.id}: {e}")
        raise

# Initialize Reddit client
try:
    reddit = init_reddit()
except Exception as e:
    logger.error(f"Failed to initialize Reddit client: {e}")
    reddit = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'reddit_client': 'initialized' if reddit else 'not initialized',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test Reddit API connection"""
    if not reddit:
        return jsonify({
            'status': 'error',
            'message': 'Reddit client not initialized'
        }), 500

    try:
        username = reddit.user.me()
        mod_subreddits = [str(subreddit) for subreddit in reddit.user.moderator_subreddits()]
        
        return jsonify({
            'status': 'success',
            'data': {
                'username': str(username),
                'moderated_subreddits': mod_subreddits
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/mod/sync', methods=['GET', 'POST'])
def sync_unmoderated_posts():
    """Fetch and sync unmoderated posts to database"""
    if not reddit:
        return jsonify({
            'status': 'error',
            'message': 'Reddit client not initialized'
        }), 500

    try:
        subreddit_name = request.args.get('subreddit', 'mod')
        limit = min(int(request.args.get('limit', 100)), 100)
        
        logger.info(f"Fetching unmoderated posts from r/{subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        posts_data = []
        
        for post in subreddit.mod.unmoderated(limit=limit):
            try:
                post_data = format_post(post)
                posts_data.append(post_data)
            except Exception as e:
                logger.error(f"Error processing post {post.id}: {e}")
                continue
        
        # Sync with database
        successful_updates = db_handler.bulk_upsert_posts(posts_data)
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_posts': len(posts_data),
                'successful_updates': successful_updates,
                'subreddit': subreddit_name
            }
        })

    except prawcore.exceptions.OAuthException as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Reddit authentication failed'
        }), 401
    except prawcore.exceptions.RequestException as e:
        logger.error(f"Connection error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Cannot connect to Reddit API'
        }), 503
    except Exception as e:
        logger.error(f"Error syncing posts: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/mod/stored-posts', methods=['GET'])
def get_stored_posts():
    """Get posts from database"""
    try:
        subreddit = request.args.get('subreddit')
        limit = min(int(request.args.get('limit', 100)), 100)
        
        posts = db_handler.get_unmoderated_posts(subreddit, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'posts': [
                    {
                        'id': post.id,
                        'title': post.title,
                        'author': post.author,
                        'subreddit': post.subreddit,
                        'created_utc': post.created_utc.isoformat(),
                        'moderation_status': post.moderation_status,
                        'last_updated': post.last_updated.isoformat()
                    }
                    for post in posts
                ],
                'count': len(posts)
            }
        })

    except Exception as e:
        logger.error(f"Error retrieving posts: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/mod/modqueue', methods=['GET'])
def get_mod_queue():
    """Get posts in moderation queue"""
    try:
        subreddit_name = request.args.get('subreddit', 'mod')
        limit = min(int(request.args.get('limit', 100)), 100)
        
        subreddit = reddit.subreddit(subreddit_name)
        queue_posts = []
        
        for post in subreddit.mod.modqueue(limit=limit):
            try:
                post_data = format_post(post)
                # Add modqueue-specific information
                post_data.update({
                    'mod_reports': post.mod_reports,
                    'user_reports': post.user_reports,
                    'report_reasons': post.report_reasons
                })
                queue_posts.append(post_data)
            except Exception as e:
                logger.error(f"Error processing post {post.id}: {e}")
                continue

        return jsonify({
            'status': 'success',
            'data': {
                'subreddit': subreddit_name,
                'posts': queue_posts,
                'count': len(queue_posts)
            }
        })
    except Exception as e:
        logger.error(f"Error fetching mod queue: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/db/status', methods=['GET'])
def get_db_status():
    """Get database status and counts"""
    try:
        # Get post counts
        total_posts = db_handler.get_post_count()
        unmoderated_posts = db_handler.get_post_count(status='unmoderated')
        
        # Get latest posts for preview
        latest_posts = db_handler.get_latest_posts(limit=5)
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_posts': total_posts,
                'unmoderated_posts': unmoderated_posts,
                'latest_posts': [{
                    'id': post.id,
                    'title': post.title,
                    'subreddit': post.subreddit,
                    'created_utc': post.created_utc.isoformat(),
                    'last_updated': post.last_updated.isoformat()
                } for post in latest_posts]
            }
        })
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/db/inspect', methods=['GET'])
def inspect_database():
    """Get detailed database inspection"""
    try:
        # Get various statistics
        stats = {
            'total_posts': db_handler.get_post_count(),
            'unmoderated_posts': db_handler.get_post_count(status='unmoderated'),
            'subreddit_summary': [
                {
                    'subreddit': subreddit,
                    'post_count': count
                }
                for subreddit, count in db_handler.get_subreddit_summary()
            ],
            'latest_posts': [
                {
                    'id': post.id,
                    'title': post.title,
                    'subreddit': post.subreddit,
                    'author': post.author,
                    'created_utc': post.created_utc.isoformat(),
                    'num_comments': post.num_comments,
                    'score': post.score,
                    'moderation_status': post.moderation_status,
                    'last_updated': post.last_updated.isoformat()
                }
                for post in db_handler.get_latest_posts(limit=5)
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        logger.error(f"Error inspecting database: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True) 
    