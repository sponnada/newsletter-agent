import os
from datetime import datetime
from typing import List
import logging

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

from ..models import NewsItem

logger = logging.getLogger(__name__)

class RedditSource:
    """Fetches posts from Reddit subreddits"""
    
    def __init__(self, subreddits: List[str], posts_per_subreddit: int = 5):
        self.subreddits = subreddits
        self.posts_per_subreddit = posts_per_subreddit
        self.reddit_client = None
        
        if PRAW_AVAILABLE:
            self._setup_reddit()
    
    def _setup_reddit(self):
        """Setup Reddit API client"""
        if not PRAW_AVAILABLE:
            logger.warning("praw library not installed. Cannot set up Reddit client.")
            return
            
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.warning("Reddit API credentials not found in environment variables")
            return
        
        try:
            self.reddit_client = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent='newsletter_agent/1.0'
            )
        except Exception as e:
            logger.error(f"Error setting up Reddit client: {e}")
    
    async def fetch(self) -> List[NewsItem]:
        """Fetch posts from Reddit subreddits"""
        if not PRAW_AVAILABLE:
            logger.warning("praw library not installed. Skipping Reddit.")
            return []
        
        if not self.reddit_client:
            logger.warning("Reddit client not configured. Skipping Reddit.")
            return []
        
        try:
            items = []
            
            for subreddit_name in self.subreddits:
                try:
                    logger.info(f"Fetching from r/{subreddit_name}")
                    subreddit = self.reddit_client.subreddit(subreddit_name)
                    
                    for submission in subreddit.hot(limit=self.posts_per_subreddit):
                        item = NewsItem(
                            title=submission.title,
                            url=submission.url,
                            summary=submission.selftext[:200] if submission.selftext else '',
                            source=f'Reddit r/{subreddit_name}',
                            published_at=datetime.fromtimestamp(submission.created_utc),
                            score=submission.score
                        )
                        items.append(item)
                    
                    logger.info(f"Fetched {self.posts_per_subreddit} posts from r/{subreddit_name}")
                    
                except Exception as e:
                    logger.error(f"Error fetching Reddit r/{subreddit_name}: {e}")
                    continue
            
            logger.info(f"Total Reddit items fetched: {len(items)}")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching Reddit: {e}")
            return []