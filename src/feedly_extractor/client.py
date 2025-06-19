"""Feedly API client for handling authentication and requests."""

import time
import logging
from typing import Dict, Any, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import Config
from .models import Category


class FeedlyClient:
    """Client for interacting with the Feedly API."""
    
    def __init__(self, access_token: str):
        """Initialize with Feedly access token."""
        self.access_token = access_token
        self.base_url = "https://cloud.feedly.com/v3"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.session = self._create_session()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        return logger

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=Config.MAX_RETRIES,
            backoff_factor=Config.RETRY_BACKOFF_FACTOR,
            status_forcelist=Config.RETRY_STATUS_CODES,
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with timeout and error handling"""
        kwargs['timeout'] = kwargs.get('timeout', Config.API_TIMEOUT)
        kwargs['headers'] = self.headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.logger.error("Authentication failed. Check your access token.")
            elif e.response.status_code == 429:
                self.logger.warning(f"Rate limit exceeded. Waiting {Config.RATE_LIMIT_DELAY} seconds before retrying...")
                time.sleep(Config.RATE_LIMIT_DELAY)
                # Retry the request once after waiting
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            raise

    def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile information"""
        url = f"{self.base_url}/profile"
        response = self._make_request("GET", url)
        return response.json()

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all feed subscriptions"""
        url = f"{self.base_url}/subscriptions"
        response = self._make_request("GET", url)
        return response.json()

    def get_categories(self) -> List[Category]:
        """Get all categories/folders"""
        url = f"{self.base_url}/categories"
        response = self._make_request("GET", url)
        categories_data = response.json()
        return [Category.from_feedly_data(cat) for cat in categories_data]

    def get_stream_content(self, stream_id: str, newer_than: int, 
                          older_than: Optional[int] = None,
                          count: int = Config.PAGE_SIZE, 
                          unread_only: bool = False,
                          continuation: Optional[str] = None) -> Dict[str, Any]:
        """Get content from a stream (feed, category, or global)"""
        url = f"{self.base_url}/streams/contents"
        params = {
            "streamId": stream_id,
            "count": count,
            "unreadOnly": "true" if unread_only else "false"
        }

        if continuation:
            params["continuation"] = continuation
        else:
            params["newerThan"] = newer_than
            if older_than:
                params["olderThan"] = older_than

        response = self._make_request("GET", url, params=params)
        return response.json()

    def find_category_by_name(self, category_name: str) -> Optional[Category]:
        """Find category by name (case-insensitive partial match)"""
        categories = self.get_categories()
        
        # Try exact match first
        for cat in categories:
            if category_name.lower() == cat.label.lower():
                return cat
        
        # Then try partial match
        for cat in categories:
            if category_name.lower() in cat.label.lower():
                return cat
        
        return None