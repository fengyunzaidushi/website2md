"""
Main web crawler implementation using crawl4ai
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import urljoin, urlparse
import logging

try:
    from crawl4ai import AsyncWebCrawler, CacheMode
    from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
except ImportError:
    print("crawl4ai not installed. Please install it with: pip install crawl4ai")
    raise

from .config import CrawlConfig
from .utils import save_results, is_valid_url, normalize_url

logger = logging.getLogger(__name__)


class WebCrawler:
    """Main web crawler class using crawl4ai"""
    
    def __init__(self, config: Optional[CrawlConfig] = None):
        self.config = config or CrawlConfig()
        self.results: List[Dict[str, Any]] = []
        self.visited_urls: set = set()
        self.filters: Dict[str, Callable] = {}
        self.processors: Dict[str, Callable] = {}
        
    async def crawl(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Crawl a website starting from the given URL
        
        Args:
            start_url: The URL to start crawling from
            
        Returns:
            List of crawled page data
        """
        if not is_valid_url(start_url):
            raise ValueError(f"Invalid URL: {start_url}")
        
        self.results = []
        self.visited_urls = set()
        
        logger.info(f"Starting crawl from: {start_url}")
        
        # Initialize browser configuration with v0.6.x API
        browser_config = BrowserConfig(
            headless=self.config.headless,
            browser_type=self.config.browser_type,
            user_agent=self.config.user_agent,
            verbose=True
        )
        
        # Add stealth mode if enabled  
        if self.config.enable_stealth:
            browser_config.stealth_mode = True
        
        # Add geolocation settings
        if self.config.geolocation:
            browser_config.geolocation = self.config.geolocation
            browser_config.locale = self.config.locale
            browser_config.timezone_id = self.config.timezone
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            await self._crawl_recursive(
                crawler=crawler,
                url=start_url,
                depth=0
            )
        
        logger.info(f"Crawl completed. Found {len(self.results)} pages")
        return self.results
    
    async def _crawl_recursive(
        self, 
        crawler: AsyncWebCrawler, 
        url: str, 
        depth: int
    ) -> None:
        """
        Recursively crawl pages up to max_depth
        
        Args:
            crawler: The AsyncWebCrawler instance
            url: Current URL to crawl
            depth: Current crawling depth
        """
        # Check limits
        if depth > self.config.max_depth:
            return
        
        if len(self.results) >= self.config.max_pages:
            return
        
        # Normalize and check if already visited
        normalized_url = normalize_url(url)
        if normalized_url in self.visited_urls:
            return
        
        # Check domain restrictions
        if not self._is_allowed_domain(url):
            return
        
        self.visited_urls.add(normalized_url)
        
        try:
            logger.info(f"Crawling (depth {depth}): {url}")
            
            # Add delay between requests
            if self.config.delay > 0:
                await asyncio.sleep(self.config.delay)
            
            # Create crawler run configuration with v0.6.x API
            run_config = CrawlerRunConfig(
                word_count_threshold=self.config.word_count_threshold,
                cache_mode=CacheMode.BYPASS if self.config.bypass_cache else CacheMode.ENABLED,
                page_timeout=self.config.timeout * 1000,  # Convert to milliseconds
                screenshot=self.config.enable_screenshot,
                verbose=True
            )
            
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                # Process the crawled data
                page_data = await self._process_page_data(result, url, depth)
                if page_data:  # Only add if page_data is not None
                    self.results.append(page_data)
                
                # Extract and crawl child links if not at max depth
                if depth < self.config.max_depth and self.config.extract_links:
                    links = self._extract_links(result.links, url)
                    
                    # Crawl child pages
                    tasks = []
                    for link in links:
                        if len(self.results) + len(tasks) < self.config.max_pages:
                            task = self._crawl_recursive(crawler, link, depth + 1)
                            tasks.append(task)
                    
                    # Limit concurrent requests
                    for i in range(0, len(tasks), self.config.max_concurrent_requests):
                        batch = tasks[i:i + self.config.max_concurrent_requests]
                        await asyncio.gather(*batch, return_exceptions=True)
                        
            else:
                logger.warning(f"Failed to crawl {url}: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
    
    async def _process_page_data(self, result, url: str, depth: int) -> Dict[str, Any]:
        """Process crawled page data"""
        page_data = {
            "url": url,
            "depth": depth,
            "title": result.metadata.get("title", "") if hasattr(result, 'metadata') and result.metadata else "",
            "status_code": getattr(result, 'status_code', 200),
            "content_length": len(result.markdown) if hasattr(result, 'markdown') and result.markdown else 0,
            "crawl_timestamp": time.time(),
            "success": result.success if hasattr(result, 'success') else True,
        }
        
        # Add content based on configuration
        if self.config.extract_text and hasattr(result, 'markdown') and result.markdown:
            page_data["content"] = result.markdown
            
        if self.config.extract_links and hasattr(result, 'links') and result.links:
            page_data["links"] = result.links
            
        if self.config.extract_images:
            # Handle both legacy media format and new format
            if hasattr(result, 'media') and result.media:
                page_data["images"] = result.media.get("images", [])
            elif hasattr(result, 'images') and result.images:
                page_data["images"] = result.images
            
            # Add screenshot if available
            if hasattr(result, 'screenshot') and result.screenshot:
                page_data["screenshot"] = result.screenshot
            
        # Add metadata if requested
        if self.config.include_metadata and hasattr(result, 'metadata') and result.metadata:
            page_data["metadata"] = result.metadata
            
        # Add extracted data if available (v0.6.x feature)
        if hasattr(result, 'extracted_content') and result.extracted_content:
            page_data["extracted_content"] = result.extracted_content
            
        # Add fit markdown if available (v0.6.x feature)
        if hasattr(result, 'fit_markdown') and result.fit_markdown:
            page_data["fit_markdown"] = result.fit_markdown
            
        # Add network traffic if captured (v0.6.x feature)
        if hasattr(result, 'network_traffic') and result.network_traffic:
            page_data["network_traffic"] = result.network_traffic
            
        # Add console logs if captured (v0.6.x feature)
        if hasattr(result, 'console_logs') and result.console_logs:
            page_data["console_logs"] = result.console_logs
            
        # Apply custom filters
        for filter_name, filter_func in self.filters.items():
            if not filter_func(page_data):
                logger.debug(f"Page {url} filtered out by {filter_name}")
                page_data["filtered"] = True
                page_data["filter_reason"] = filter_name
                return page_data
                
        # Apply custom processors
        for processor_name, processor_func in self.processors.items():
            try:
                processed_data = processor_func(page_data)
                if processed_data:
                    page_data[processor_name] = processed_data
            except Exception as e:
                logger.warning(f"Processor {processor_name} failed for {url}: {e}")
                
        return page_data
    
    def _extract_links(self, links: Dict, base_url: str) -> List[str]:
        """Extract and filter links from page"""
        extracted_links = []
        
        if not links or not isinstance(links, dict):
            return extracted_links
            
        # Get internal and external links
        internal_links = links.get("internal", [])
        external_links = links.get("external", [])
        
        # Add internal links
        for link in internal_links:
            if isinstance(link, dict):
                href = link.get("href", "")
            else:
                href = str(link)
                
            if href:
                full_url = urljoin(base_url, href)
                if is_valid_url(full_url):
                    extracted_links.append(full_url)
        
        # Add external links if allowed
        if self.config.follow_external_links:
            for link in external_links:
                if isinstance(link, dict):
                    href = link.get("href", "")
                else:
                    href = str(link)
                    
                if href and is_valid_url(href):
                    extracted_links.append(href)
        
        return extracted_links
    
    def _is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is allowed"""
        domain = urlparse(url).netloc.lower()
        
        # Check blocked domains
        if self.config.blocked_domains:
            for blocked in self.config.blocked_domains:
                if blocked.lower() in domain:
                    return False
        
        # Check allowed domains
        if self.config.allowed_domains:
            for allowed in self.config.allowed_domains:
                if allowed.lower() in domain:
                    return True
            return False
        
        return True
    
    def add_filter(self, name: str, filter_func: Callable) -> None:
        """Add a custom filter function"""
        self.filters[name] = filter_func
        
    def add_processor(self, name: str, processor_func: Callable) -> None:
        """Add a custom processor function"""
        self.processors[name] = processor_func
        
    def save_results(self, filename: str, format: str = "json") -> None:
        """Save crawl results to file"""
        save_results(self.results, filename, format)
        logger.info(f"Results saved to {filename} in {format} format")