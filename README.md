# Website2MD - Convert Websites to Markdown

A powerful tool that converts websites to markdown format using crawl4ai framework. Perfect for creating LLM-ready content from documentation sites, full websites, or URL lists.

## Features

- 🚀 **Auto-detection**: Automatically detects input type (site/docs/list)
- 📝 **Markdown Output**: Converts web content to clean markdown format
- 🤖 **LLM-Ready**: Optimized for use as LLM context and training data
- 🌐 **JavaScript Support**: Handles modern SPA websites and dynamic content
- 📚 **Documentation Sites**: Specialized crawler for docs with menu expansion
- 📋 **Batch Processing**: Process multiple URLs from files or lists
- ⚡ **High Performance**: Async processing with smart concurrency
- 🎯 **Content Selection**: Advanced CSS selectors and exclude patterns

## Installation

```bash
pip install website2md
```

Or install from source:

```bash
git clone https://github.com/fengyunzaidushi/website2md.git
cd website2md
pip install -e .
```

## Quick Start

### Command Line Usage

```bash
# Auto-detect and convert website to markdown
website2md https://docs.example.com --output ./docs

# Convert full website (auto-detected as 'site' type)
website2md https://example.com --output ./website-content

# Process documentation site (auto-detected as 'docs' type)
website2md https://docs.react.dev --output ./react-docs

# Process URL list from file
website2md urls.txt --type list --output ./batch-content

# Process URL list directly
website2md "url1,url2,url3" --type list --output ./multi-content

# Specify type explicitly
website2md https://example.com --type site --max-pages 50 --output ./results
```

### Python API Usage

```python
from website2md import DocSiteCrawler, URLListCrawler
from website2md.config import CrawlConfig

# Crawl documentation site
config = CrawlConfig(max_pages=100, wait_for_content=True)
crawler = DocSiteCrawler(config, "./output")
results = await crawler.crawl_site("https://docs.example.com")

# Process URL list
url_crawler = URLListCrawler(config, "./output") 
results = await url_crawler.crawl_urls("url1,url2,url3")
```

## Input Types

Website2MD automatically detects input types based on patterns:

- **📄 Site**: Full website crawling (`https://example.com`)
- **📚 Docs**: Documentation sites (`https://docs.example.com`, `/docs/` URLs)  
- **📋 List**: URL files (`.txt` files) or comma-separated URL strings

## Advanced Configuration

### Documentation Sites

```python
from website2md import DocSiteCrawler
from website2md.config import CrawlConfig

config = CrawlConfig(
    max_pages=200,
    wait_for_content=True,    # Enable JavaScript rendering
    js_wait_time=3.0,         # Wait time for JS execution
    expand_menus=True,        # Auto-click expandable menus
    scroll_for_content=True,  # Scroll to trigger lazy loading
    exclude_selectors=[       # Remove navigation elements
        '.sidebar', '.nav', '.breadcrumb', '.toc'
    ],
    timeout=60
)

crawler = DocSiteCrawler(config, "./docs-output")
```

### Batch URL Processing

```python
from website2md import URLFileCrawler

# Process URLs from file
config = CrawlConfig(max_pages=100, headless=True)
crawler = URLFileCrawler(config, "./batch-output")

# From file
results = await crawler.crawl_from_file("urls.txt")

# From list
results = await crawler.crawl_urls(["url1", "url2", "url3"])
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

## Use Cases

- 🤖 **LLM Training Data**: Convert documentation sites to training datasets
- 📚 **Knowledge Bases**: Build markdown knowledge bases from websites  
- 🔍 **Content Migration**: Migrate content from old sites to new platforms
- 📖 **Offline Documentation**: Create offline copies of documentation
- 🎯 **Content Analysis**: Extract and analyze website content at scale

## Requirements

- Python 3.10+
- crawl4ai >= 0.6.0
- aiohttp
- beautifulsoup4
- click

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📦 **PyPI**: [website2md](https://pypi.org/project/website2md/)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/fengyunzaidushi/website2md/wiki)
- 🐛 **Issues**: [GitHub Issues](https://github.com/fengyunzaidushi/website2md/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/fengyunzaidushi/website2md/discussions)