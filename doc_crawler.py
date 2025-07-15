"""
Documentation site crawler with sitemap extraction and individual MD file saving
"""

import asyncio
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse, unquote
import logging

try:
    from crawl4ai import AsyncWebCrawler, CacheMode
    from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
except ImportError:
    print("crawl4ai not installed. Please install it with: pip install crawl4ai")
    raise

from .config import CrawlConfig
from .utils import is_valid_url, normalize_url

logger = logging.getLogger(__name__)


class DocSiteCrawler:
    """Documentation site crawler with sitemap extraction and MD file saving"""
    
    def __init__(self, config: Optional[CrawlConfig] = None):
        self.config = config or CrawlConfig()
        self.base_domain = ""
        self.sitemap_urls: Set[str] = set()
        self.crawled_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        
        # Set default exclude selectors for common documentation site elements
        if self.config.exclude_selectors is None:
            self.config.exclude_selectors = [
                "#navigation-items",
                "#starlight__sidebar", 
                ".sidebar",
                ".navigation",
                ".nav",
                ".toc",
                ".table-of-contents",
                ".breadcrumb",
                ".breadcrumbs",
                ".header",
                ".footer",
                ".site-header",
                ".site-footer",
                ".docs-sidebar",
                ".sidebar-nav",
                ".menu",
                ".navbar",
                "#sidebar",
                ".aside",
                "[data-testid='sidebar']",
                "[data-testid='navigation']",
                ".theme-doc-sidebar-container",
                ".theme-doc-toc-mobile",
                ".pagination-nav"
            ]
        
    def url_to_filename(self, url: str) -> str:
        """
        Convert URL to filename by removing domain and replacing path separators
        
        Args:
            url: Full URL like https://example.com/docs/guide/intro
            
        Returns:
            Filename like docs_guide_intro.md
        """
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
    
    async def extract_sitemap_from_page(self, url: str) -> Set[str]:
        """
        Extract all documentation links from a page with dynamic menu expansion
        
        This method handles collapsible/expandable sidebar menus by automatically
        clicking on expandable elements to reveal hidden navigation links.
        
        Args:
            url: URL to extract sitemap from
            
        Returns:
            Set of discovered URLs
        """
        browser_config = BrowserConfig(
            headless=self.config.headless,
            browser_type=self.config.browser_type,
            verbose=True
        )
        
        # Use session to maintain state across multiple interactions
        session_id = f"sitemap_extraction_{int(time.time())}"
        
        discovered_urls = set()
        
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"Extracting sitemap with dynamic menu expansion from: {url}")
                
                # Step 1: Load initial page
                initial_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS if self.config.bypass_cache else CacheMode.ENABLED,
                    page_timeout=self.config.timeout * 1000,
                    session_id=session_id,
                    verbose=True
                )
                
                result = await crawler.arun(url=url, config=initial_config)
                
                if not result.success:
                    logger.warning(f"Failed to load initial page {url}: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
                    return discovered_urls
                
                # Step 2: Expand all collapsible menu sections
                menu_expansion_js = """
                (async () => {
                    console.log('Starting dynamic menu expansion...');
                    
                    // Common selectors for expandable menu items
                    const expandableSelectors = [
                        // Generic patterns
                        '[aria-expanded="false"]',
                        '[data-toggle="collapse"]',
                        '.collapsible:not(.active)',
                        '.expandable:not(.expanded)',
                        '.dropdown-toggle',
                        '.menu-toggle',
                        
                        // Documentation-specific patterns
                        '.sidebar-item[aria-expanded="false"]',
                        '.nav-item[aria-expanded="false"]',
                        '.toc-item[aria-expanded="false"]',
                        '.docs-nav-item[aria-expanded="false"]',
                        
                        // Framework-specific patterns (Docusaurus, GitBook, etc.)
                        '.menu__list-item--collapsible:not(.menu__list-item--collapsed)',
                        '.theme-doc-sidebar-item-category[aria-expanded="false"]',
                        '.navigation-item[aria-expanded="false"]',
                        
                        // Button/link patterns
                        'button[aria-expanded="false"]',
                        'a[aria-expanded="false"]',
                        '.nav-link[aria-expanded="false"]',
                        
                        // Custom patterns for common docs sites
                        '.sidebar-category:not(.active)',
                        '.category-item:not(.expanded)',
                        '.folder:not(.open)',
                        '.tree-node:not(.expanded)',
                        
                        // Cursor docs specific (based on the example URLs)
                        '.sidebar-item .cursor-pointer[aria-expanded="false"]',
                        '.navigation-item .toggle-button:not(.expanded)'
                    ];
                    
                    let totalClicked = 0;
                    let rounds = 0;
                    const maxRounds = 5; // Prevent infinite loops
                    
                    while (rounds < maxRounds) {
                        rounds++;
                        console.log(`Expansion round ${rounds}...`);
                        
                        let clickedInRound = 0;
                        
                        // Try each selector pattern
                        for (const selector of expandableSelectors) {
                            try {
                                const elements = document.querySelectorAll(selector);
                                console.log(`Found ${elements.length} elements for selector: ${selector}`);
                                
                                for (const element of elements) {
                                    // Check if element is visible and clickable
                                    if (element.offsetParent !== null && !element.disabled) {
                                        try {
                                            // Scroll into view
                                            element.scrollIntoView({ behavior: 'instant', block: 'center' });
                                            
                                            // Wait a bit for scroll
                                            await new Promise(r => setTimeout(r, 100));
                                            
                                            // Click the element
                                            element.click();
                                            clickedInRound++;
                                            totalClicked++;
                                            
                                            console.log(`Clicked element: ${selector} (${element.textContent?.trim().substring(0, 50)})`);
                                            
                                            // Wait for potential content to load
                                            await new Promise(r => setTimeout(r, 200));
                                            
                                        } catch (clickError) {
                                            console.log(`Failed to click element: ${clickError.message}`);
                                        }
                                    }
                                }
                            } catch (selectorError) {
                                // Selector might not be valid, continue
                                console.log(`Selector error for ${selector}: ${selectorError.message}`);
                            }
                        }
                        
                        console.log(`Round ${rounds} completed. Clicked ${clickedInRound} elements.`);
                        
                        // If no new elements were clicked, we're done
                        if (clickedInRound === 0) {
                            break;
                        }
                        
                        // Wait between rounds for content to settle
                        await new Promise(r => setTimeout(r, 500));
                    }
                    
                    console.log(`Menu expansion completed. Total elements clicked: ${totalClicked}`);
                    
                    // Mark completion
                    window.menuExpansionComplete = true;
                    return totalClicked;
                })();
                """
                
                # Execute menu expansion with wait condition
                expansion_config = CrawlerRunConfig(
                    session_id=session_id,
                    js_code=menu_expansion_js,
                    wait_for="js:() => window.menuExpansionComplete === true",
                    js_only=True,  # Continue in existing session
                    page_timeout=60000,  # Give more time for expansion
                    verbose=True
                )
                
                logger.info("Expanding dynamic menu sections...")
                expansion_result = await crawler.arun(url=url, config=expansion_config)
                
                if expansion_result.success:
                    logger.info("Menu expansion completed successfully")
                else:
                    logger.warning("Menu expansion may have failed, but continuing...")
                
                # Step 3: Extract all links after expansion
                final_config = CrawlerRunConfig(
                    session_id=session_id,
                    js_only=True,  # Continue in existing session
                    verbose=True
                )
                
                logger.info("Extracting navigation data and links after menu expansion...")
                final_result = await crawler.arun(url=url, config=final_config)
                
                if final_result.success:
                    # Method 1: Extract from navigation JSON data structures
                    if hasattr(final_result, 'html') and final_result.html:
                        json_urls = self._extract_urls_from_navigation_json(final_result.html, url)
                        discovered_urls.update(json_urls)
                        logger.info(f"Found {len(json_urls)} URLs from navigation JSON data")
                    
                    # Method 2: Extract from standard links (fallback)
                    if hasattr(final_result, 'links') and final_result.links:
                        internal_links = final_result.links.get("internal", [])
                        
                        for link in internal_links:
                            if isinstance(link, dict):
                                href = link.get("href", "")
                            else:
                                href = str(link)
                                
                            if href:
                                full_url = urljoin(url, href)
                                if is_valid_url(full_url) and self._is_documentation_url(full_url):
                                    discovered_urls.add(normalize_url(full_url))
                    
                    logger.info(f"Found {len(discovered_urls)} total documentation URLs after comprehensive extraction")
                else:
                    logger.warning(f"Failed to extract content after expansion: {final_result.error_message if hasattr(final_result, 'error_message') else 'Unknown error'}")
                
                # Clean up session
                try:
                    await crawler.crawler_strategy.kill_session(session_id)
                except:
                    pass  # Session cleanup is best effort
                    
        except Exception as e:
            logger.error(f"Error extracting sitemap from {url}: {str(e)}")
            
        return discovered_urls
    
    def _extract_urls_from_navigation_json(self, html: str, base_url: str) -> Set[str]:
        """
        Extract URLs from JSON navigation data structures embedded in HTML
        
        Args:
            html: Raw HTML content
            base_url: Base URL to resolve relative paths
            
        Returns:
            Set of discovered URLs from navigation JSON
        """
        import re
        
        discovered_urls = set()
        parsed_base = urlparse(base_url)
        base_url_clean = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        try:
            # Pattern 1: Extract navigation groups with pages
            group_pattern = r'"group":\s*"([^"]*)",\s*"pages":\s*\[([^\]]*)\]'
            matches = re.findall(group_pattern, html)
            
            for group_name, pages_str in matches:
                # Extract individual page paths from the pages array
                page_pattern = r'"([^"]*)"'
                pages = re.findall(page_pattern, pages_str)
                
                for page in pages:
                    if page and '/' in page and not page.startswith('http'):
                        # Handle leading slash variations
                        clean_page = page.lstrip('/')
                        if clean_page:
                            full_url = f"{base_url_clean}/{clean_page}"
                            if self._is_documentation_url(full_url):
                                discovered_urls.add(normalize_url(full_url))
            
            # Pattern 2: Extract standalone page references
            # Look for URL-like patterns that could be navigation paths
            url_patterns = [
                r'"([a-zA-Z0-9@/_-]+/[a-zA-Z0-9@/_-]+)"',  # Standard paths
                r'"(/[a-zA-Z0-9@/_-]+/[a-zA-Z0-9@/_-]+)"',  # Paths with leading slash
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    # Clean and validate the path
                    path = match.lstrip('/')
                    if (path and 
                        '/' in path and 
                        not path.startswith('http') and 
                        not path.startswith('_') and
                        len(path) > 3 and
                        # Only include paths that look like documentation
                        any(keyword in path.lower() for keyword in [
                            'agent', 'context', 'get-started', 'guides', 'tools',
                            'account', 'settings', 'troubleshooting', 'tab',
                            'configuration', 'models', 'chat', 'inline-edit',
                            '@-symbols', 'background-agent', 'more'
                        ])):
                        full_url = f"{base_url_clean}/{path}"
                        if self._is_documentation_url(full_url):
                            discovered_urls.add(normalize_url(full_url))
            
            logger.info(f"JSON extraction found {len(discovered_urls)} unique URLs")
            
        except Exception as e:
            logger.warning(f"Error extracting URLs from JSON navigation: {str(e)}")
        
        return discovered_urls
    
    def _is_documentation_url(self, url: str) -> bool:
        """
        Check if URL looks like a documentation page
        
        Args:
            url: URL to check
            
        Returns:
            True if it looks like documentation
        """
        parsed = urlparse(url)
        
        # Check if it's on the same domain
        if not parsed.netloc.endswith(self.base_domain.replace('https://', '').replace('http://', '')):
            return False
            
        path = parsed.path.lower()
        
        # Common documentation patterns
        doc_patterns = [
            '/docs/', '/documentation/', '/guide/', '/guides/', '/tutorial/', 
            '/tutorials/', '/api/', '/reference/', '/help/', '/manual/',
            '/wiki/', '/kb/', '/knowledge/', '/learn/', '/getting-started/',
            '/quickstart/', '/overview/', '/concepts/', '/examples/',
            '/features/', '/tools/', '/tab/', '/chat/', '/composer/'
        ]
        
        # Check if path contains documentation indicators
        for pattern in doc_patterns:
            if pattern in path:
                return True
                
        # Check file extensions (avoid binary files)
        excluded_extensions = ['.pdf', '.zip', '.tar.gz', '.exe', '.dmg', '.pkg']
        for ext in excluded_extensions:
            if path.endswith(ext):
                return False
                
        return True
    
    async def crawl_single_url(self, url: str, output_dir: str) -> Optional[Dict[str, Any]]:
        """
        Crawl a single URL and save as individual MD file
        
        Args:
            url: URL to crawl
            output_dir: Directory to save MD files
            
        Returns:
            Dictionary with crawl results or None if failed
        """
        browser_config = BrowserConfig(
            headless=self.config.headless,
            browser_type=self.config.browser_type,
            verbose=False  # Less verbose for individual crawls
        )
        
        # Prepare content selection parameters
        css_selector = self.config.content_selector if self.config.content_selector else None
        excluded_selector = None
        
        if self.config.exclude_selectors:
            # Join multiple selectors with comma for CSS selector exclusion
            excluded_selector = ", ".join(self.config.exclude_selectors)
        
        # Debug logging for content selection
        logger.info(f"Content selector: {css_selector}")
        logger.info(f"Exclude selector: {excluded_selector}")
        
        # Build JavaScript code for content loading
        js_code = None
        if self.config.wait_for_content:
            js_parts = []
            
            if self.config.scroll_for_content:
                js_parts.append("""
                // Scroll to trigger lazy loading
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 1000));
                """)
            
            if self.config.expand_menus:
                js_parts.append("""
                // Try to expand collapsible menus
                const expandableElements = document.querySelectorAll('[aria-expanded="false"]');
                expandableElements.forEach(el => {
                    try {
                        el.click();
                    } catch (e) {
                        console.log('Could not click element:', e);
                    }
                });
                await new Promise(resolve => setTimeout(resolve, 500));
                """)
            
            if js_parts:
                js_code = "".join(js_parts)
        
        run_config = CrawlerRunConfig(
            word_count_threshold=self.config.word_count_threshold,
            cache_mode=CacheMode.BYPASS if self.config.bypass_cache else CacheMode.ENABLED,
            page_timeout=self.config.timeout * 1000,
            css_selector=css_selector,
            excluded_selector=excluded_selector,
            js_code=js_code,
            delay_before_return_html=self.config.js_wait_time if self.config.wait_for_content else 0,
            verbose=True  # Enable verbose to debug selector application
        )
        
        # Check if file already exists and skip if so
        filename = self.url_to_filename(url)
        file_path = os.path.join(output_dir, filename)
        
        if os.path.exists(file_path):
            logger.info(f"Skipping {url} - file already exists: {filename}")
            # Return success info for existing file
            try:
                file_size = os.path.getsize(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Estimate content length (markdown content after metadata header)
                    content_lines = content.split('\n')
                    content_start = 0
                    if content_lines and content_lines[0].strip() == '---':
                        # Find end of metadata header
                        for i in range(1, len(content_lines)):
                            if content_lines[i].strip() == '---':
                                content_start = i + 1
                                break
                    markdown_content = '\n'.join(content_lines[content_start:])
                    
                return {
                    "url": url,
                    "filename": filename,
                    "file_path": file_path,
                    "title": "Existing file",
                    "content_length": len(markdown_content),
                    "success": True,
                    "skipped": True,
                    "timestamp": time.time()
                }
            except Exception as e:
                logger.warning(f"Error reading existing file {file_path}: {str(e)}")
                # Continue with crawling if we can't read existing file
        
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"Crawling: {url}")
                result = await crawler.arun(url=url, config=run_config)
                
                if result.success and hasattr(result, 'markdown') and result.markdown:
                    # Prepare markdown content with metadata
                    content = self._prepare_markdown_content(result, url)
                    
                    # Save to file
                    os.makedirs(output_dir, exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"Saved: {filename}")
                    
                    # Return success info
                    return {
                        "url": url,
                        "filename": filename,
                        "file_path": file_path,
                        "title": result.metadata.get("title", "") if hasattr(result, 'metadata') and result.metadata else "",
                        "content_length": len(result.markdown),
                        "success": True,
                        "timestamp": time.time()
                    }
                else:
                    error_msg = result.error_message if hasattr(result, 'error_message') else "Unknown error"
                    logger.warning(f"Failed to crawl {url}: {error_msg}")
                    self.failed_urls.add(url)
                    return {
                        "url": url,
                        "success": False,
                        "error": error_msg,
                        "timestamp": time.time()
                    }
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            self.failed_urls.add(url)
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _prepare_markdown_content(self, result, url: str) -> str:
        """
        Prepare markdown content with metadata header
        
        Args:
            result: Crawl result from crawl4ai
            url: Original URL
            
        Returns:
            Formatted markdown content
        """
        # Extract metadata
        title = ""
        if hasattr(result, 'metadata') and result.metadata:
            title = result.metadata.get("title", "")
            
        # Build metadata header
        metadata = [
            "---",
            f"url: {url}",
            f"title: {title}" if title else "",
            f"crawled_at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "---",
            ""
        ]
        
        # Filter out empty lines in metadata
        metadata = [line for line in metadata if line or line == "---"]
        
        # Combine metadata and content
        content_lines = metadata + [result.markdown]
        
        return "\n".join(content_lines)
    
    async def crawl_documentation_site(self, start_url: str, output_dir: str = "docs_output") -> Dict[str, Any]:
        """
        Main method to crawl a documentation site
        
        Args:
            start_url: Starting URL of the documentation site
            output_dir: Directory to save MD files
            
        Returns:
            Dictionary with crawl statistics
        """
        logger.info(f"Starting documentation site crawl: {start_url}")
        
        # Set base domain
        parsed = urlparse(start_url)
        self.base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Step 1: Extract sitemap/navigation
        logger.info("📋 Step 1: Extracting sitemap...")
        self.sitemap_urls = await self.extract_sitemap_from_page(start_url)
        
        # Add start URL to sitemap if not already there
        self.sitemap_urls.add(normalize_url(start_url))
        
        logger.info(f"📄 Found {len(self.sitemap_urls)} unique URLs to crawl")
        
        # Step 2: Crawl each URL and save as MD
        logger.info("🚀 Step 2: Crawling individual pages...")
        
        successful_crawls = []
        failed_crawls = []
        skipped_crawls = []
        
        # Limit concurrent requests to avoid overwhelming the server
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def crawl_with_semaphore(url):
            async with semaphore:
                # Add delay between requests
                if self.config.delay > 0:
                    await asyncio.sleep(self.config.delay)
                return await self.crawl_single_url(url, output_dir)
        
        # Process URLs in batches
        batch_size = 5
        url_list = list(self.sitemap_urls)
        
        for i in range(0, len(url_list), batch_size):
            batch = url_list[i:i + batch_size]
            
            # Process batch
            tasks = [crawl_with_semaphore(url) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Exception in crawl: {result}")
                    failed_crawls.append({"error": str(result)})
                elif result and result.get("success"):
                    if result.get("skipped"):
                        skipped_crawls.append(result)
                    else:
                        successful_crawls.append(result)
                    self.crawled_urls.add(result["url"])
                else:
                    failed_crawls.append(result)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(url_list) + batch_size - 1)//batch_size}")
        
        # Step 3: Generate summary
        summary = {
            "start_url": start_url,
            "base_domain": self.base_domain,
            "urls_discovered": len(self.sitemap_urls),
            "urls_crawled_successfully": len(successful_crawls),
            "urls_skipped": len(skipped_crawls),
            "urls_failed": len(failed_crawls),
            "total_processed": len(successful_crawls) + len(skipped_crawls) + len(failed_crawls),
            "output_directory": output_dir,
            "crawl_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "successful_crawls": successful_crawls,
            "skipped_crawls": skipped_crawls,
            "failed_crawls": failed_crawls
        }
        
        # Save summary
        summary_file = os.path.join(output_dir, "_crawl_summary.json")
        os.makedirs(output_dir, exist_ok=True)
        
        import json
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Crawl completed!")
        logger.info(f"📄 Successfully crawled: {len(successful_crawls)} pages")
        logger.info(f"⏭️ Skipped existing: {len(skipped_crawls)} pages")
        logger.info(f"❌ Failed: {len(failed_crawls)} pages")
        logger.info(f"📊 Total processed: {len(successful_crawls) + len(skipped_crawls) + len(failed_crawls)} pages")
        logger.info(f"💾 Output saved to: {output_dir}")
        logger.info(f"📋 Summary saved to: {summary_file}")
        
        return summary