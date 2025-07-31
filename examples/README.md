# Website2MD Python Examples

This directory contains comprehensive Python examples demonstrating how to use Website2MD programmatically with various content filtering strategies.

## 📁 Available Examples

### 1. **crawl_cursor_docs.py**
- **Purpose**: Crawl Cursor documentation site excluding navigation
- **URL**: `https://docs.cursor.com/en/welcome`
- **Excludes**: `#navigation-items`
- **Features**: 
  - Documentation site crawling
  - Single specific element exclusion
  - Comprehensive error handling
  - Progress reporting

### 2. **crawl_anthropic_docs.py**
- **Purpose**: Crawl Anthropic Claude Code docs with default excludes
- **URL**: `https://docs.anthropic.com/zh-CN/docs/claude-code/cli-reference`
- **Excludes**: Default documentation site selectors
- **Features**:
  - Default comprehensive filtering
  - Custom selectors addition example
  - Two different approaches comparison
  - Chinese content handling

### 3. **basic_site_crawling.py**
- **Purpose**: Basic site crawling with content filtering
- **Features**:
  - News site crawling (ads, navigation exclusion)
  - Blog crawling (marketing content exclusion)
  - E-commerce crawling (pricing, cart exclusion)
  - Domain-specific filtering strategies

### 4. **advanced_filtering.py**
- **Purpose**: Advanced CSS selector techniques
- **Features**:
  - Attribute-based filtering
  - Descendant and child selectors
  - Pseudo-selectors usage
  - Real-world complex filtering scenarios

## 🚀 How to Run Examples

### Prerequisites
```bash
# Install website2md
pip install website2md

# Or install from source
pip install -e .

# Install Playwright browsers (required for JavaScript sites)
playwright install
```

### Running Individual Examples
```bash
# Run specific example
python examples/crawl_cursor_docs.py

# Run with UTF-8 encoding (Windows)
PYTHONIOENCODING=utf-8 python examples/crawl_cursor_docs.py
```

### Running All Examples
```bash
# Run all basic examples
python examples/basic_site_crawling.py

# Run all advanced examples
python examples/advanced_filtering.py
```

## 🎯 Key Concepts Demonstrated

### 1. **Basic Configuration**
```python
from website2md.config import CrawlConfig

config = CrawlConfig(
    max_pages=50,
    wait_for_content=True,
    exclude_selectors=["#navigation", ".sidebar"],
    timeout=60
)
```

### 2. **Documentation Site Crawling**
```python
from website2md.doc_crawler import DocSiteCrawler

crawler = DocSiteCrawler(config)
results = await crawler.crawl_documentation_site(url, output_dir)
```

### 3. **General Site Crawling**
```python
from website2md.crawler import WebCrawler

crawler = WebCrawler(config)
results = await crawler.crawl(url)
```

### 4. **Content Filtering Strategies**

#### By Element Type
```python
exclude_selectors = [
    "nav",           # All navigation elements
    "header",        # All headers
    "footer",        # All footers
    "aside"          # All sidebars
]
```

#### By ID
```python
exclude_selectors = [
    "#navigation-items",    # Specific navigation
    "#sidebar",            # Specific sidebar
    "#advertisement"       # Specific ads
]
```

#### By Class
```python
exclude_selectors = [
    ".advertisement",      # Ad containers
    ".social-share",       # Share buttons
    ".newsletter-signup"   # Newsletter forms
]
```

#### By Attributes
```python
exclude_selectors = [
    "[data-testid='ad']",           # Test ID attributes
    "[role='banner']",              # ARIA roles
    "[class*='tracking']"           # Partial class matching
]
```

#### Complex Combinations
```python
exclude_selectors = [
    "#header nav",                  # Nav inside header
    ".sidebar > .widget",           # Direct widget children
    "[data-component='ad'][class*='banner']"  # Multiple attributes
]
```

## 📊 Example Output Structure

Each example creates an output directory with:
```
output_directory/
├── page1.md                    # Individual page content
├── page2.md
├── subdirectory/
│   ├── page3.md
│   └── page4.md
└── _crawl_summary.json         # Crawl statistics and metadata
```

## 🛠️ Customization Tips

### 1. **Adjusting for Your Site**
- Replace example URLs with your target sites
- Inspect elements using browser dev tools
- Test selectors in browser console first
- Start with small `max_pages` for testing

### 2. **Performance Tuning**
```python
config = CrawlConfig(
    delay=2.0,                     # Respectful crawling
    max_concurrent_requests=2,     # Limit concurrent requests
    timeout=60,                    # Adjust for slow sites
    headless=True                  # Faster execution
)
```

### 3. **Debugging**
```python
config = CrawlConfig(
    verbose=True,                  # Enable detailed logging
    headless=False                 # See browser for debugging
)
```

## ⚠️ Important Notes

### **Ethical Crawling**
- Always check `robots.txt` before crawling
- Use appropriate delays between requests
- Respect rate limits and server capacity
- Don't overload servers with concurrent requests

### **Legal Considerations**
- Ensure you have permission to crawl the target sites
- Respect copyright and terms of service
- Use crawled content responsibly
- Consider data privacy implications

### **Technical Considerations**
- Some selectors may not work in all browser contexts
- JavaScript-heavy sites may need longer wait times
- Test with small batches before large crawls
- Monitor memory usage for large crawls

## 🔧 Troubleshooting

### Common Issues

#### **Encoding Errors (Windows)**
```bash
# Use UTF-8 encoding
PYTHONIOENCODING=utf-8 python examples/script.py
```

#### **JavaScript Timeouts**
```python
config = CrawlConfig(
    wait_for_content=True,
    js_wait_time=5.0,              # Increase wait time
    timeout=120                    # Increase overall timeout
)
```

#### **Selector Not Working**
- Test selector in browser dev tools console: `document.querySelectorAll('your-selector')`
- Check if element is dynamically loaded
- Try more specific or less specific selectors
- Use attribute selectors for dynamic content

#### **Memory Issues**
- Reduce `max_pages` and `max_concurrent_requests`
- Process in smaller batches
- Clear results periodically for long runs

## 📚 Additional Resources

- [CSS Selector Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [Website2MD Documentation](../README.md)
- [Crawl4AI Documentation](https://github.com/unclecode/crawl4ai)
- [Browser Developer Tools Guide](https://developer.chrome.com/docs/devtools/)

---

💡 **Pro Tip**: Start with the basic examples and gradually work your way up to advanced filtering techniques. Each example builds upon concepts from the previous ones!