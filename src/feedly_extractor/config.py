"""Configuration constants and settings for the Feedly Extractor."""

import os
from typing import Optional


class Config:
    """Configuration constants for the application"""
    
    # API Configuration
    API_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 0.3
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]  # Added 429 for rate limiting
    
    # Request Settings
    PAGE_SIZE = 250  # Reduced from 1000 to be more conservative
    API_DELAY = 0.5  # Increased from 0.1 to be more respectful of rate limits
    RATE_LIMIT_DELAY = 60  # Wait 60 seconds when rate limited
    
    # Rate Limiting Prevention
    SAFE_ARTICLE_LIMIT = 5000  # Conservative limit to avoid rate limiting
    PROGRESSIVE_DELAY_THRESHOLD = 2000  # Start increasing delays after this many articles
    MAX_DELAY = 3.0  # Maximum delay between requests
    
    # Application Limits
    MAX_DATE_RANGE_DAYS = 365
    DEFAULT_DAYS_BACK = 7
    
    # File Settings
    DEFAULT_OUTPUT_FORMAT = 'all'
    
    @classmethod
    def get_access_token(cls) -> Optional[str]:
        """Get Feedly access token from environment variables."""
        return os.getenv('FEEDLY_ACCESS_TOKEN')
    
    @classmethod
    def validate_token(cls, token: Optional[str] = None) -> str:
        """Validate and return access token."""
        if not token:
            token = cls.get_access_token()
        
        if not token:
            raise ValueError(
                "FEEDLY_ACCESS_TOKEN not found in environment variables.\n"
                "Create a .env file with: FEEDLY_ACCESS_TOKEN=your_token_here\n"
                "Get your token at: https://feedly.com/v3/auth/dev"
            )
        
        return token