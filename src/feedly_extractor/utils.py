"""Utility functions for the Feedly Extractor."""

import re
from html.parser import HTMLParser
from datetime import datetime
from typing import Optional


class HTMLStripper(HTMLParser):
    """Simple HTML tag stripper"""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return ''.join(self.text)


def strip_html_tags(html: str) -> str:
    """Remove HTML tags from text"""
    if not html:
        return ''
    
    try:
        # Try HTML parser first
        stripper = HTMLStripper()
        stripper.feed(html)
        return stripper.get_data().strip()
    except Exception:
        # Fallback to regex
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html).strip()


def get_timestamp_from_days_ago(days: int) -> int:
    """Get timestamp for N days ago"""
    from datetime import timedelta
    date_ago = datetime.now() - timedelta(days=days)
    return int(date_ago.timestamp() * 1000)


def get_timestamp_from_date(date_str: str) -> int:
    """Convert date string (YYYY-MM-DD) to timestamp"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return int(date_obj.timestamp() * 1000)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def validate_date_range(start_date: Optional[str], end_date: Optional[str], 
                       days_back: Optional[int], max_days: int = 365) -> tuple[int, Optional[int]]:
    """Validate and convert date range to timestamps"""
    from .config import Config
    
    # Determine newer_than timestamp
    if start_date:
        newer_than = get_timestamp_from_date(start_date)
        print(f"📅 Using start date: {start_date}")
    else:
        days = days_back or Config.DEFAULT_DAYS_BACK
        newer_than = get_timestamp_from_days_ago(days)
        print(f"📅 Looking back {days} days")

    # Determine older_than timestamp
    older_than = None
    if end_date:
        older_than = get_timestamp_from_date(end_date)
        print(f"📅 Using end date: {end_date}")
        
        # Validate date range
        if older_than <= newer_than:
            raise ValueError("End date must be after start date")
        
        # Check if range is too large
        days_diff = (older_than - newer_than) / (1000 * 60 * 60 * 24)
        if days_diff > max_days:
            print(f"⚠️  Date range spans {days_diff:.0f} days. This may take a while...")

    return newer_than, older_than


def generate_output_filename(prefix: Optional[str] = None) -> str:
    """Generate output filename with timestamp"""
    if prefix:
        return prefix
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"feedly_articles_{timestamp}"