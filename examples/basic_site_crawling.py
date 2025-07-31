#!/usr/bin/env python3
"""
Example: Basic Site Crawling with Content Filtering

This example demonstrates different approaches to crawl websites with
various content filtering strategies.
"""

import asyncio
import os
from pathlib import Path

from website2md.crawler import WebCrawler
from website2md.config import CrawlConfig


async def crawl_news_site():
    """Example: Crawl a news site excluding ads and navigation"""
    
    print("📰 Example 1: News Site Crawling")
    print("-" * 40)
    
    # Configuration for news site
    start_url = "https://example-news.com"  # Replace with actual news site
    output_dir = "./test_news_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=10,
        max_depth=2,
        delay=2.0,                        # Be respectful with delays
        timeout=30,
        exclude_selectors=[               # Common news site excludes
            ".advertisement",             # Ad containers
            ".ad-banner",                 # Ad banners
            ".social-share",              # Social sharing buttons
            ".newsletter-signup",         # Newsletter forms
            ".related-articles",          # Related articles sidebar
            "#header",                    # Site header
            "#footer",                    # Site footer
            ".navigation",                # Navigation menus
            ".comments-section"           # Comments section
        ],
        javascript_enabled=True,
        max_concurrent_requests=2
    )
    
    crawler = WebCrawler(config)
    
    try:
        print("⏳ Crawling news site...")
        results = await crawler.crawl(start_url)
        print(f"✅ Crawled {len(results)} pages")
        
        # Save results manually for WebCrawler
        from website2md.cli import _save_crawl_results
        _save_crawl_results(results, output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def crawl_blog():
    """Example: Crawl a blog excluding marketing content"""
    
    print("\n📝 Example 2: Blog Crawling")
    print("-" * 40)
    
    start_url = "https://example-blog.com"  # Replace with actual blog
    output_dir = "./blog_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=15,
        max_depth=3,
        delay=1.5,
        timeout=45,
        exclude_selectors=[               # Blog-specific excludes
            ".author-bio",                # Author biography
            ".post-metadata",             # Post metadata (dates, tags)
            ".share-buttons",             # Social sharing
            ".email-signup",              # Email signup forms
            ".sidebar-widgets",           # Sidebar widgets
            ".comment-form",              # Comment forms
            ".related-posts",             # Related posts
            ".pagination",                # Pagination controls
            "[data-testid='advertisement']"  # Ads with data attributes
        ],
        javascript_enabled=True,
        max_concurrent_requests=3
    )
    
    crawler = WebCrawler(config)
    
    try:
        print("⏳ Crawling blog...")
        results = await crawler.crawl(start_url)
        print(f"✅ Crawled {len(results)} pages")
        
        # Save results
        from website2md.cli import _save_crawl_results
        _save_crawl_results(results, output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def crawl_ecommerce():
    """Example: Crawl e-commerce site for product information only"""
    
    print("\n🛒 Example 3: E-commerce Product Info")
    print("-" * 40)
    
    start_url = "https://example-shop.com"  # Replace with actual e-commerce site
    output_dir = "./ecommerce_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=20,
        max_depth=2,
        delay=2.0,                        # Be extra respectful for e-commerce
        timeout=60,
        exclude_selectors=[               # E-commerce specific excludes
            ".price",                     # Pricing (if you only want descriptions)
            ".buy-button",                # Purchase buttons
            ".add-to-cart",               # Cart buttons
            ".shopping-cart",             # Cart widget
            ".checkout",                  # Checkout elements
            ".recommendations",           # Product recommendations
            ".reviews-section",           # Customer reviews
            ".rating-stars",              # Star ratings
            ".shipping-info",             # Shipping information
            ".payment-methods",           # Payment options
            ".promotional-banner",        # Promotional banners
            ".discount-badge",            # Discount badges
            ".stock-status"               # Stock availability
        ],
        javascript_enabled=True,
        max_concurrent_requests=1         # Very conservative for e-commerce
    )
    
    crawler = WebCrawler(config)
    
    try:
        print("⏳ Crawling e-commerce site...")
        results = await crawler.crawl(start_url)
        print(f"✅ Crawled {len(results)} pages")
        
        # Save results
        from website2md.cli import _save_crawl_results
        _save_crawl_results(results, output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all examples"""
    
    print("🔍 Website2MD Basic Site Crawling Examples")
    print("=" * 50)
    print("\n⚠️  Note: Replace example URLs with real websites")
    print("⚠️  Be respectful: Use appropriate delays and limits")
    print("⚠️  Check robots.txt before crawling")
    
    # Run examples
    await crawl_news_site()
    await crawl_blog() 
    await crawl_ecommerce()
    
    print("\n🎉 All examples completed!")
    print("\n💡 Tips:")
    print("   - Adjust exclude_selectors based on actual site structure")
    print("   - Use browser dev tools to inspect elements")
    print("   - Test with small max_pages first")
    print("   - Respect rate limits and robots.txt")
    print("   - Monitor site performance impact")


if __name__ == "__main__":
    asyncio.run(main())