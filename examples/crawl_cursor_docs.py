#!/usr/bin/env python3
"""
Example: Crawl Cursor Documentation Site

This example demonstrates how to crawl the entire Cursor documentation website
starting from the welcome page, using recursive link discovery.

URL: https://docs.cursor.com/en/welcome
Method: Site crawling (recursive link following)
"""

import asyncio
import os
import time
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

from website2md.crawler import WebCrawler
from website2md.config import CrawlConfig


def url_to_filename(url: str) -> str:
    """Convert URL to filename"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    
    # URL decode and clean the path
    path = unquote(path)
    
    # Replace path separators and special characters with underscores
    filename = re.sub(r'[/\\:*?"<>|]', '_', path)
    
    # Remove multiple underscores and leading/trailing underscores
    filename = re.sub(r'_+', '_', filename).strip('_')
    
    # If filename is empty, use index
    if not filename:
        filename = "index"
        
    # Add .md extension
    return f"{filename}.md"


def save_markdown_results(results, output_dir):
    """Save crawl results as individual markdown files"""
    saved_files = []
    
    for result in results:
        if not result.get('success', False):
            continue
            
        url = result.get('url', '')
        if not url:
            continue
            
        # Get content
        content = result.get('content', '')
        if not content:
            continue
            
        # Create filename 
        filename = url_to_filename(url)
        file_path = os.path.join(output_dir, filename)
        
        # Prepare markdown content with metadata
        title = result.get('title', url)
        
        markdown_content = f"""---
url: {url}
title: {title}
crawled_at: {time.strftime('%Y-%m-%d %H:%M:%S')}
---
{content}
"""
        
        # Save file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            saved_files.append(filename)
            print(f"   - {filename}")
        except Exception as e:
            print(f"   ❌ Failed to save {filename}: {e}")
    
    return saved_files


async def main():
    """Main crawling function"""
    
    # Configuration
    start_url = "https://docs.cursor.com/en/welcome"
    output_dir = "./test_cursor_site3"
    
    print(f"🚀 Starting to crawl Cursor documentation...")
    print(f"📍 Start URL: {start_url}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🚫 Excluding: nav, aside, header, footer, [role='navigation'], .mintlify")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure crawler (WebCrawler for recursive link discovery)
    config = CrawlConfig(
        max_depth=3,                      # Crawl up to 3 levels deep  
        max_pages=100,                    # Crawl up to 100 pages
        exclude_selectors=[               # Exclude navigation items and header/footer
            "nav", "aside", "[role='navigation']", 
            "header", "footer", ".mintlify"
        ],
        javascript_enabled=True,          # Enable JavaScript processing
        headless=True,                    # Run browser in headless mode
        timeout=30,                       # 30 second timeout per page
        delay=1.0,                        # 1 second delay between requests
        max_concurrent_requests=5,        # Allow more concurrent requests for efficiency
        follow_external_links=False       # Stay within the same domain
    )
    
    # Create crawler instance (use WebCrawler for better URL discovery)
    crawler = WebCrawler(config)
    
    try:
        # Start crawling
        print("\n⏳ Crawling in progress...")
        results = await crawler.crawl(start_url)
        
        # Save results as markdown files
        print(f"\n💾 Saving {len(results)} pages as markdown files...")
        saved_files = save_markdown_results(results, output_dir)
        
        # Print results summary
        print(f"\n✅ Crawling completed!")
        print(f"📊 Total pages crawled: {len(results) if results else 0}")
        print(f"📄 Generated {len(saved_files)} markdown files:")
        print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
        
        if len(saved_files) > 10:
            print(f"   (showing first 10 of {len(saved_files)} files)")
            for filename in sorted(saved_files)[:10]:
                print(f"   - {filename}")
            print(f"   ... and {len(saved_files) - 10} more files")
        else:
            for filename in sorted(saved_files):
                print(f"   - {filename}")
        
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Cursor Documentation Crawler")
    print("=" * 60)
    
    # Run the crawler
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Successfully completed crawling Cursor documentation!")
        print("\n💡 Tips:")
        print("   - Check the output directory for generated markdown files")
        print("   - Use the _crawl_summary.json file to see crawl statistics")
        print("   - Navigation items have been excluded for cleaner content")
    else:
        print("\n❌ Crawling failed. Please check the error messages above.")