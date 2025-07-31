#!/usr/bin/env python3
"""
Example: Crawl Cursor Documentation Site

This example demonstrates how to crawl the entire Cursor documentation website
starting from the welcome page, while excluding the navigation items.

URL: https://docs.cursor.com/en/welcome
Excludes: div with id="navigation-items"
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from website2md.doc_crawler import DocSiteCrawler
from website2md.config import CrawlConfig


async def main():
    """Main crawling function"""
    
    # Configuration
    start_url = "https://docs.cursor.com/en/welcome"
    output_dir = "./test_cursor_site"
    
    print(f"🚀 Starting to crawl Cursor documentation...")
    print(f"📍 Start URL: {start_url}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🚫 Excluding: #navigation-items")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure crawler
    config = CrawlConfig(
        max_pages=100,                    # Crawl up to 100 pages
        wait_for_content=True,            # Wait for JavaScript content
        js_wait_time=3.0,                 # Wait 3 seconds for JS execution
        expand_menus=True,                # Auto-expand navigation menus
        scroll_for_content=True,          # Scroll to trigger lazy loading
        exclude_selectors=[               # Exclude navigation items
            "#navigation-items"
        ],
        headless=True,                    # Run browser in headless mode
        timeout=60,                       # 60 second timeout per page
        delay=1.0,                        # 1 second delay between requests
        max_concurrent_requests=3,        # Limit concurrent requests
        verbose=True                      # Enable verbose logging
    )
    
    # Create crawler instance
    crawler = DocSiteCrawler(config)
    
    try:
        # Start crawling
        print("\n⏳ Crawling in progress...")
        results = await crawler.crawl_documentation_site(start_url, output_dir)
        
        # Print results summary
        print(f"\n✅ Crawling completed!")
        print(f"📊 Total pages crawled: {len(results) if results else 0}")
        print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
        
        # List generated files
        if os.path.exists(output_dir):
            files = list(Path(output_dir).glob("*.md"))
            print(f"📄 Generated {len(files)} markdown files:")
            for file in sorted(files)[:10]:  # Show first 10 files
                print(f"   - {file.name}")
            if len(files) > 10:
                print(f"   ... and {len(files) - 10} more files")
        
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