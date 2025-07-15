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
from .utils import format_file_size, get_file_size
import os
import re

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
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(
    input_source: str,
    type: Optional[str],
    output: str,
    max_pages: int,
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
            click.echo(f"🔍 Auto-detected type: {type}")
    
    # Create output directory
    os.makedirs(output, exist_ok=True)
    
    try:
        # Select and configure appropriate crawler
        if type == 'site':
            crawler = _create_site_crawler(max_pages)
            click.echo(f"🌐 Crawling full website: {input_source}")
            results = asyncio.run(crawler.crawl(input_source))
            
        elif type == 'docs':
            crawler = _create_docs_crawler(max_pages, output)
            click.echo(f"📚 Crawling documentation site: {input_source}")
            results = asyncio.run(crawler.crawl_documentation_site(input_source, output))
            
        elif type == 'list':
            if os.path.isfile(input_source):
                # URL file
                crawler = _create_url_file_crawler(max_pages, output)
                click.echo(f"📄 Processing URL file: {input_source}")
                results = asyncio.run(crawler.crawl_urls_from_file(input_source, output))
            else:
                # URL list string
                crawler = _create_url_list_crawler(max_pages, output)
                click.echo(f"📋 Processing URL list")
                results = asyncio.run(crawler.crawl_url_list(input_source, output))
        
        else:
            click.echo(f"❌ Unknown type: {type}", err=True)
            sys.exit(1)
        
        # Show summary
        if results:
            click.echo(f"✅ Successfully processed {len(results)} pages")
            click.echo(f"📁 Output saved to: {output}/")
        else:
            click.echo("❌ No pages were successfully processed", err=True)
            sys.exit(1)
                    
    except KeyboardInterrupt:
        click.echo("\n⏹️  Process interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
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


def _create_site_crawler(max_pages: int) -> WebCrawler:
    """Create crawler for full website crawling"""
    config = CrawlConfig(
        max_depth=3,
        max_pages=max_pages,
        delay=1.0,
        timeout=30,
        follow_external_links=False,
        javascript_enabled=True,
        max_concurrent_requests=5,
        output_format='json'
    )
    return WebCrawler(config)


def _create_docs_crawler(max_pages: int, output_dir: str) -> DocSiteCrawler:
    """Create crawler for documentation sites"""
    config = CrawlConfig(
        max_pages=max_pages,
        wait_for_content=True,
        js_wait_time=3.0,
        expand_menus=True,
        scroll_for_content=True,
        exclude_selectors=[
            '.sidebar', '.nav', '.navigation', '#sidebar',
            '#starlight__sidebar', '.docs-sidebar', '.theme-doc-sidebar-container',
            '.header', '.footer', '.breadcrumb', '.toc',
            '.border-r-border', '.md\\:w-64', '.xl\\:w-72'
        ],
        headless=True,
        timeout=60
    )
    return DocSiteCrawler(config)


def _create_url_file_crawler(max_pages: int, output_dir: str) -> URLFileCrawler:
    """Create crawler for URL file processing"""
    config = CrawlConfig(
        max_pages=max_pages,
        wait_for_content=True,
        js_wait_time=2.0,
        headless=True,
        timeout=30
    )
    return URLFileCrawler(config)


def _create_url_list_crawler(max_pages: int, output_dir: str) -> URLListCrawler:
    """Create crawler for URL list processing"""
    config = CrawlConfig(
        max_pages=max_pages,
        wait_for_content=True,
        js_wait_time=2.0,
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
            click.echo("❌ Configuration file is empty or invalid", err=True)
            sys.exit(1)
        
        # Try to create config object
        config = CrawlConfig(**config_data)
        
        click.echo("✅ Configuration file is valid")
        click.echo(f"📊 Max depth: {config.max_depth}")
        click.echo(f"📊 Max pages: {config.max_pages}")
        click.echo(f"📊 Delay: {config.delay}s")
        click.echo(f"📊 User agent: {config.user_agent}")
        
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()