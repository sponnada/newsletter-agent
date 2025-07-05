import aiohttp
from datetime import datetime
from typing import List
import logging

from ..models import NewsItem

logger = logging.getLogger(__name__)

class NYTimesSource:
    """Fetches articles from New York Times API"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: str, max_items: int = 10):
        self.session = session
        self.api_key = api_key
        self.max_items = max_items
    
    async def fetch(self) -> List[NewsItem]:
        """Fetch articles from New York Times API"""
        if not self.api_key:
            logger.warning("NYT API key not configured")
            return []
        
        url = "https://api.nytimes.com/svc/topstories/v2/home.json"
        params = {'api-key': self.api_key}
        
        try:
            logger.info("Fetching from New York Times API...")
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"NYT API error: {response.status}")
                    return []
                
                data = await response.json()
                
                items = []
                for article in data.get('results', [])[:self.max_items]:
                    # Skip articles without URLs
                    if not article.get('url'):
                        continue
                    
                    # Parse publication date
                    published_at = None
                    if article.get('published_date'):
                        try:
                            published_at = datetime.fromisoformat(article['published_date'])
                        except ValueError:
                            pass
                    
                    item = NewsItem(
                        title=article['title'],
                        url=article['url'],
                        summary=article.get('abstract', ''),
                        source='New York Times',
                        published_at=published_at,
                        score=0
                    )
                    items.append(item)
                
                logger.info(f"Successfully fetched {len(items)} articles from NYT")
                return items
                
        except Exception as e:
            logger.error(f"Error fetching NYT: {e}")
            return []