#!/usr/bin/env python3
"""
URL List Crawler for crawl4ai v0.6.x
Accepts URL lists directly from user input and crawls them using crawl4ai
"""

import os
import re
from typing import List, Set, Dict, Optional, Union
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.async_configs import BrowserConfig
from .config import CrawlConfig

class URLListCrawler:
    """
    Crawler that accepts URL lists directly from user input and crawls them using crawl4ai
    """
    
    def __init__(self, config: CrawlConfig):
        self.config = config
        
    def parse_url_input(self, url_input: Union[str, List[str]]) -> Set[str]:
        """
        Parse various URL input formats and return a set of valid URLs
        
        Args:
            url_input: URLs in various formats:
                     - List of strings: ["url1", "url2", ...]
                     - Comma-separated string: "url1, url2, url3"
                     - Line-separated string: "url1\nurl2\nurl3"
                     - Single URL string: "https://example.com"
                     
        Returns:
            Set of unique, valid URLs
        """
        urls = set()
        
        if isinstance(url_input, list):
            # Handle list input
            for url in url_input:
                if isinstance(url, str):
                    parsed_url = self._validate_and_clean_url(url.strip())
                    if parsed_url:
                        urls.add(parsed_url)
        
        elif isinstance(url_input, str):
            # Handle string input - try different separators
            if '\n' in url_input:
                # Line-separated
                for line in url_input.split('\n'):
                    parsed_url = self._validate_and_clean_url(line.strip())
                    if parsed_url:
                        urls.add(parsed_url)
            elif ',' in url_input:
                # Comma-separated
                for url in url_input.split(','):
                    parsed_url = self._validate_and_clean_url(url.strip())
                    if parsed_url:
                        urls.add(parsed_url)
            else:
                # Single URL
                parsed_url = self._validate_and_clean_url(url_input.strip())
                if parsed_url:
                    urls.add(parsed_url)
        
        return urls
    
    def _validate_and_clean_url(self, url: str) -> Optional[str]:
        """
        Validate and clean a URL string
        
        Args:
            url: URL string to validate
            
        Returns:
            Cleaned valid URL or None
        """
        if not url:
            return None
            
        # Skip comments and non-http protocols
        if url.startswith(('#', '//', 'mailto:', 'tel:', 'ftp:', 'file:')):
            return None
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Validate URL format
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return None
            if result.scheme not in ['http', 'https']:
                return None
            return url
        except Exception:
            return None
    
    def filter_urls_by_domain(self, urls: Set[str], allowed_domains: Optional[List[str]] = None) -> Set[str]:
        """
        Filter URLs by allowed domains
        
        Args:
            urls: Set of URLs to filter
            allowed_domains: List of allowed domains (e.g., ['docs.cursor.com'])
            
        Returns:
            Filtered set of URLs
        """
        if not allowed_domains:
            return urls
            
        filtered_urls = set()
        for url in urls:
            try:
                domain = urlparse(url).netloc.lower()
                # Remove www. prefix for comparison
                domain = domain.replace('www.', '')
                
                for allowed_domain in allowed_domains:
                    allowed_domain = allowed_domain.lower().replace('www.', '')
                    if domain == allowed_domain or domain.endswith('.' + allowed_domain):
                        filtered_urls.add(url)
                        break
            except Exception:
                continue
                
        return filtered_urls
    
    def deduplicate_urls(self, urls: Set[str]) -> Set[str]:
        """
        Advanced URL deduplication handling fragments and query parameters
        
        Args:
            urls: Set of URLs to deduplicate
            
        Returns:
            Deduplicated set of URLs
        """
        seen_normalized = set()
        deduplicated = set()
        
        for url in urls:
            try:
                parsed = urlparse(url)
                
                # Create normalized version without fragment
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    normalized += f"?{parsed.query}"
                    
                # For fragment-only differences, prefer the one without fragment
                if normalized not in seen_normalized:
                    seen_normalized.add(normalized)
                    deduplicated.add(url)
                elif not parsed.fragment:
                    # Replace with non-fragment version
                    deduplicated = {u for u in deduplicated if not u.startswith(normalized)}
                    deduplicated.add(url)
                    
            except Exception:
                # Keep original URL if parsing fails
                deduplicated.add(url)
                
        return deduplicated
    
    async def crawl_url_list(self, url_input: Union[str, List[str]], output_dir: str, 
                           allowed_domains: Optional[List[str]] = None) -> Dict:
        """
        Main method to crawl URLs from user input
        
        Args:
            url_input: URLs in various formats (list, comma-separated, line-separated, single URL)
            output_dir: Directory to save crawled content
            allowed_domains: Optional list of allowed domains to filter URLs
            
        Returns:
            Dictionary with crawl summary
        """
        print(f"Processing URL input...")
        
        # Step 1: Parse URLs from input
        raw_urls = self.parse_url_input(url_input)
        print(f"Found {len(raw_urls)} raw URLs")
        
        if not raw_urls:
            return {
                'urls_input': str(url_input)[:100] + "..." if len(str(url_input)) > 100 else str(url_input),
                'urls_parsed': 0,
                'urls_filtered': 0,
                'urls_unique': 0,
                'pages_crawled': 0,
                'files_saved': 0,
                'errors': 1,
                'error_details': ['No valid URLs found in input']
            }
        
        # Show parsed URLs
        print("Parsed URLs:")
        for i, url in enumerate(sorted(raw_urls), 1):
            print(f"  {i}. {url}")
        
        # Step 2: Filter by domains if specified
        if allowed_domains:
            filtered_urls = self.filter_urls_by_domain(raw_urls, allowed_domains)
            print(f"After domain filtering: {len(filtered_urls)} URLs")
        else:
            filtered_urls = raw_urls
            
        # Step 3: Deduplicate URLs
        unique_urls = self.deduplicate_urls(filtered_urls)
        print(f"After deduplication: {len(unique_urls)} unique URLs")
        
        if not unique_urls:
            return {
                'urls_input': str(url_input)[:100] + "..." if len(str(url_input)) > 100 else str(url_input),
                'urls_parsed': len(raw_urls),
                'urls_filtered': len(filtered_urls),
                'urls_unique': 0,
                'pages_crawled': 0,
                'files_saved': 0,
                'errors': 1,
                'error_details': ['No valid URLs after filtering']
            }
        
        # Step 4: Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 5: Setup crawl4ai configuration
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS if self.config.bypass_cache else CacheMode.ENABLED,
            semaphore_count=self.config.max_concurrent_requests,
            mean_delay=self.config.delay,
            css_selector=self.config.content_selector,
            excluded_tags=self.config.exclude_selectors,
            stream=True  # Process results as they come
        )
        
        # Step 6: Crawl URLs using arun_many
        urls_list = list(unique_urls)
        if self.config.max_pages and len(urls_list) > self.config.max_pages:
            urls_list = urls_list[:self.config.max_pages]
            print(f"Limited to first {self.config.max_pages} URLs")
        
        summary = {
            'urls_input': str(url_input)[:100] + "..." if len(str(url_input)) > 100 else str(url_input),
            'urls_parsed': len(raw_urls),
            'urls_filtered': len(filtered_urls),
            'urls_unique': len(unique_urls),
            'pages_crawled': 0,
            'files_saved': 0,
            'files_skipped': 0,
            'errors': 0,
            'error_details': []
        }
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print(f"\nStarting crawl of {len(urls_list)} URLs...")
            print("-" * 60)
            
            try:
                async for result in await crawler.arun_many(urls_list, config=crawler_config):
                    summary['pages_crawled'] += 1
                    
                    if result.success:
                        # Save content to file
                        filename = self._url_to_filename(result.url)
                        file_path = os.path.join(output_dir, filename)
                        
                        # Check if file exists (skip existing files feature)
                        if os.path.exists(file_path):
                            summary['files_skipped'] += 1
                            print(f"[SKIP] {result.url} -> {filename} (exists)")
                            continue
                        
                        # Save markdown content
                        content = f"---\nurl: {result.url}\ncrawled_at: {self._get_timestamp()}\n---\n{result.markdown}"
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                        summary['files_saved'] += 1
                        print(f"[SAVE] {result.url} -> {filename}")
                        
                    else:
                        summary['errors'] += 1
                        error_msg = f"{result.url}: {result.error_message}"
                        summary['error_details'].append(error_msg)
                        print(f"[ERROR] {error_msg}")
                        
            except Exception as e:
                summary['errors'] += 1
                summary['error_details'].append(f"Crawl failed: {str(e)}")
                print(f"[FATAL] Crawl failed: {e}")
        
        return summary
    
    def _url_to_filename(self, url: str) -> str:
        """
        Convert URL to safe filename
        
        Args:
            url: URL to convert
            
        Returns:
            Safe filename string
        """
        try:
            parsed = urlparse(url)
            
            # Start with domain
            domain = parsed.netloc.replace('www.', '')
            
            # Add path, replacing slashes with underscores
            path = parsed.path.strip('/')
            if path:
                path = path.replace('/', '_').replace('-', '-')
            else:
                path = 'index'
            
            # Combine and clean
            if domain and path != 'index':
                filename = f"{domain}_{path}"
            elif domain:
                filename = domain
            else:
                filename = 'unknown'
            
            # Remove invalid characters and add extension
            filename = re.sub(r'[<>:"/\\|?*]', '', filename)
            filename = filename.replace(' ', '_')
            
            # Ensure it ends with .md
            if not filename.endswith('.md'):
                filename += '.md'
                
            return filename
            
        except Exception:
            # Fallback to hash of URL
            import hashlib
            return f"url_{hashlib.md5(url.encode()).hexdigest()[:8]}.md"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def preview_urls(self, url_input: Union[str, List[str]], 
                    allowed_domains: Optional[List[str]] = None) -> Dict:
        """
        Preview what URLs would be crawled without actually crawling
        
        Args:
            url_input: URLs in various formats
            allowed_domains: Optional domain filter
            
        Returns:
            Dictionary with URL processing summary
        """
        print("Previewing URL processing...")
        
        # Parse URLs
        raw_urls = self.parse_url_input(url_input)
        print(f"\n1. Parsed {len(raw_urls)} URLs from input")
        
        # Filter by domains
        if allowed_domains:
            filtered_urls = self.filter_urls_by_domain(raw_urls, allowed_domains)
            print(f"2. After domain filtering: {len(filtered_urls)} URLs")
        else:
            filtered_urls = raw_urls
            print(f"2. No domain filtering applied: {len(filtered_urls)} URLs")
            
        # Deduplicate
        unique_urls = self.deduplicate_urls(filtered_urls)
        print(f"3. After deduplication: {len(unique_urls)} unique URLs")
        
        # Show final URL list
        print(f"\nFinal URLs to crawl:")
        for i, url in enumerate(sorted(unique_urls), 1):
            print(f"  {i}. {url}")
            
        return {
            'input_preview': str(url_input)[:200] + "..." if len(str(url_input)) > 200 else str(url_input),
            'urls_parsed': len(raw_urls),
            'urls_filtered': len(filtered_urls),
            'urls_unique': len(unique_urls),
            'final_urls': sorted(unique_urls)
        }