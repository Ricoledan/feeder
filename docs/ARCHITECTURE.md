# Project Architecture

This document describes the modular architecture of Feeder.

## Project Structure

```
feeder/
├── src/
│   └── feedly_extractor/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── client.py            # Feedly API client
│       ├── config.py            # Configuration and constants
│       ├── extractor.py         # Main extraction logic
│       ├── file_handlers.py     # File I/O operations
│       ├── models.py            # Data models and structures
│       └── utils.py             # Utility functions
├── feedly_extractor.py          # Main entry point
├── setup.py                     # Package setup configuration
├── requirements.txt             # Dependencies
├── README.md                    # Main documentation
├── EXAMPLES.md                  # Usage examples
└── ARCHITECTURE.md              # This file
```

## Module Responsibilities

### `cli.py` - Command Line Interface
- Argument parsing with `argparse`
- Input validation
- Error handling for user-facing errors
- Main entry point coordination

### `client.py` - Feedly API Client
- HTTP session management with retry logic
- API authentication
- Rate limiting handling
- Low-level API calls to Feedly endpoints

### `config.py` - Configuration Management
- Application constants and settings
- Environment variable handling
- Token validation
- Centralized configuration access

### `extractor.py` - Main Extraction Logic
- High-level article fetching workflow
- Progressive saving coordination
- Category/folder filtering
- Summary generation

### `file_handlers.py` - File Operations
- CSV, JSON, and URL file exports
- Progressive saving implementation
- Batch writing operations
- File format management

### `models.py` - Data Models
- `Article` dataclass for article representation
- `Category` dataclass for Feedly folders
- `FetchOptions` dataclass for request parameters
- Data transformation methods

### `utils.py` - Utility Functions
- HTML content cleaning
- Date/timestamp conversions
- Date range validation
- Common helper functions

## Design Principles

### Separation of Concerns
Each module has a single, well-defined responsibility:
- **API communication** is isolated in `client.py`
- **File operations** are centralized in `file_handlers.py`
- **Business logic** is in `extractor.py`
- **User interface** is in `cli.py`

### Data Flow
1. **CLI** parses arguments and creates `FetchOptions`
2. **Extractor** coordinates the overall process
3. **Client** handles API communication
4. **Models** represent data throughout the pipeline
5. **FileHandlers** manage output formatting and saving

### Error Handling
- **Network errors** are handled in `client.py`
- **Validation errors** are handled in `cli.py` and `utils.py`
- **Business logic errors** are handled in `extractor.py`

### Progressive Saving
The `ProgressiveSaver` class in `file_handlers.py` provides:
- Real-time saving as articles are fetched
- Protection against data loss on interruption
- Support for multiple output formats simultaneously

## Benefits of This Architecture

### Maintainability
- Each module can be modified independently
- Clear boundaries between concerns
- Easy to add new features or output formats

### Testability
- Individual modules can be unit tested in isolation
- Mock dependencies for reliable testing
- Clear interfaces between components

### Extensibility
- Easy to add new output formats in `file_handlers.py`
- Simple to add new API endpoints in `client.py`
- Straightforward to extend CLI options in `cli.py`

### Reusability
- Core logic can be imported as a library
- Individual components can be used in other projects
- Clean API for programmatic use

## Usage as a Library

```python
from feedly_extractor import ArticleExtractor, Config, FetchOptions

# Initialize
token = Config.validate_token()
extractor = ArticleExtractor(token)

# Configure fetch
options = FetchOptions(
    days_back=7,
    category="Tech News",
    max_articles=100
)

# Get articles
articles = extractor.get_articles(options)

# Process articles
for article in articles:
    print(f"{article.title}: {article.url}")
```

## Performance Considerations

### Rate Limiting
- Configurable delays between API requests
- Automatic retry with exponential backoff
- Batch processing to minimize API calls

### Memory Usage
- Progressive saving reduces memory footprint
- Streaming file writes for large datasets
- Lazy evaluation where possible

### I/O Efficiency
- Batch file operations
- Buffered writes for better performance
- Minimal file reopening

## Future Enhancements

### Planned Features
- Database storage support
- Parallel fetching for multiple categories
- Resume capability for interrupted downloads
- Web interface option

### Extension Points
- New output formats (PDF, EPUB, etc.)
- Additional data sources beyond Feedly
- Custom filtering and processing plugins
- Integration with other tools (NotebookLM, etc.)