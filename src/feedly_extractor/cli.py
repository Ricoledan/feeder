"""Command-line interface for the Feedly Extractor."""

import argparse
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

from .config import Config
from .extractor import ArticleExtractor
from .models import FetchOptions
from .utils import generate_output_filename


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Extract articles from your Feedly feeds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract articles from the past week
  python feedly_extractor.py

  # Extract articles from the past 3 days
  python feedly_extractor.py --days 3

  # Extract articles from a specific date range
  python feedly_extractor.py --start-date 2024-01-01 --end-date 2024-01-07

  # Extract only unread articles
  python feedly_extractor.py --unread-only

  # Extract from a specific category
  python feedly_extractor.py --category "Tech News"

  # Limit to 100 articles and save as JSON only
  python feedly_extractor.py --max-articles 100 --format json

  # Custom output filename
  python feedly_extractor.py --output my_articles
        """
    )

    # Date range options
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--days', '-d',
        type=int,
        default=Config.DEFAULT_DAYS_BACK,
        help=f'Number of days to look back (default: {Config.DEFAULT_DAYS_BACK})'
    )
    date_group.add_argument(
        '--start-date', '-s',
        type=str,
        help='Start date in YYYY-MM-DD format'
    )

    parser.add_argument(
        '--end-date', '-e',
        type=str,
        help='End date in YYYY-MM-DD format (requires --start-date)'
    )

    # Filtering options
    parser.add_argument(
        '--category', '-c',
        type=str,
        help='Filter by Feedly folder/category name (partial match, case-insensitive)'
    )

    parser.add_argument(
        '--unread-only', '-u',
        action='store_true',
        help='Only fetch unread articles'
    )

    parser.add_argument(
        '--max-articles', '-m',
        type=int,
        help='Maximum number of articles to fetch'
    )

    # Output options
    parser.add_argument(
        '--format', '-f',
        choices=['all', 'csv', 'json', 'urls'],
        default='all',
        help='Output format (default: all)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output filename prefix (without extension)'
    )

    # Display options
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )

    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List your Feedly folders and exit'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=Config.API_DELAY,
        help=f'Delay between API requests in seconds (default: {Config.API_DELAY})'
    )

    parser.add_argument(
        '--no-progressive-save',
        action='store_true',
        help='Disable progressive saving (save all at once at the end)'
    )

    return parser


def validate_args(args) -> None:
    """Validate command line arguments."""
    if args.end_date and not args.start_date:
        print("❌ Error: --end-date requires --start-date")
        sys.exit(1)


def main() -> None:
    """Main function to run the CLI"""
    # Load environment variables
    load_dotenv()
    
    parser = create_parser()
    args = parser.parse_args()
    
    validate_args(args)

    try:
        # Validate access token
        access_token = Config.validate_token()
        
        # Initialize extractor
        extractor = ArticleExtractor(access_token)

        # List categories if requested
        if args.list_categories:
            extractor.list_categories()
            return

        # Get articles
        if not args.quiet:
            print("🚀 Starting Feedly Articles Extractor...")

        # Generate output filename prefix
        output_prefix = generate_output_filename(args.output)

        # Create fetch options
        options = FetchOptions(
            days_back=args.days,
            start_date=args.start_date,
            end_date=args.end_date,
            category=args.category,
            unread_only=args.unread_only,
            max_articles=args.max_articles,
            api_delay=args.delay,
            output_prefix=output_prefix,
            output_format=args.format,
            progressive_save=not args.no_progressive_save,
            quiet=args.quiet
        )

        articles = extractor.get_articles(options)

        if not articles:
            print("📭 No articles found for the specified criteria")
            return

        # If progressive save was disabled, save now
        if args.no_progressive_save:
            extractor.save_articles(articles, output_prefix, args.format)

        # Print summary
        if not args.quiet:
            extractor.print_summary(articles)

    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        if "429" in str(e):
            print("❌ Rate limit exceeded. The Feedly API has usage limits.")
            print("💡 Tips to avoid rate limits:")
            print("   - Use smaller date ranges (--days 1 or --days 3)")
            print("   - Limit articles fetched (--max-articles 100)")
            print("   - Wait a few minutes before trying again")
            print("   - Use --category to fetch from specific categories only")
        else:
            print(f"❌ API Error: {e}")
            print("🔍 Check your access token and internet connection")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()