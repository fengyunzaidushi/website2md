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

# Crawl documentation site with content filtering
config = CrawlConfig(
    max_pages=100, 
    wait_for_content=True,
    exclude_selectors=["#navigation-items", ".sidebar", ".advertisement"]
)
crawler = DocSiteCrawler(config)
results = await crawler.crawl_documentation_site("https://docs.example.com", "./output")

# Process URL list
url_crawler = URLListCrawler(config)
results = await url_crawler.crawl_url_list("url1,url2,url3", "./output")
```

### 📝 Python Examples

Check out the [`examples/`](examples/) directory for comprehensive Python usage examples:

- **[crawl_cursor_docs.py](examples/crawl_cursor_docs.py)** - Crawl Cursor docs excluding `#navigation-items`
- **[crawl_anthropic_docs.py](examples/crawl_anthropic_docs.py)** - Crawl Anthropic docs with default excludes
- **[basic_site_crawling.py](examples/basic_site_crawling.py)** - News, blog, e-commerce filtering
- **[advanced_filtering.py](examples/advanced_filtering.py)** - Advanced CSS selector techniques

See [examples/README.md](examples/README.md) for detailed usage instructions and best practices.

## 💡 Best Practices & Troubleshooting

### URL Discovery Optimization

For complex documentation sites or sites with dynamic content, you may get better results by explicitly specifying the crawler type:

```bash
# If auto-detection gives poor results, try 'site' type for better URL discovery
website2md https://docs.cursor.com/en/welcome --type site --output ./docs

# The 'site' type uses recursive link discovery, often finding more pages
# than the 'docs' type which relies on menu expansion
```

### Common Issues and Solutions

#### Issue: Only 1 page crawled instead of full site
**Symptom**: Expected many pages but only got the starting page.

**Solutions**:
1. **Use `--type site`** for better URL discovery:
   ```bash
   website2md https://docs.example.com --type site --output ./docs
   ```

2. **Check if JavaScript is required**: Some sites need JS rendering
   ```bash
   website2md https://spa-site.com --type site --output ./docs
   ```

#### Issue: Content contains too much navigation/clutter
**Symptom**: Generated markdown files contain sidebars, navigation menus, ads.

**Solutions**:
1. **Use exclude selectors** to filter unwanted content:
   ```bash
   website2md https://example.com --exclude-selectors "nav,aside,header,footer,.ads" --output ./clean
   ```

2. **For documentation sites**, try these common selectors:
   ```bash
   website2md https://docs.site.com --exclude-selectors ".sidebar,.navigation,.toc,.breadcrumb" --output ./docs
   ```

#### Issue: Windows encoding errors (GBK codec)
**Symptom**: `'gbk' codec can't encode character` errors.

**Solution**: Set UTF-8 encoding:
```bash
# Windows Command Prompt
set PYTHONIOENCODING=utf-8 && website2md https://example.com --output ./docs

# PowerShell
$env:PYTHONIOENCODING="utf-8"; website2md https://example.com --output ./docs
```

#### Issue: Empty or missing content
**Symptom**: Generated files are empty or missing expected content.

**Solutions**:
1. **Increase timeout** for slow sites:
   ```bash
   website2md https://slow-site.com --type site --output ./docs
   ```

2. **Check if playwright browsers are installed**:
   ```bash
   playwright install
   ```

### Performance Tips

- **Start small**: Use `--max-pages` to test before full crawls
- **Use appropriate delays**: Add `--delay` for rate limiting
- **Monitor output**: Use `--verbose` to see what's happening
- **Choose the right type**: `site` for comprehensive, `docs` for structured

### Type Selection Guide

| Site Type | Use `--type site` when | Use `--type docs` when |
|-----------|------------------------|------------------------|
| Documentation | Complex navigation, SPA-style docs | Traditional docs with clear menu structure |
| Corporate sites | Marketing sites, blogs | API docs, help centers |
| E-commerce | Product catalogs | Knowledge bases |
| News sites | Article listing pages | FAQ sections |

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

## Content Filtering (New in v0.1.7)

Website2MD supports powerful content filtering using CSS selectors to exclude unwanted elements from the crawled content.

### Basic CSS Selector Syntax

#### ID Selectors
Use `#` to target elements by ID:
```bash
# Exclude div with id="navigation-items"
website2md https://example.com --exclude-selectors "#navigation-items"

# Exclude header with id="main-header" 
website2md https://example.com --exclude-selectors "#main-header"
```

#### Class Selectors
Use `.` to target elements by class:
```bash
# Exclude elements with class="sidebar"
website2md https://example.com --exclude-selectors ".sidebar"

# Exclude multiple classes
website2md https://example.com --exclude-selectors ".advertisement,.popup,.cookie-banner"
```

#### Tag Selectors
Target HTML tags directly:
```bash
# Exclude all nav elements
website2md https://example.com --exclude-selectors "nav"

# Exclude headers and footers
website2md https://example.com --exclude-selectors "header,footer"
```

### Advanced Selector Examples

#### Attribute Selectors
```bash
# Exclude elements with specific attributes
website2md https://example.com --exclude-selectors "[data-testid='navigation']"

# Exclude elements with specific attribute values
website2md https://example.com --exclude-selectors "[role='banner']"
```

#### Descendant Selectors
```bash
# Exclude navigation menus inside header
website2md https://example.com --exclude-selectors "#header .navigation-menu"

# Exclude all divs inside sidebar
website2md https://example.com --exclude-selectors ".sidebar div"
```

#### Complex Combinations
```bash
# Comprehensive content filtering
website2md https://example.com \
  --exclude-selectors "#navigation-items,.sidebar,nav,.advertisement,[data-testid='footer']" \
  --output ./clean-content
```

### Common Use Cases

#### Remove Website Navigation
```bash
website2md https://example.com \
  --exclude-selectors "#navigation,nav,.navbar,.menu" \
  --output ./content-only
```

#### Clean Documentation Sites
```bash
website2md https://docs.example.com \
  --type docs \
  --exclude-selectors ".toc,.breadcrumb,#sidebar,.docs-navigation" \
  --output ./clean-docs
```

#### Filter Marketing Content
```bash
website2md https://blog.example.com \
  --exclude-selectors ".advertisement,.cta-banner,.newsletter-signup,.social-share" \
  --output ./articles-only
```

#### E-commerce Content Extraction
```bash
website2md https://shop.example.com \
  --exclude-selectors ".price,.buy-button,.cart,.recommendations" \
  --output ./product-info
```

### Smart Documentation Filtering

For `--type docs`, user-specified selectors are automatically combined with default documentation site filters:

**Default Documentation Excludes:**
- `.sidebar`, `.nav`, `.navigation`, `#sidebar`
- `#starlight__sidebar`, `.docs-sidebar`, `.theme-doc-sidebar-container`
- `.header`, `.footer`, `.breadcrumb`, `.toc`
- `.border-r-border`, `.md\\:w-64`, `.xl\\:w-72`

**Example with Smart Merging:**
```bash
# Your selectors are added to the defaults
website2md https://docs.example.com \
  --type docs \
  --exclude-selectors "#custom-banner,.advertisement" \
  --output ./clean-docs
```

### Tips for Effective Filtering

1. **Inspect Element**: Use browser developer tools to identify element selectors
2. **Test Selectors**: Start with simple selectors and add complexity gradually
3. **Multiple Passes**: Use `--verbose` to see what's being excluded
4. **Verify Results**: Check the output files to ensure desired content remains

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
