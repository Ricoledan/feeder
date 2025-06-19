# Feedly Extractor Examples

## Working with Feedly Folders

### List Your Folders
First, see what folders you have in Feedly:
```bash
python feedly_extractor.py --list-categories
```

Output example:
```
📁 Available categories/folders:
==================================================
   Found 3 folder(s):

   📂 Tech News
      Use: --category "Tech News"

   📂 AI Research
      Use: --category "AI Research"

   📂 Business
      Use: --category "Business"

💡 Tip: Use --category with the folder name to fetch only from that folder
💡 Example: python feedly_extractor.py --category "Tech News" --days 7
```

### Fetch from a Specific Folder
```bash
# Exact folder name
python feedly_extractor.py --category "Tech News" --days 7

# Partial matching also works
python feedly_extractor.py --category "tech" --days 7

# Case-insensitive
python feedly_extractor.py --category "TECH NEWS" --days 7
```

### Folder-Specific Workflows

#### Daily AI Research Digest
```bash
# Get yesterday's AI papers and articles
python feedly_extractor.py --category "AI Research" --days 1 --format urls --output ai_daily
```

#### Weekly Tech Newsletter Prep
```bash
# Get unread tech articles from the past week
python feedly_extractor.py --category "Tech News" --days 7 --unread-only --format csv
```

#### Business News Archive
```bash
# Archive last month's business articles
python feedly_extractor.py --category "Business" --days 30 --format json --output business_archive_$(date +%Y%m)
```

## Rate Limit Friendly Examples

### Conservative Fetching
```bash
# Fetch with longer delays to avoid rate limits
python feedly_extractor.py --category "Tech" --days 7 --delay 1.0 --max-articles 200
```

### Incremental Daily Fetching
Instead of fetching 30 days at once, fetch daily:
```bash
# Day 1
python feedly_extractor.py --days 1 --output articles_day1

# Day 2 
python feedly_extractor.py --days 1 --output articles_day2
```

## NotebookLM Integration

### Best Practices for NotebookLM
```bash
# 1. Export URLs only for easy import
python feedly_extractor.py --category "AI Research" --days 7 --format urls

# 2. Focus on high-quality sources
python feedly_extractor.py --category "Academic Papers" --days 30 --format urls --max-articles 50

# 3. Create topic-specific collections
python feedly_extractor.py --category "Machine Learning" --unread-only --format urls --output ml_collection
```

## Advanced Filtering

### Date Range Queries
```bash
# Specific date range
python feedly_extractor.py --start-date 2024-01-01 --end-date 2024-01-31 --category "Tech"

# From a specific date to today
python feedly_extractor.py --start-date 2024-01-15 --category "News"
```

### Combining Filters
```bash
# Unread tech articles from the past 3 days, max 100
python feedly_extractor.py --category "Tech" --days 3 --unread-only --max-articles 100 --format csv
```

## Automation Examples

### Cron Job for Daily Digest
```bash
# Add to crontab: crontab -e
# Run every day at 8 AM
0 8 * * * cd /path/to/feedly-extractor && python feedly_extractor.py --category "Tech" --days 1 --format urls --output ~/daily_digest/tech_$(date +\%Y\%m\%d)
```

### Shell Script for Multiple Folders
```bash
#!/bin/bash
# fetch_all_folders.sh

FOLDERS=("Tech News" "AI Research" "Business" "Science")
DAYS=7

for folder in "${FOLDERS[@]}"; do
    echo "Fetching from $folder..."
    python feedly_extractor.py --category "$folder" --days $DAYS --format csv --output "${folder// /_}_export"
    sleep 5  # Be nice to the API
done
```

## Troubleshooting

### Rate Limit Issues
```bash
# If you hit rate limits, try:
# 1. Smaller batches
python feedly_extractor.py --max-articles 100

# 2. Longer delays
python feedly_extractor.py --delay 2.0

# 3. Specific folders instead of all feeds
python feedly_extractor.py --category "Tech" --days 3
```

### No Articles Found
```bash
# Check if you have unread articles
python feedly_extractor.py --days 30

# Remove the unread filter
python feedly_extractor.py --category "Tech" --days 7
# (without --unread-only)
```