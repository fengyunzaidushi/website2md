#!/usr/bin/env python3
"""
URL File Crawler for crawl4ai v0.6.x
Reads URLs from a text file, deduplicates them, and crawls using crawl4ai
"""

import os
import re
from typing import Set, List, Dict, Optional
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.async_configs import BrowserConfig
from .config import CrawlConfig

class URLFileCrawler:
    """
    Crawler that reads URLs from a text file and crawls them using crawl4ai
    """
    
    def __init__(self, config: CrawlConfig):
        self.config = config
        
    def read_urls_from_file(self, file_path: str) -> Set[str]:
        """
        Read URLs from text file and return deduplicated set
        
        Args:
            file_path: Path to text file containing URLs
            
        Returns:
            Set of unique, valid URLs
        """
        urls = set()
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"URL file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Extract URL from line (handle cases like "mailto:", "https://...")
                url = self._extract_url_from_line(line)
                if url:
                    urls.add(url)
                else:
                    print(f"Warning: Invalid URL on line {line_num}: {line}")
                    
        return urls
    
    def _extract_url_from_line(self, line: str) -> Optional[str]:
        """
        Extract valid HTTP/HTTPS URL from a line of text
        
        Args:
            line: Line of text that may contain a URL
            
        Returns:
            Valid URL or None
        """
        line = line.strip()
        
        # Skip mailto and other non-http protocols
        if line.startswith(('mailto:', 'tel:', 'ftp:', 'file:')):
            return None
            
        # If line starts with http/https, validate it
        if line.startswith(('http://', 'https://')):
            if self._is_valid_url(line):
                return line
        
        # Try to find URL in the line using regex
        url_pattern = r'https?://[^\s<>"]+[^\s<>"\.]'
        match = re.search(url_pattern, line)
        if match:
            url = match.group()
            if self._is_valid_url(url):
                return url
                
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if string is a proper URL
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid URL
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
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
    
    async def crawl_urls_from_file(self, file_path: str, output_dir: str, 
                                 allowed_domains: Optional[List[str]] = None) -> Dict:
        """
        Main method to crawl URLs from file
        
        Args:
            file_path: Path to text file containing URLs
            output_dir: Directory to save crawled content
            allowed_domains: Optional list of allowed domains to filter URLs
            
        Returns:
            Dictionary with crawl summary
        """
        print(f"Reading URLs from file: {file_path}")
        
        # Step 1: Read URLs from file
        raw_urls = self.read_urls_from_file(file_path)
        print(f"Found {len(raw_urls)} raw URLs")
        
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
                'urls_found': len(raw_urls),
                'urls_filtered': len(filtered_urls),
                'urls_unique': 0,
                'pages_crawled': 0,
                'files_saved': 0,
                'errors': 0,
                'error_details': ['No valid URLs to crawl']
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
            'urls_found': len(raw_urls),
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