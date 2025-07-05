import aiohttp
from datetime import datetime
from typing import List
import logging

from ..models import NewsItem

logger = logging.getLogger(__name__)

class HackerNewsSource:
    """Fetches top stories from Hacker News"""
    
    def __init__(self, session: aiohttp.ClientSession, max_items: int = 10):
        self.session = session
        self.max_items = max_items
    
    async def fetch(self) -> List[NewsItem]:
        """Fetch top stories from Hacker News"""
        try:
            # Get top story IDs
            async with self.session.get('https://hacker-news.firebaseio.com/v0/topstories.json') as response:
                story_ids = await response.json()
            
            # Fetch details for top stories
            items = []
            max_items = min(self.max_items, 20)
            
            logger.info(f"Fetching {max_items} stories from Hacker News...")
            
            for story_id in story_ids[:max_items]:
                try:
                    async with self.session.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json') as response:
                        story = await response.json()
                    
                    if story and story.get('type') == 'story':
                        item = NewsItem(
                            title=story['title'],
                            url=story.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                            summary='',
                            source='Hacker News',
                            published_at=datetime.fromtimestamp(story['time']),
                            score=story.get('score', 0)
                        )
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error fetching HN story {story_id}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} stories from Hacker News")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching Hacker News: {e}")
            return []