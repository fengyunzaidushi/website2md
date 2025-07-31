"""
Command line interface for the web crawler
"""

import asyncio
import click
import logging
import sys
from typing import Optional

from .crawler import WebCrawler
from .doc_crawler import DocSiteCrawler
from .url_file_crawler import URLFileCrawler
from .url_list_crawler import URLListCrawler
from .config import CrawlConfig
from .utils import format_file_size, get_file_size, create_safe_filename
import os
import re
import json
from urllib.parse import urlparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.command()
@click.argument('input_source')
@click.option('--type', '-t', type=click.Choice(['site', 'docs', 'list']), 
              help='Type: site (full website), docs (documentation), list (URL list)')
@click.option('--output', '-o', default='output', help='Output directory (default: output)')
@click.option('--max-pages', '-m', default=100, help='Maximum pages to crawl (default: 100)')
@click.option('--allow-external', is_flag=True, help='Allow crawling external domains (default: same domain only)')
@click.option('--allowed-domains', help='Comma-separated list of additional domains to allow (e.g., "api.example.com,console.example.com")')
@click.option('--exclude-selectors', help='Comma-separated list of CSS selectors to exclude from content (e.g., ".sidebar,.nav,.footer")')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(
    input_source: str,
    type: Optional[str],
    output: str,
    max_pages: int,
    allow_external: bool,
    allowed_domains: Optional[str],
    exclude_selectors: Optional[str],
    verbose: bool
):
    """
    Website2MD - Convert websites to markdown format
    
    Examples:
    
    \b
    # Auto-detect and crawl full site
    website2md https://example.com --output ./results
    
    \b
    # Crawl documentation site
    website2md https://docs.example.com --type docs --output ./docs
    
    \b
    # Process URL list from file
    website2md urls.txt --type list --output ./content
    
    \b
    # Process URL list directly
    website2md "url1,url2,url3" --type list --output ./content
    
    \b
    # Exclude specific content using CSS selectors
    website2md https://example.com --exclude-selectors ".advertisement,.popup,.cookie-banner" --output ./clean
    """
    
    # Setup logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Auto-detect input type if not specified
    if not type:
        type = _detect_input_type(input_source)
        if verbose:
            click.echo(f"Auto-detected type: {type}")
    
    # Create output directory
    os.makedirs(output, exist_ok=True)
    
    try:
        # Parse allowed domains list
        allowed_domains_list = None
        if allowed_domains:
            allowed_domains_list = [domain.strip() for domain in allowed_domains.split(',')]
            if verbose:
                click.echo(f"Additional allowed domains: {allowed_domains_list}")
        
        # Parse exclude selectors list
        exclude_selectors_list = None
        if exclude_selectors:
            exclude_selectors_list = [selector.strip() for selector in exclude_selectors.split(',')]
            if verbose:
                click.echo(f"Exclude selectors: {exclude_selectors_list}")
        
        # Select and configure appropriate crawler
        if type == 'site':
            crawler = _create_site_crawler(max_pages, allow_external, allowed_domains_list, exclude_selectors_list)
            click.echo(f"[SITE] Crawling full website: {input_source}")
            results = asyncio.run(crawler.crawl(input_source))
            
            # Save results to markdown files
            if results:
                _save_crawl_results(results, output)
            
        elif type == 'docs':
            crawler = _create_docs_crawler(max_pages, output, allow_external, allowed_domains_list, exclude_selectors_list)
            click.echo(f"[DOCS] Crawling documentation site: {input_source}")
            results = asyncio.run(crawler.crawl_documentation_site(input_source, output))
            
        elif type == 'list':
            if os.path.isfile(input_source):
                # URL file
                crawler = _create_url_file_crawler(max_pages, output, allow_external, allowed_domains_list, exclude_selectors_list)
                click.echo(f"[FILE] Processing URL file: {input_source}")
                results = asyncio.run(crawler.crawl_urls_from_file(input_source, output))
            else:
                # URL list string
                crawler = _create_url_list_crawler(max_pages, output, allow_external, allowed_domains_list, exclude_selectors_list)
                click.echo(f"[LIST] Processing URL list")
                results = asyncio.run(crawler.crawl_url_list(input_source, output))
        
        else:
            click.echo(f"[ERROR] Unknown type: {type}", err=True)
            sys.exit(1)
        
        # Show summary
        if results:
            click.echo(f"[SUCCESS] Successfully processed {len(results)} pages")
            click.echo(f"[OUTPUT] Output saved to: {output}/")
        else:
            click.echo("[ERROR] No pages were successfully processed", err=True)
            sys.exit(1)
                    
    except KeyboardInterrupt:
        click.echo("\n[INTERRUPTED] Process interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[ERROR] Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _detect_input_type(input_source: str) -> str:
    """Auto-detect input type based on source"""
    # Check if it's a file
    if os.path.isfile(input_source):
        return 'list'
    
    # Check if it's a comma-separated URL list
    if ',' in input_source and not input_source.startswith('http'):
        return 'list'
    
    # Check if it's a URL
    if input_source.startswith(('http://', 'https://')):
        # Check for documentation indicators
        doc_patterns = ['docs.', 'documentation', '/docs/', 'api.', 'dev.']
        if any(pattern in input_source.lower() for pattern in doc_patterns):
            return 'docs'
        else:
            return 'site'
    
    # Default to list for other inputs
    return 'list'


def _create_site_crawler(max_pages: int, allow_external: bool = False, allowed_domains: list = None, exclude_selectors: list = None) -> WebCrawler:
    """Create crawler for full website crawling"""
    config = CrawlConfig(
        max_depth=3,
        max_pages=max_pages,
        delay=1.0,
        timeout=30,
        follow_external_links=False,
        allow_external_domains=allow_external,
        additional_allowed_domains=allowed_domains,
        exclude_selectors=exclude_selectors,
        javascript_enabled=True,
        max_concurrent_requests=5,
        output_format='json'
    )
    return WebCrawler(config)


def _create_docs_crawler(max_pages: int, output_dir: str, allow_external: bool = False, allowed_domains: list = None, exclude_selectors: list = None) -> DocSiteCrawler:
    """Create crawler for documentation sites"""
    # Default documentation site exclude selectors
    default_exclude_selectors = [
        '.sidebar', '.nav', '.navigation', '#sidebar',
        '#starlight__sidebar', '.docs-sidebar', '.theme-doc-sidebar-container',
        '.header', '.footer', '.breadcrumb', '.toc',
        '.border-r-border', '.md\\:w-64', '.xl\\:w-72'
    ]
    
    # Combine default and user-provided exclude selectors
    final_exclude_selectors = default_exclude_selectors.copy()
    if exclude_selectors:
        final_exclude_selectors.extend(exclude_selectors)
    
    config = CrawlConfig(
        max_pages=max_pages,
        wait_for_content=True,
        js_wait_time=3.0,
        expand_menus=True,
        scroll_for_content=True,
        allow_external_domains=allow_external,
        additional_allowed_domains=allowed_domains,
        exclude_selectors=final_exclude_selectors,
        headless=True,
        timeout=60
    )
    return DocSiteCrawler(config)


def _create_url_file_crawler(max_pages: int, output_dir: str, allow_external: bool = False, allowed_domains: list = None, exclude_selectors: list = None) -> URLFileCrawler:
    """Create crawler for URL file processing"""
    config = CrawlConfig(
        max_pages=max_pages,
        wait_for_content=True,
        js_wait_time=2.0,
        allow_external_domains=allow_external,
        additional_allowed_domains=allowed_domains,
        exclude_selectors=exclude_selectors,
        headless=True,
        timeout=30
    )
    return URLFileCrawler(config)


def _create_url_list_crawler(max_pages: int, output_dir: str, allow_external: bool = False, allowed_domains: list = None, exclude_selectors: list = None) -> URLListCrawler:
    """Create crawler for URL list processing"""
    config = CrawlConfig(
        max_pages=max_pages,
        wait_for_content=True,
        js_wait_time=2.0,
        allow_external_domains=allow_external,
        additional_allowed_domains=allowed_domains,
        exclude_selectors=exclude_selectors,
        headless=True,
        timeout=30
    )
    return URLListCrawler(config)


@click.group()
def cli():
    """Website2MD - Convert websites to markdown format"""
    pass


@cli.command()
def version():
    """Show version information"""
    from . import __version__
    click.echo(f"Website2MD v{__version__}")


@cli.command()
@click.argument('config_file')
def validate_config(config_file: str):
    """Validate a configuration file"""
    try:
        from .utils import load_config
        config_data = load_config(config_file)
        
        if not config_data:
            click.echo("[ERROR] Configuration file is empty or invalid", err=True)
            sys.exit(1)
        
        # Try to create config object
        config = CrawlConfig(**config_data)
        
        click.echo("[VALID] Configuration file is valid")
        click.echo(f"[INFO] Max depth: {config.max_depth}")
        click.echo(f"[INFO] Max pages: {config.max_pages}")
        click.echo(f"[INFO] Delay: {config.delay}s")
        click.echo(f"[INFO] User agent: {config.user_agent}")
        
    except Exception as e:
        click.echo(f"[ERROR] Configuration validation failed: {str(e)}", err=True)
        sys.exit(1)


def _save_crawl_results(results: list, output_dir: str) -> None:
    """Save crawl results as markdown files"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save individual markdown files
    for result in results:
        if not result.get('content'):
            continue
            
        url = result.get('url', '')
        title = result.get('title', '')
        content = result.get('content', '')
        
        # Create filename from URL
        filename = create_safe_filename(url)
        if not filename.endswith('.md'):
            filename += '.md'
            
        filepath = output_path / filename
        
        # Create markdown content with metadata
        markdown_content = f"""# {title}

**URL**: {url}
**Crawled**: {result.get('crawl_timestamp', '')}

---

{content}
"""
        
        # Write file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        except Exception as e:
            click.echo(f"[WARNING] Failed to save {filename}: {e}")
    
    # Save summary
    summary = {
        'total_pages': len(results),
        'successful_pages': len([r for r in results if r.get('success', True)]),
        'failed_pages': len([r for r in results if not r.get('success', True)]),
        'crawl_summary': [
            {
                'url': r.get('url'),
                'title': r.get('title', ''),
                'status_code': r.get('status_code', 200),
                'content_length': r.get('content_length', 0),
                'success': r.get('success', True)
            }
            for r in results
        ]
    }
    
    summary_path = output_path / '_crawl_summary.json'
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    except Exception as e:
        click.echo(f"[WARNING] Failed to save summary: {e}")


if __name__ == '__main__':
    main()