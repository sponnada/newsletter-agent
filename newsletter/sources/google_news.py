import aiohttp
from datetime import datetime
from typing import List
import logging

from ..models import NewsItem

logger = logging.getLogger(__name__)

class GoogleNewsSource:
    """Fetches news from Google News API (NewsAPI.org)"""
    
    def __init__(self, session: aiohttp.ClientSession, api_key: str, max_items: int = 10):
        self.session = session
        self.api_key = api_key
        self.max_items = max_items
    
    async def fetch(self) -> List[NewsItem]:
        """Fetch news from Google News API"""
        if not self.api_key:
            logger.warning("Google News API key not configured")
            return []
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': self.api_key,
            'pageSize': self.max_items,
            'language': 'en'
        }
        
        try:
            logger.info("Fetching from Google News API...")
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Google News API error: {response.status}")
                    return []
                
                data = await response.json()
                
                if data.get('status') != 'ok':
                    logger.error(f"Google News API error: {data.get('message', 'Unknown error')}")
                    return []
                
                items = []
                for article in data.get('articles', []):
                    # Skip articles without URLs
                    if not article.get('url'):
                        continue
                    
                    # Parse publication date
                    published_at = None
                    if article.get('publishedAt'):
                        try:
                            published_at = datetime.fromisoformat(
                                article['publishedAt'].replace('Z', '+00:00')
                            )
                        except ValueError:
                            pass
                    
                    item = NewsItem(
                        title=article['title'],
                        url=article['url'],
                        summary=article.get('description', ''),
                        source=f"Google News ({article.get('source', {}).get('name', 'Unknown')})",
                        published_at=published_at,
                        score=0
                    )
                    items.append(item)
                
                logger.info(f"Successfully fetched {len(items)} articles from Google News")
                return items
                
        except Exception as e:
            logger.error(f"Error fetching Google News: {e}")
            return []