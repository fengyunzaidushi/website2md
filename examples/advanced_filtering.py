#!/usr/bin/env python3
"""
Example: Advanced Content Filtering Techniques

This example demonstrates advanced CSS selector techniques for precise
content filtering in different scenarios.
"""

import asyncio
import os
from pathlib import Path

from website2md.doc_crawler import DocSiteCrawler
from website2md.crawler import WebCrawler
from website2md.config import CrawlConfig


async def attribute_based_filtering():
    """Example: Using attribute selectors for precise filtering"""
    
    print("🎯 Example 1: Attribute-Based Filtering")
    print("-" * 45)
    
    start_url = "https://example.com"
    output_dir = "./test_filtering_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    print("🚫 Excluding elements by attributes:")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=5,
        exclude_selectors=[
            # Data attribute selectors
            "[data-testid='advertisement']",      # Test ID attributes
            "[data-component='newsletter']",      # Component attributes
            "[data-track='click']",               # Tracking attributes
            "[data-widget='social-share']",       # Widget attributes
            
            # Role attribute selectors
            "[role='banner']",                    # Banner role
            "[role='navigation']",                # Navigation role
            "[role='complementary']",             # Sidebar/aside role
            "[role='contentinfo']",               # Footer role
            
            # Class attribute selectors (partial matching)
            "[class*='advertisement']",           # Any class containing 'advertisement'
            "[class*='tracking']",                # Any class containing 'tracking'
            "[class*='popup']",                   # Any class containing 'popup'
            
            # ID attribute selectors (partial matching)
            "[id*='nav']",                        # Any ID containing 'nav'
            "[id*='sidebar']",                    # Any ID containing 'sidebar'
            
            # Other attribute selectors
            "[aria-hidden='true']",               # Hidden elements
            "[style*='display: none']",           # Inline hidden elements
        ],
        timeout=30,
        delay=1.0
    )
    
    crawler = WebCrawler(config)
    
    try:
        print("⏳ Crawling with attribute selectors...")
        results = await crawler.crawl(start_url)
        print(f"✅ Processed {len(results)} pages with attribute filtering")
        
        from website2md.cli import _save_crawl_results
        _save_crawl_results(results, output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def descendant_selectors():
    """Example: Using descendant and child selectors"""
    
    print("\n🌳 Example 2: Descendant & Child Selectors")
    print("-" * 45)
    
    start_url = "https://example.com"
    output_dir = "./descendant_filtering_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    print("🚫 Excluding nested elements:")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=5,
        exclude_selectors=[
            # Descendant selectors (space separator)
            "#header nav",                        # Nav inside header
            ".sidebar .widget",                   # Widgets inside sidebar
            ".content .advertisement",            # Ads inside content
            "#footer .social-links",              # Social links in footer
            
            # Child selectors (> separator)
            ".main > .sidebar",                   # Direct sidebar child of main
            "#content > .ad-banner",              # Direct ad banner child
            
            # Multiple level descendants
            "#page .sidebar .widget .advertisement",  # Deeply nested ads
            ".content .post .meta .sharing",      # Nested sharing buttons
            
            # Complex combinations
            ".article header .meta",              # Article metadata in header
            ".blog-post footer .tags",            # Tags in post footer
            ".page-content aside .related",       # Related content in aside
            
            # Universal selectors with descendants
            "* [class*='track']",                 # Any tracking elements anywhere
            "section * [data-ad]",                # Any ad data attributes in sections
        ],
        timeout=30,
        delay=1.0
    )
    
    crawler = WebCrawler(config)
    
    try:
        print("⏳ Crawling with descendant selectors...")
        results = await crawler.crawl(start_url)
        print(f"✅ Processed {len(results)} pages with descendant filtering")
        
        from website2md.cli import _save_crawl_results
        _save_crawl_results(results, output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def pseudo_selectors():
    """Example: Using pseudo-selectors for advanced filtering"""
    
    print("\n🎭 Example 3: Pseudo-Selectors")
    print("-" * 35)
    
    start_url = "https://example.com"
    output_dir = "./pseudo_filtering_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    print("🚫 Excluding with pseudo-selectors:")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=5,
        exclude_selectors=[
            # Nth-child selectors
            ".sidebar > div:first-child",         # First sidebar element
            ".content > div:last-child",          # Last content element
            ".widget-area > div:nth-child(even)", # Even-numbered widgets
            
            # Content-based pseudo-selectors (limited browser support)
            # Note: These might not work in all crawling contexts
            "div:empty",                          # Empty divs
            
            # Attribute existence pseudo-selectors
            "div:not([class])",                   # Divs without class attribute
            "a:not([href])",                      # Links without href
            
            # Complex pseudo combinations
            ".post:not(.featured)",               # Non-featured posts
            "img:not([alt])",                     # Images without alt text
            
            # Multiple pseudo selectors
            ".sidebar > div:first-child .widget", # Widgets in first sidebar div
            ".content > p:last-child .metadata",  # Metadata in last paragraph
        ],
        timeout=30,
        delay=1.0
    )
    
    crawler = WebCrawler(config)
    
    try:
        print("⏳ Crawling with pseudo-selectors...")
        results = await crawler.crawl(start_url)
        print(f"✅ Processed {len(results)} pages with pseudo-selector filtering")
        
        from website2md.cli import _save_crawl_results
        _save_crawl_results(results, output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def real_world_complex_filtering():
    """Example: Real-world complex filtering scenario"""
    
    print("\n🌍 Example 4: Real-World Complex Filtering")
    print("-" * 50)
    
    # Using a documentation site as an example
    start_url = "https://docs.example.com"
    output_dir = "./complex_filtering_output"
    
    print(f"📍 URL: {start_url}")
    print(f"📁 Output: {output_dir}")
    print("🚫 Complex real-world filtering:")
    
    os.makedirs(output_dir, exist_ok=True)
    
    config = CrawlConfig(
        max_pages=10,
        wait_for_content=True,
        js_wait_time=3.0,
        exclude_selectors=[
            # Header and navigation
            "header",
            "nav",
            "#navigation",
            ".navbar",
            ".header-nav",
            
            # Sidebar and TOC
            "aside",
            ".sidebar",
            ".toc",
            "#table-of-contents",
            "[data-testid='sidebar']",
            
            # Footer and metadata
            "footer",
            ".footer",
            ".page-footer",
            ".post-meta",
            ".article-meta",
            
            # Interactive elements
            ".share-buttons",
            ".social-share",
            ".feedback-widget",
            ".rating-widget",
            
            # Ads and tracking
            ".advertisement",
            ".ad-banner",
            "[data-track]",
            "[class*='ad-']",
            "[id*='google-ad']",
            
            # Newsletter and forms
            ".newsletter-signup",
            ".email-subscription",
            ".contact-form",
            
            # Related content
            ".related-articles",
            ".recommended-reading",
            ".similar-posts",
            
            # Breadcrumbs and pagination
            ".breadcrumb",
            ".breadcrumbs",
            ".pagination",
            ".page-navigation",
            
            # Comments
            ".comments",
            ".comment-section",
            "#disqus_thread",
            
            # Mobile-specific
            ".mobile-menu",
            ".mobile-nav",
            "[class*='mobile-only']",
            
            # Framework-specific (common patterns)
            ".skip-link",
            ".screen-reader-text",
            "[aria-hidden='true']",
            
            # Complex descendant patterns
            ".content-wrapper > .sidebar",
            "#main-content aside .widget",
            ".article-body > .pull-quote",
            ".documentation .navigation-panel",
            
            # Attribute-based complex selectors
            "[role='banner']",
            "[role='navigation']",
            "[role='complementary']",
            "[data-component='advertisement']",
            "[data-widget*='social']",
            
            # Pseudo-selector combinations
            ".sidebar > div:first-child",
            ".content > div:last-child .metadata",
        ],
        timeout=60,
        delay=1.5,
        max_concurrent_requests=2
    )
    
    crawler = DocSiteCrawler(config)
    
    try:
        print("⏳ Crawling with comprehensive complex filtering...")
        results = await crawler.crawl_documentation_site(start_url, output_dir)
        print(f"✅ Processed comprehensive filtering")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all advanced filtering examples"""
    
    print("🔍 Website2MD Advanced Content Filtering Examples")
    print("=" * 55)
    print("\n⚠️  Note: Replace example.com with real websites")
    print("⚠️  Some pseudo-selectors may have limited browser support")
    print("⚠️  Test selectors in browser dev tools first")
    
    # Run examples
    await attribute_based_filtering()
    await descendant_selectors()
    await pseudo_selectors()
    await real_world_complex_filtering()
    
    print("\n🎉 All advanced filtering examples completed!")
    print("\n💡 Advanced Tips:")
    print("   - Use browser dev tools to test selectors")
    print("   - Combine multiple selector types for precision")
    print("   - Start simple and add complexity gradually")
    print("   - Test with small pages first")
    print("   - Some pseudo-selectors may not work in all contexts")
    print("   - Attribute selectors are very powerful for modern sites")


if __name__ == "__main__":
    asyncio.run(main())