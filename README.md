# Website2MD - Convert Websites to Markdown

A sophisticated web crawler that converts websites to markdown format using crawl4ai framework. Specializes in creating LLM-ready content from documentation sites, full websites, or URL lists with advanced JavaScript rendering and intelligent content selection.

## 📋 项目概述

Website2MD 是一个强大的网站内容抓取和转换工具，专门用于将网站内容转换为高质量的 Markdown 格式。特别适合：

- 🤖 **AI/LLM 训练数据准备**：将文档网站转换为训练数据集
- 📚 **知识库构建**：从网站批量提取内容构建知识库  
- 🔍 **内容迁移**：将旧网站内容迁移到新平台
- 📖 **离线文档**：创建文档的离线副本

## Features

- 🚀 **Auto-detection**: Automatically detects input type (site/docs/list)
- 📝 **Markdown Output**: Converts web content to clean markdown format
- 🤖 **LLM-Ready**: Optimized for use as LLM context and training data
- 🌐 **JavaScript Support**: Handles modern SPA websites and dynamic content
- 📚 **Documentation Sites**: Specialized crawler for docs with menu expansion
- 📋 **Batch Processing**: Process multiple URLs from files or lists
- ⚡ **High Performance**: Async processing with smart concurrency
- 🎯 **Content Selection**: Advanced CSS selectors and exclude patterns
- 🔒 **Precise Domain Filtering**: Only crawl exact same subdomain by default, with flexible domain control
- 🚫 **Content Filtering**: Exclude unwanted elements using CSS selectors (ads, popups, navigation, etc.)

## Installation

### Using pip (PyPI)

```bash
pip install website2md
```

### Using uv (Recommended for faster installation)

```bash
# Install from PyPI with Chinese mirror for faster speed
uv pip install website2md --default-index https://mirrors.aliyun.com/pypi/simple

# Or use Tsinghua mirror
uv pip install website2md --default-index https://pypi.tuna.tsinghua.edu.cn/simple
```

### From Source (Development)

```bash
git clone https://github.com/fengyunzaidushi/website2md.git
cd website2md

# Using uv (recommended)
uv venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac
uv sync --default-index https://mirrors.aliyun.com/pypi/simple

# Or using pip
pip install -e .
```

### Browser Setup (Required for JavaScript sites)

After installation, install Playwright browsers:

```bash
playwright install
```

## Quick Start

### Command Line Usage

```bash
# Auto-detect and convert website to markdown
website2md https://docs.example.com --output ./docs

# Convert documentation site (auto-detected as 'docs' type)
website2md https://docs.cursor.com --output ./cursor-docs --verbose

# Convert full website (auto-detected as 'site' type)  
website2md https://example.com --output ./website-content

# Process URL list from file
website2md urls.txt --type list --output ./batch-content

# Process URL list directly
website2md "url1,url2,url3" --type list --output ./multi-content

# Specify type explicitly with custom settings
website2md https://example.com --type site --max-pages 50 --output ./results

# Domain filtering: Only crawl exact same subdomain (default behavior)
website2md https://docs.anthropic.com/zh-CN/docs --output ./docs

# Allow additional specific domains
website2md https://docs.anthropic.com/zh-CN/docs \
  --allowed-domains "console.anthropic.com,api.anthropic.com" \
  --output ./docs

# Allow all external domains (use with caution)
website2md https://docs.anthropic.com/zh-CN/docs \
  --allow-external \
  --output ./docs

# Content filtering: Exclude unwanted elements using CSS selectors
website2md https://example.com \
  --exclude-selectors ".advertisement,.popup,.cookie-banner" \
  --output ./clean-content

# Combine multiple options for precise control
website2md https://docs.example.com \
  --type docs \
  --exclude-selectors "nav,.sidebar,.toc" \
  --max-pages 20 \
  --output ./docs

# Windows users: Use UTF-8 encoding to avoid codec errors
PYTHONIOENCODING=utf-8 website2md https://docs.example.com --output ./docs
```

### Python API Usage

```python
from website2md.doc_crawler import DocSiteCrawler
from website2md.url_list_crawler import URLListCrawler
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

## Domain Filtering (New in v0.1.5)

Website2MD now provides precise domain control to ensure you only crawl relevant content:

### Default Behavior: Exact Subdomain Matching
- Input: `https://docs.anthropic.com/zh-CN/docs`
- Only crawls: `docs.anthropic.com` domain
- Skips: `console.anthropic.com`, `www.anthropic.com`, etc.

### Flexible Domain Control
```bash
# Include specific additional domains
--allowed-domains "console.anthropic.com,api.anthropic.com"

# Allow all external domains (use with caution)
--allow-external
```

### Benefits
- **Focused Content**: Only get relevant documentation pages
- **No Pollution**: Avoid unrelated external links
- **Better Performance**: Fewer unnecessary requests
- **Quality Control**: Cleaner, more relevant output

## Advanced Configuration

### Documentation Sites

```python
from website2md.doc_crawler import DocSiteCrawler
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
from website2md.url_file_crawler import URLFileCrawler

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

## ⚙️ Technical Requirements

### System Requirements
- **Python**: 3.10+ (recommended: 3.11 or 3.12)
- **Operating System**: Windows, macOS, Linux
- **Memory**: 2GB+ RAM (4GB+ for large sites)
- **Browser**: Chromium/Firefox (auto-installed via Playwright)

### Core Dependencies
- **crawl4ai** >= 0.6.0 - Web crawling framework with browser automation
- **aiohttp** - Async HTTP client for concurrent requests
- **beautifulsoup4** - HTML parsing and content extraction
- **click** - Command-line interface framework
- **playwright** - Browser automation for JavaScript rendering

### Development Tools (Optional)
- **uv** - Fast Python package manager (recommended)
- **black** - Code formatting
- **flake8** - Code linting  
- **mypy** - Type checking

## 🛠️ Development & Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/fengyunzaidushi/website2md.git
cd website2md

# Setup development environment with uv (recommended)
uv venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# Install with development dependencies
uv sync --default-index https://mirrors.aliyun.com/pypi/simple

# Install Playwright browsers
playwright install

# Run development checks
black website2md/          # Format code
flake8 website2md/         # Lint code  
mypy website2md/           # Type check
```

### Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes following code style guidelines
4. **Test** your changes with real websites
5. **Submit** a pull request with clear description

### Testing Your Changes

```bash
# Test CLI with various site types
PYTHONIOENCODING=utf-8 website2md https://docs.cursor.com --output ./test-output --verbose
website2md https://example.com --output ./test-site --max-pages 5
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📦 **PyPI**: [website2md](https://pypi.org/project/website2md/)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/fengyunzaidushi/website2md/wiki)
- 🐛 **Issues**: [GitHub Issues](https://github.com/fengyunzaidushi/website2md/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/fengyunzaidushi/website2md/discussions)
