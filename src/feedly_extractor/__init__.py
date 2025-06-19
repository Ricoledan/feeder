"""
Feeder Package

A tool for extracting articles from Feedly feeds with flexible filtering and export options.
"""

__version__ = "1.0.0"
__author__ = "Ricardo Ledan"

from .client import FeedlyClient
from .extractor import ArticleExtractor
from .config import Config

__all__ = ["FeedlyClient", "ArticleExtractor", "Config"]