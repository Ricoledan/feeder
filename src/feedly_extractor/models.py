"""Data models and structures for the Feedly Extractor."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List


@dataclass
class Article:
    """Represents a Feedly article with all relevant metadata."""
    
    id: str
    title: str
    url: str
    author: str
    published_date: str
    crawled_date: str
    source_title: str
    source_url: str
    source_stream_id: str
    summary: str
    content: str
    engagement: int
    language: str
    keywords: str
    categories: str
    tags: str
    read: bool
    visual_url: str
    word_count: int
    
    @classmethod
    def from_feedly_data(cls, data: Dict[str, Any]) -> 'Article':
        """Create Article from Feedly API response data."""
        from .utils import strip_html_tags
        
        # Get the canonical URL or fallback to alternate
        url = data.get('canonicalUrl', '')
        if not url and data.get('alternate'):
            url = data['alternate'][0].get('href', '')

        # Extract publication date
        published = data.get('published', 0)
        if published:
            published_date = datetime.fromtimestamp(published / 1000).isoformat()
        else:
            published_date = ''

        # Extract crawled date
        crawled = data.get('crawled', 0)
        if crawled:
            crawled_date = datetime.fromtimestamp(crawled / 1000).isoformat()
        else:
            crawled_date = ''

        # Extract and clean content
        summary = strip_html_tags(data.get('summary', {}).get('content', ''))
        content = strip_html_tags(data.get('content', {}).get('content', ''))

        return cls(
            id=data.get('id', ''),
            title=strip_html_tags(data.get('title', '')),
            url=url,
            author=data.get('author', ''),
            published_date=published_date,
            crawled_date=crawled_date,
            source_title=data.get('origin', {}).get('title', ''),
            source_url=data.get('origin', {}).get('htmlUrl', ''),
            source_stream_id=data.get('origin', {}).get('streamId', ''),
            summary=summary,
            content=content,
            engagement=data.get('engagement', 0),
            language=data.get('language', ''),
            keywords=', '.join(data.get('keywords', [])),
            categories=', '.join([cat.get('label', '') for cat in data.get('categories', [])]),
            tags=', '.join([tag.get('label', '') for tag in data.get('tags', [])]),
            read=data.get('unread', True) == False,
            visual_url=data.get('visual', {}).get('url', ''),
            word_count=len(content.split()) if content else 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Article to dictionary for CSV/JSON export."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'author': self.author,
            'published_date': self.published_date,
            'crawled_date': self.crawled_date,
            'source_title': self.source_title,
            'source_url': self.source_url,
            'source_stream_id': self.source_stream_id,
            'summary': self.summary,
            'content': self.content,
            'engagement': self.engagement,
            'language': self.language,
            'keywords': self.keywords,
            'categories': self.categories,
            'tags': self.tags,
            'read': self.read,
            'visual_url': self.visual_url,
            'word_count': self.word_count
        }


@dataclass
class Category:
    """Represents a Feedly category/folder."""
    
    id: str
    label: str
    
    @classmethod
    def from_feedly_data(cls, data: Dict[str, Any]) -> 'Category':
        """Create Category from Feedly API response data."""
        return cls(
            id=data.get('id', ''),
            label=data.get('label', 'Unnamed')
        )


@dataclass
class FetchOptions:
    """Options for fetching articles from Feedly."""
    
    days_back: int = 7
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    category: Optional[str] = None
    unread_only: bool = False
    max_articles: Optional[int] = None
    api_delay: float = 0.5
    output_prefix: Optional[str] = None
    output_format: str = 'all'
    progressive_save: bool = True
    quiet: bool = False