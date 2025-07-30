# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Website2MD is a sophisticated web crawler that converts websites to markdown format using crawl4ai v0.6.x. The project specializes in creating LLM-ready content from documentation sites, full websites, or URL lists with advanced features like JavaScript rendering, dynamic menu expansion, and intelligent content selection.

## Core Architecture

### Multi-Crawler System
The project implements a modular crawler architecture with specialized crawlers for different use cases:

- **WebCrawler** (`website2md/crawler.py`): Basic general-purpose web crawler
- **DocSiteCrawler** (`website2md/doc_crawler.py`): Specialized for documentation sites with dynamic menu expansion and content selection  
- **URLFileCrawler** (`website2md/url_file_crawler.py`): Batch processing from URL files with deduplication
- **URLListCrawler** (`website2md/url_list_crawler.py`): Direct URL list processing with flexible input formats

### Simplified CLI Interface
The CLI (`website2md/cli.py`) provides a simplified interface with automatic input type detection:
- **Auto-detection**: Automatically detects input type (site/docs/list) based on patterns
- **Minimal parameters**: Only requires input source and output directory
- **Smart crawler selection**: Automatically selects appropriate crawler based on input type

### Configuration System
Centralized configuration through `CrawlConfig` class (`website2md/config.py`) supports:
- JavaScript rendering settings for SPA sites (wait_for_content, js_wait_time, scroll_for_content, expand_menus)
- Content selection via CSS selectors and exclude patterns
- Performance tuning (concurrency, delays, timeouts)  
- Browser automation settings for crawl4ai v0.6.x

## Project Structure & Integration Points

### Core Module Dependencies
```
website2md/
├── cli.py              # CLI entry point, auto-detection logic
├── config.py           # CrawlConfig class, shared configuration
├── crawler.py          # Base WebCrawler class
├── doc_crawler.py      # DocSiteCrawler, extends base crawler
├── url_file_crawler.py # URLFileCrawler, batch file processing  
├── url_list_crawler.py # URLListCrawler, direct URL list processing
└── utils.py            # Shared utilities and helpers
```

### Crawler Class Hierarchy
- **Base**: `WebCrawler` provides core crawling functionality
- **Specialized**: `DocSiteCrawler` adds menu expansion and site mapping
- **Batch**: `URLFileCrawler` and `URLListCrawler` handle multiple URL processing
- **CLI Integration**: All crawlers accept `CrawlConfig` and implement standard interface

### Key Integration Patterns
- **Constructor Pattern**: `crawler = CrawlerClass(config)` + `crawler.method(input, output_dir)`
- **Configuration Flow**: CLI → CrawlConfig → Crawler classes → crawl4ai
- **Output Standardization**: All crawlers generate markdown files + `_crawl_summary.json`

## Development Commands

### Installation & Setup
```bash
# Install from source
pip install -e .

# CLI installation check
website2md --help

# Test CLI with different input types
website2md https://docs.example.com --output ./docs
python -m website2md https://example.com --output ./site
```

### Building & Publishing
```bash
# Build package
python -m build

# Upload to PyPI (requires configured ~/.pypirc)
python -m twine upload dist/website2md-*.tar.gz dist/website2md-*.whl

# Clean build artifacts
rm -rf dist/* build/* *.egg-info
```

### Development Environment Setup
```bash
# Create virtual environment with uv (recommended)
uv venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# Install in development mode
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Testing & Quality Assurance
```bash
# Run code formatting
black website2md/

# Run linting
flake8 website2md/

# Run type checking
mypy website2md/

# Test CLI functionality with real sites
PYTHONIOENCODING=utf-8 website2md https://docs.cursor.com/en/get-started/concepts --output ./test_output --verbose
website2md https://docs.astral.sh/uv --output ./uv_docs --verbose
website2md urls.txt --type list --output ./batch_content
```

## Technology Stack & Dependencies

- **Python 3.10+** with asyncio for concurrent crawling
- **crawl4ai v0.6.x** - Modern web crawling with browser automation
- **Click** - CLI framework with simplified interface
- **BeautifulSoup4 & lxml** - HTML parsing
- **aiohttp** - Async HTTP client
- **Chromium/Firefox** - Browser engines for JavaScript rendering

## JavaScript SPA Support

### Configuration for SPA Sites
```python
config = CrawlConfig(
    # JavaScript rendering settings
    wait_for_content=True,     # Enable JS content waiting
    js_wait_time=3.0,         # Wait time for JS execution  
    scroll_for_content=True,   # Auto-scroll for lazy loading
    expand_menus=True,        # Click expandable elements
    
    # Content selection for complex layouts
    exclude_selectors=[        # Remove navigation clutter
        ".sidebar", ".nav", ".navigation", "#sidebar",
        "#starlight__sidebar", ".docs-sidebar", ".theme-doc-sidebar-container",
        ".header", ".footer", ".breadcrumb", ".toc"
    ],
    headless=True,
    timeout=60
)
```

### SPA Crawling Process  
1. **Page load**: Initial HTML fetch with browser automation
2. **JS execution**: Custom JavaScript for scrolling and menu expansion
3. **Content waiting**: Configurable delay for dynamic content loading
4. **Selector application**: CSS selectors applied after JS execution
5. **Content extraction**: Clean markdown with navigation removed

## CLI Input Types & Auto-Detection

### Input Type Detection Logic
The CLI automatically detects input types based on patterns:

- **Site**: Full website crawling (`https://example.com`)
- **Docs**: Documentation sites (`https://docs.example.com`, `/docs/` URLs)  
- **List**: URL files (`.txt` files) or comma-separated URL strings

### Crawler Method Mapping
```python
# DocSiteCrawler
crawler.crawl_documentation_site(url, output_dir)

# URLFileCrawler  
crawler.crawl_urls_from_file(file_path, output_dir)

# URLListCrawler
crawler.crawl_url_list(url_input, output_dir)
```

## Content Selection Strategy

### Exclude-First Approach (Recommended)
Instead of targeting specific content selectors, use comprehensive exclude patterns:
```python
exclude_selectors = [
    # Sidebars and navigation
    ".sidebar", ".nav", ".navigation", "#sidebar",
    
    # Documentation-specific
    "#starlight__sidebar", ".docs-sidebar", ".theme-doc-sidebar-container",
    
    # Layout elements
    ".header", ".footer", ".breadcrumb", ".toc",
    
    # Site-specific patterns
    ".border-r-border", ".md\\:w-64", ".xl\\:w-72"
]
```

### Dynamic Content Discovery
The `extract_sitemap_from_page` method implements:
1. **Multi-round menu expansion**: Clicks expandable elements iteratively
2. **JSON navigation extraction**: Parses JavaScript navigation data
3. **Session persistence**: Maintains browser state across interactions
4. **Comprehensive URL patterns**: Discovers 150+ URLs vs 28 with basic methods

## Migration Notes (crawl4ai v0.5.x → v0.6.x)

### Breaking Changes Handled
- `LocalSeleniumCrawlerStrategy` → `BrowserConfig`/`CrawlerRunConfig`
- `include_raw_html` parameter removed
- `bypass_cache` → `cache_mode=CacheMode.BYPASS`
- Updated import paths: `from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode`

### Configuration Updates
```python
# v0.6.x configuration
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

browser_config = BrowserConfig(browser_type="chromium", headless=True)
crawl_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    css_selector=content_selector,
    excluded_selector=exclude_selector,
    js_code=javascript_code,
    delay_before_return_html=wait_time
)
```

## Output Structure

All content is saved as individual markdown files in the specified output directory:
```
output/
├── page1.md
├── page2.md
├── subdir/
│   ├── page3.md
│   └── page4.md
└── crawl_summary.json
```

Each markdown file contains:
- Clean, LLM-ready content
- Preserved formatting and structure  
- Metadata headers (title, URL, timestamp)

## Common Troubleshooting

### Windows Encoding Issues (GBK Codec Errors)
- **Symptom**: `'gbk' codec can't encode character` errors during crawling
- **Solution**: Set UTF-8 encoding before running CLI commands:
  ```bash
  PYTHONIOENCODING=utf-8 website2md [url] --output [dir]
  ```
- **Root Cause**: Windows console default encoding conflicts with Unicode characters in content

### Playwright Browser Installation
- **Symptom**: `Executable doesn't exist` errors when crawling JavaScript sites
- **Solution**: Install Playwright browsers after package installation:
  ```bash
  playwright install
  ```
- **Note**: Required for JavaScript rendering and SPA site crawling

### JavaScript Sites Returning "Loading..."
- **Cause**: SPA sites require JavaScript execution
- **Solution**: Enable `wait_for_content=True` and `js_wait_time=3.0+`
- **Configuration**: Ensure proper SPA settings in CrawlConfig

### Missing Navigation URLs
- **Cause**: Expandable menus not clicked during discovery
- **Solution**: Set `expand_menus=True` and increase `timeout` to 60+ seconds
- **Debug**: Use `headless=False` during development to observe menu expansion

### CLI Constructor Errors
- **Cause**: Mismatched constructor parameters between CLI and crawler classes
- **Solution**: Ensure crawler constructors only receive `config` parameter, pass `output_dir` to crawler methods
- **Pattern**: `crawler = DocSiteCrawler(config)` then `crawler.crawl_documentation_site(url, output_dir)`

### Performance Issues with Large Sites
- **Tuning**: Adjust `max_concurrent_requests` (3-5 for respectful crawling)
- **Delays**: Set appropriate `delay` between requests (1.0+ seconds)
- **Timeouts**: Increase `timeout` for JavaScript-heavy sites (30-60 seconds)
- **Resume**: Use skip existing files functionality for interrupted crawls