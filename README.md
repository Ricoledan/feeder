# Feeder

A powerful command-line tool to extract articles from your Feedly feeds with flexible filtering, date ranges, and export options.

## Features

- **Flexible Date Ranges**: Extract articles from the past N days or specific date ranges
- **Category Filtering**: Filter by specific Feedly categories/folders
- **Read Status**: Option to fetch only unread articles
- **Article Limits**: Set maximum number of articles to extract
- **Multiple Formats**: Export to CSV, JSON, or plain text URLs
- **CLI Interface**: Full command-line interface with helpful options
- **Secure**: Uses environment variables for API tokens
- **Progressive Saving**: Articles are saved as they're fetched (no data loss on interruption)
- **Modular Architecture**: Clean, maintainable code structure

## Installation

### Option 1: Install as Package (Recommended)
```bash
# Clone the repository
git clone https://github.com/ricoledan/feeder.git
cd feeder

# Install the package
pip install -e .

# Use via CLI
feeder --help
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Use directly
python feedly_extractor.py --help
```

## Configuration

1. **Get Your Feedly Access Token**
   - Go to [https://feedly.com/v3/auth/dev](https://feedly.com/v3/auth/dev)
   - Log in to your Feedly account
   - Copy the access token that appears

2. **Configure Environment Variables**
   ```bash
   # Copy template (if it exists)
   cp .env.template .env
   
   # Or create .env file manually
   echo "FEEDLY_ACCESS_TOKEN=your_actual_token_here" > .env
   ```

## Usage

### Working with Feedly Folders

If you've organized your feeds into folders in Feedly, you can fetch articles from specific folders:

```bash
# List all your Feedly folders
feeder --list-categories

# Fetch from a specific folder (e.g., "Tech News")  
feeder --category "Tech News" --days 7

# Fetch from a folder with partial name matching
feeder --category "tech" --days 7
```

### Basic Examples

```bash
# Extract articles from the past week (default)
feeder

# Extract articles from the past 3 days
feeder --days 3

# Extract only unread articles
feeder --unread-only

# Extract from a specific Feedly folder/category
feeder --category "Tech News"

# List all your Feedly folders
feeder --list-categories

# Limit to 100 articles
feeder --max-articles 100
```

### Date Range Examples

```bash
# Extract articles from a specific date range
feeder --start-date 2024-01-01 --end-date 2024-01-07

# Extract articles from January 1st to now
feeder --start-date 2024-01-01

# Extract articles from the past month
feeder --days 30
```

### Output Format Examples

```bash
# Save only as CSV
feeder --format csv

# Save only as JSON
feeder --format json

# Save only URLs as text file
feeder --format urls

# Custom output filename
feeder --output my_articles
```

### Advanced Examples

```bash
# Quiet mode (no progress output)
feeder --quiet

# List available categories
feeder --list-categories

# Complex query: Tech articles from past 2 weeks, unread only, max 50
feeder --category "Tech" --days 14 --unread-only --max-articles 50 --output tech_backlog
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--days` | `-d` | Number of days to look back (default: 7) |
| `--start-date` | `-s` | Start date in YYYY-MM-DD format |
| `--end-date` | `-e` | End date in YYYY-MM-DD format |
| `--category` | `-c` | Filter by Feedly folder/category name (partial match) |
| `--unread-only` | `-u` | Only fetch unread articles |
| `--max-articles` | `-m` | Maximum number of articles to fetch |
| `--format` | `-f` | Output format: all, csv, json, urls (default: all) |
| `--output` | `-o` | Output filename prefix (without extension) |
| `--quiet` | `-q` | Suppress progress output |
| `--list-categories` | | List your Feedly folders and exit |
| `--help` | `-h` | Show help message |

## Output Files

The tool generates the following files based on your format selection:

- **CSV**: `feedly_articles_YYYYMMDD_HHMMSS.csv` - Full article data in spreadsheet format
- **JSON**: `feedly_articles_YYYYMMDD_HHMMSS.json` - Complete article data in JSON format
- **URLs**: `feedly_articles_YYYYMMDD_HHMMSS_urls.txt` - Plain text file with one URL per line

### CSV Columns

The CSV export includes these columns:

- `id` - Unique article identifier
- `title` - Article title
- `url` - Article URL
- `author` - Article author
- `published_date` - When the article was published
- `crawled_date` - When Feedly discovered the article
- `source_title` - Name of the source feed
- `source_url` - Homepage of the source
- `summary` - Article summary/excerpt
- `content` - Full article content (if available)
- `language` - Article language
- `keywords` - Associated keywords
- `categories` - Feedly categories
- `tags` - User-applied tags
- `read` - Whether you've read the article
- `word_count` - Approximate word count

## Progressive Saving

By default, articles are saved **progressively** as they're fetched, which means:

- ✅ **No data loss** if the script is interrupted
- ✅ **Memory efficient** for large fetches  
- ✅ **Real-time progress** tracking

```bash
# Articles are saved in batches as they're fetched (default behavior)
feeder --days 30 --category "Tech"

# Disable progressive saving (save all at once at the end)
feeder --days 7 --no-progressive-save
```

**Progressive saving output:**
```
📄 Fetching page 1...
✅ Found 250 articles on page 1
💾 Saved batch: 250 articles (total saved: 250)
📄 Fetching page 2...
✅ Found 180 articles on page 2  
💾 Saved batch: 180 articles (total saved: 430)
✅ Progressive save complete: 430 articles saved
📄 CSV: feedly_articles_20241219_143022.csv
📄 JSON: feedly_articles_20241219_143022.json
📄 URLs: feedly_articles_20241219_143022_urls.txt
```

## Error Handling

### Common Issues

**Authentication Error (401)**
```
❌ Authentication failed. Check your access token.
```
- Verify your token in the `.env` file
- Get a new token from [https://feedly.com/v3/auth/dev](https://feedly.com/v3/auth/dev)

**Category Not Found**
```
❌ Category 'Tech News' not found. Available categories:
   - Technology
   - News
   - Business
```
- Use `--list-categories` to see available options
- Category matching is case-insensitive and supports partial matches

**No Articles Found**
```
📭 No articles found for the specified criteria
```
- Try expanding your date range with `--days`
- Remove filters like `--unread-only` or `--category`
- Check if you have any articles in your Feedly

## Tips for NotebookLM Integration

Since you mentioned wanting to use this with NotebookLM, here are some tips:

1. **Use URL format for quick import**:
   ```bash
   feeder --format urls --days 7
   ```

2. **Generate CSV for metadata**:
   ```bash
   feeder --format csv --days 7
   ```
   Then you can manually select interesting articles to add to NotebookLM.

3. **Filter by category for focused research**:
   ```bash
   feeder --category "AI" --days 30 --format urls
   ```

4. **Create a weekly automation**:
   Set up a cron job or scheduled task to run this weekly and save URLs to a consistent location.

## API Rate Limits

The Feedly API has rate limits. The script includes small delays between requests to be respectful. If you encounter rate limiting:

- Use smaller date ranges
- Use `--max-articles` to limit the number of requests
- Wait a few minutes before retrying

## Troubleshooting

### Installation Issues

```bash
# If you have permission issues
pip install --user -r requirements.txt

# If you're using conda
conda install requests python-dotenv

# If you're using Python 3.12+ and have issues
pip install --upgrade requests python-dotenv
```

### Runtime Issues

```bash
# Test your token
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Token loaded:', bool(os.getenv('FEEDLY_ACCESS_TOKEN')))"

# Check available categories
feeder --list-categories

# Run with debug info
feeder --days 1 --max-articles 5
```

## Documentation

- 📖 **[Usage Examples](docs/EXAMPLES.md)** - Comprehensive examples and workflows
- 🏗️ **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical details and design decisions

## Contributing

This project uses a modular architecture for easy maintenance and extension. See the [Architecture Guide](docs/ARCHITECTURE.md) for details on the codebase structure.

## License

MIT License - feel free to use and modify as needed.