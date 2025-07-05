from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class NewsItem:
    """Represents a single news item from any source"""
    title: str
    url: str
    summary: str = ""
    source: str = ""
    published_at: Optional[datetime] = None
    score: int = 0
    category: str = ""
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
    
    def matches_keywords(self, include_keywords: List[str], exclude_keywords: List[str]) -> bool:
        """Check if item matches keyword filters"""
        text_to_check = f"{self.title} {self.summary}".lower()
        
        # Include keywords (if specified)
        if include_keywords:
            if not any(keyword.lower() in text_to_check for keyword in include_keywords):
                return False
        
        # Exclude keywords
        if exclude_keywords:
            if any(keyword.lower() in text_to_check for keyword in exclude_keywords):
                return False
        
        return True