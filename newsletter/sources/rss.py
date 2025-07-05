import feedparser
from datetime import datetime
from typing import List
import logging

from ..models import NewsItem

logger = logging.getLogger(__name__)

class RSSSource:
    """Fetches articles from RSS feeds"""
    
    def __init__(self, urls: List[str], items_per_feed: int = 5):
        self.urls = urls
        self.items_per_feed = items_per_feed
    
    async def fetch(self) -> List[NewsItem]:
        """Fetch articles from RSS feeds"""
        items = []
        
        for url in self.urls:
            try:
                logger.info(f"Fetching RSS feed: {url}")
                feed = feedparser.parse(url)
                
                feed_title = feed.feed.get('title', 'RSS Feed')
                
                for entry in feed.entries[:self.items_per_feed]:
                    # Parse published date
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            published_at = datetime(*entry.published_parsed[:6])
                        except:
                            pass
                    
                    item = NewsItem(
                        title=entry.title,
                        url=entry.link,
                        summary=entry.get('summary', ''),
                        source=f"{feed_title} (RSS)",
                        published_at=published_at,
                        score=0
                    )
                    items.append(item)
                
                logger.info(f"Fetched {len(feed.entries[:self.items_per_feed])} items from {feed_title}")
                
            except Exception as e:
                logger.error(f"Error fetching RSS feed {url}: {e}")
                continue
        
        logger.info(f"Total RSS items fetched: {len(items)}")
        return items