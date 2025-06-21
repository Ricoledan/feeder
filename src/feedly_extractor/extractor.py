"""Main extractor class that orchestrates the article fetching process."""

import time
from typing import List, Optional

import requests

from .client import FeedlyClient
from .config import Config
from .file_handlers import FileHandler, ProgressiveSaver
from .models import Article, FetchOptions
from .utils import validate_date_range


class ArticleExtractor:
    """Main class for extracting articles from Feedly."""
    
    def __init__(self, access_token: str):
        """Initialize with Feedly access token."""
        self.client = FeedlyClient(access_token)
    
    def get_articles(self, options: FetchOptions) -> List[Article]:
        """Get articles based on fetch options."""
        if not options.quiet:
            print("🔍 Fetching user profile...")
        
        profile = self.client.get_user_profile()
        user_id = profile['id']

        # Validate and get timestamps
        newer_than, older_than = validate_date_range(
            options.start_date, options.end_date, options.days_back
        )

        # Determine stream ID
        stream_id = self._get_stream_id(user_id, options.category, options.quiet)
        if not stream_id:
            return []

        if not options.quiet:
            from datetime import datetime
            print(f"📰 Fetching articles from {datetime.fromtimestamp(newer_than / 1000).strftime('%Y-%m-%d %H:%M')}...")
            if older_than:
                print(f"📰 Until {datetime.fromtimestamp(older_than / 1000).strftime('%Y-%m-%d %H:%M')}...")

        # Setup progressive saver if needed
        progressive_saver = None
        if options.progressive_save and options.output_prefix:
            progressive_saver = ProgressiveSaver(options.output_prefix, options.output_format)

        all_articles = []
        continuation = None
        page = 1
        current_delay = options.api_delay

        while True:
            if not options.quiet:
                print(f"   📄 Fetching page {page}...")

            try:
                data = self.client.get_stream_content(
                    stream_id=stream_id,
                    newer_than=newer_than,
                    older_than=older_than,
                    count=Config.PAGE_SIZE,
                    unread_only=options.unread_only,
                    continuation=continuation
                )
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    print("❌ Authentication failed. Check your access token.")
                    return all_articles
                elif e.response.status_code == 429:
                    print("⚠️  Rate limit exceeded. Try again later or reduce the date range.")
                    print("💡 Tip: Use --max-articles to limit the number of articles fetched")
                    return all_articles
                raise

            articles_data = data.get('items', [])
            if not articles_data:
                break

            if not options.quiet:
                print(f"   ✅ Found {len(articles_data)} articles on page {page}")

            # Convert to Article objects
            batch_articles = [Article.from_feedly_data(article_data) for article_data in articles_data]
            all_articles.extend(batch_articles)

            # Progressive save
            if progressive_saver:
                progressive_saver.save_batch(batch_articles, options.quiet)

            # Check if we've reached the max article limit
            if options.max_articles and len(all_articles) >= options.max_articles:
                if not options.quiet:
                    print(f"   🛑 Reached maximum article limit: {options.max_articles}")
                all_articles = all_articles[:options.max_articles]
                break
            
            # Check if we're approaching rate limits
            if len(all_articles) >= Config.SAFE_ARTICLE_LIMIT:
                if not options.quiet:
                    print(f"   ⚠️  Approaching safe limit ({Config.SAFE_ARTICLE_LIMIT} articles)")
                    print("   💡 Consider using --max-articles to limit extraction")
                break

            # Check if there are more pages
            continuation = data.get('continuation')
            if not continuation:
                break

            page += 1
            
            # Progressive delay increases as we fetch more articles
            if len(all_articles) >= Config.PROGRESSIVE_DELAY_THRESHOLD:
                delay_multiplier = min(3.0, len(all_articles) / Config.PROGRESSIVE_DELAY_THRESHOLD)
                current_delay = min(Config.MAX_DELAY, options.api_delay * delay_multiplier)
                if not options.quiet and page % 5 == 0:  # Show delay info every 5 pages
                    print(f"   ⏱️  Using {current_delay:.1f}s delay (progressive rate limiting)")
            
            time.sleep(current_delay)  # Be nice to the API

        # Finalize progressive saving
        if progressive_saver:
            progressive_saver.finalize(options.quiet)

        return all_articles
    
    def _get_stream_id(self, user_id: str, category: Optional[str], quiet: bool) -> Optional[str]:
        """Get the appropriate stream ID for fetching articles."""
        if category:
            if not quiet:
                print("📁 Looking for folder...")
            
            found_category = self.client.find_category_by_name(category)
            
            if not found_category:
                print(f"\n❌ Folder '{category}' not found.")
                categories = self.client.get_categories()
                
                if categories:
                    print("\n📁 Available Feedly folders:")
                    for cat in categories:
                        print(f"   - {cat.label}")
                    print("\n💡 Tip: Folder names are case-insensitive and support partial matching")
                else:
                    print("📁 No custom folders found. Create folders in Feedly to organize your feeds.")
                return None

            if not quiet:
                print(f"📂 Using folder: {found_category.label}")
            return found_category.id
        else:
            if not quiet:
                print("🌍 Using all feeds")
            return f"user/{user_id}/category/global.all"
    
    def save_articles(self, articles: List[Article], output_prefix: str, 
                     output_format: str) -> None:
        """Save articles in the specified format(s)."""
        if not articles:
            print("⚠️ No articles to save")
            return

        print(f"\n💾 Saving data...")

        if output_format in ['all', 'csv']:
            FileHandler.save_to_csv(articles, f"{output_prefix}.csv")

        if output_format in ['all', 'json']:
            FileHandler.save_to_json(articles, f"{output_prefix}.json")

        if output_format in ['all', 'urls']:
            FileHandler.save_urls_only(articles, f"{output_prefix}_urls.txt")
    
    def list_categories(self) -> None:
        """List all available Feedly categories/folders."""
        print("📁 Available categories/folders:")
        print("=" * 50)
        categories = self.client.get_categories()
        
        if not categories:
            print("   No custom folders found. Create folders in Feedly to organize your feeds.")
        else:
            print(f"   Found {len(categories)} folder(s):\n")
            for cat in categories:
                print(f"   📂 {cat.label}")
                print(f"      Use: --category \"{cat.label}\"")
                print()
        
        print("💡 Tip: Use --category with the folder name to fetch only from that folder")
        print("💡 Example: python feedly_extractor.py --category \"Tech News\" --days 7")
    
    def print_summary(self, articles: List[Article]) -> None:
        """Print a summary of the extracted articles."""
        if not articles:
            print("📭 No articles found")
            return

        from collections import Counter

        print(f"\n📊 Summary:")
        print(f"   Total articles: {len(articles)}")

        # Unique sources
        sources = [article.source_title for article in articles if article.source_title]
        unique_sources = set(sources)
        print(f"   Unique sources: {len(unique_sources)}")

        # Date range
        dates = [article.published_date for article in articles if article.published_date]
        if dates:
            print(f"   Date range: {min(dates)} to {max(dates)}")

        # Read/unread status
        read_count = sum(1 for article in articles if article.read)
        unread_count = len(articles) - read_count
        print(f"   Read: {read_count}, Unread: {unread_count}")

        # Language distribution
        languages = [article.language for article in articles if article.language]
        if languages:
            lang_counts = Counter(languages)
            print(f"   Languages: {dict(lang_counts)}")

        # Top sources
        if sources:
            top_sources = Counter(sources).most_common(5)
            print(f"\n📈 Top 5 sources:")
            for source, count in top_sources:
                print(f"   {source}: {count} articles")

        # Word count stats
        word_counts = [article.word_count for article in articles if article.word_count > 0]
        if word_counts:
            avg_words = sum(word_counts) / len(word_counts)
            print(f"\n📝 Content stats:")
            print(f"   Average word count: {avg_words:.0f}")
            print(f"   Longest article: {max(word_counts)} words")