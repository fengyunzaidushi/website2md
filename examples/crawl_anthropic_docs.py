#!/usr/bin/env python3
"""
Example: Crawl Anthropic Claude Code Documentation

This example demonstrates how to crawl the Anthropic Claude Code documentation
using the default exclude selectors for documentation sites.

URL: https://docs.anthropic.com/zh-CN/docs/claude-code/overview
Uses: Default documentation site exclude selectors
"""

import asyncio
import os
from pathlib import Path

from website2md.doc_crawler import DocSiteCrawler
from website2md.config import CrawlConfig


async def main():
    """Main crawling function"""
    
    # Configuration
    start_url = "https://docs.anthropic.com/zh-CN/docs/claude-code/overview"
    output_dir = "./test_anthropic_docs_output2"
    
    print(f"🚀 Starting to crawl Anthropic Claude Code documentation...")
    print(f"📍 Start URL: {start_url}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🚫 Using default documentation exclude selectors")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure crawler with default exclude selectors
    # Note: DocSiteCrawler automatically applies comprehensive default exclude selectors
    # including navigation, sidebar, header, footer, breadcrumbs, etc.
    config = CrawlConfig(
        max_pages=50,                     # Crawl up to 50 pages
        wait_for_content=True,            # Wait for JavaScript content
        js_wait_time=3.0,                 # Wait 3 seconds for JS execution
        expand_menus=True,                # Auto-expand navigation menus
        scroll_for_content=True,          # Scroll to trigger lazy loading
        # exclude_selectors not specified - will use comprehensive defaults
        headless=True,                    # Run browser in headless mode
        timeout=60,                       # 60 second timeout per page
        delay=1.5,                        # 1.5 second delay between requests (be respectful)
        max_concurrent_requests=2,        # Limit concurrent requests for stability
    )
    
    # Create crawler instance
    crawler = DocSiteCrawler(config)
    
    try:
        # Start crawling
        print("\n⏳ Crawling in progress...")
        print("📋 Default exclude selectors include:")
        print("   - Navigation: #navigation-items, #nav, .navigation, etc.")
        print("   - Sidebars: #sidebar, .sidebar, .docs-sidebar, etc.")
        print("   - Headers/Footers: #header, #footer, .site-header, etc.")
        print("   - TOC/Breadcrumbs: #toc, .breadcrumb, .table-of-contents, etc.")
        print("   - And many more documentation-specific elements...")
        
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
                
            # Show summary file if exists
            summary_file = Path(output_dir) / "_crawl_summary.json"
            if summary_file.exists():
                print(f"📊 Summary file: {summary_file.name}")
        
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        return False
    
    return True


async def crawl_with_custom_excludes():
    """Alternative example: Adding custom exclude selectors to defaults"""
    
    print("\n" + "=" * 60)
    print("🔧 Alternative: Custom exclude selectors + defaults")
    print("=" * 60)
    
    start_url = "https://docs.anthropic.com/zh-CN/docs/claude-code/overview"
    output_dir = "./test_anthropic/anthropic_docs_custom_output"
    
    print(f"📍 Start URL: {start_url}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🚫 Adding custom selectors to defaults")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure with additional custom exclude selectors
    config = CrawlConfig(
        max_pages=20,
        wait_for_content=True,
        js_wait_time=5.0,
        expand_menus=True,
        scroll_for_content=True,
        exclude_selectors=[               # Custom selectors (will be added to defaults)
            ".language-selector",         # Language switcher
            ".version-selector",          # Version selector
            "[data-testid='feedback']",   # Feedback widgets
            ".social-links"               # Social media links
        ],
        headless=True,
        timeout=60,
        delay=1.5,
        max_concurrent_requests=2
    )
    
    crawler = DocSiteCrawler(config)
    
    try:
        print("\n⏳ Crawling with custom + default excludes...")
        results = await crawler.crawl_documentation_site(start_url, output_dir)
        
        print(f"\n✅ Custom crawling completed!")
        print(f"📊 Total pages crawled: {len(results) if results else 0}")
        print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
        
    except Exception as e:
        print(f"❌ Error during custom crawling: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Anthropic Claude Code Documentation Crawler")
    print("=" * 60)
    
    # Run the main crawler
    success1 = asyncio.run(main())
    
    if success1:
        print("\n🎉 Successfully completed crawling Anthropic documentation!")
        
        # Optionally run the custom excludes example
        print("\n❓ Would you like to run the custom excludes example too?")
        print("   (This will create a second output directory)")
        
        # For demo purposes, let's run both
        success2 = asyncio.run(crawl_with_custom_excludes())
        
        if success2:
            print("\n🎉 Both crawling examples completed successfully!")
        
        print("\n💡 Tips:")
        print("   - Compare the two output directories to see the difference")
        print("   - Default excludes provide comprehensive filtering for doc sites")
        print("   - Custom excludes are added on top of the defaults")
        print("   - Check _crawl_summary.json for detailed crawl statistics")
    else:
        print("\n❌ Crawling failed. Please check the error messages above.")