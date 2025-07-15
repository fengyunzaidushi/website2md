"""
Configuration settings for the web crawler
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class CrawlConfig:
    """Configuration class for web crawler settings"""
    
    # Basic crawling settings
    max_depth: int = 3
    max_pages: int = 100
    delay: float = 1.0
    timeout: int = 30
    
    # v0.6.x Browser and performance settings
    browser_type: str = "chromium"  # chromium, firefox, webkit
    enable_browser_pooling: bool = False
    pool_size: int = 3
    headless: bool = True
    enable_stealth: bool = False
    
    # Request settings
    user_agent: str = "Mozilla/5.0 (compatible; Crawl4Website/1.0)"
    max_concurrent_requests: int = 10
    follow_redirects: bool = True
    
    # Content settings
    follow_external_links: bool = False
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    
    # Output settings
    output_format: str = "json"
    output_file: Optional[str] = None
    include_metadata: bool = True
    
    # Advanced settings
    javascript_enabled: bool = True
    extract_images: bool = False
    extract_links: bool = True
    extract_text: bool = True
    
    # v0.6.x New features
    enable_screenshot: bool = False
    bypass_cache: bool = False
    word_count_threshold: int = 10
    include_raw_html: bool = False
    
    # Geolocation settings (v0.6.x)
    geolocation: Optional[Dict[str, float]] = None  # {"latitude": 40.7128, "longitude": -74.0060}
    locale: str = "en-US"
    timezone: str = "America/New_York"
    
    # Network monitoring (v0.6.x)
    capture_network_traffic: bool = False
    capture_console_logs: bool = False
    
    # Custom headers
    headers: Optional[Dict[str, str]] = None
    
    # Content selection settings (for documentation sites)
    content_selector: Optional[str] = None  # CSS selector for main content area (e.g., "#content-container")
    exclude_selectors: Optional[List[str]] = None  # CSS selectors to exclude from content
    
    # JavaScript rendering settings (for SPA and dynamic sites)
    wait_for_content: bool = True  # Wait for JavaScript to load content
    js_wait_time: float = 3.0  # Time to wait for JS content to load (seconds)
    scroll_for_content: bool = True  # Scroll page to trigger lazy loading
    expand_menus: bool = True  # Try to expand collapsible menus
    
    @classmethod
    def from_env(cls) -> "CrawlConfig":
        """Create configuration from environment variables"""
        geolocation = None
        if os.getenv("GEOLOCATION_LAT") and os.getenv("GEOLOCATION_LON"):
            geolocation = {
                "latitude": float(os.getenv("GEOLOCATION_LAT")),
                "longitude": float(os.getenv("GEOLOCATION_LON"))
            }
        
        return cls(
            max_depth=int(os.getenv("MAX_DEPTH", "3")),
            max_pages=int(os.getenv("MAX_PAGES", "100")),
            delay=float(os.getenv("DELAY_BETWEEN_REQUESTS", "1.0")),
            timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; Crawl4Website/1.0)"),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
            follow_external_links=os.getenv("FOLLOW_EXTERNAL_LINKS", "false").lower() == "true",
            javascript_enabled=os.getenv("JAVASCRIPT_ENABLED", "true").lower() == "true",
            extract_images=os.getenv("EXTRACT_IMAGES", "false").lower() == "true",
            browser_type=os.getenv("BROWSER_TYPE", "chromium"),
            enable_browser_pooling=os.getenv("ENABLE_BROWSER_POOLING", "false").lower() == "true",
            enable_screenshot=os.getenv("ENABLE_SCREENSHOT", "false").lower() == "true",
            geolocation=geolocation,
            locale=os.getenv("LOCALE", "en-US"),
            timezone=os.getenv("TIMEZONE", "America/New_York"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "max_depth": self.max_depth,
            "max_pages": self.max_pages,
            "delay": self.delay,
            "timeout": self.timeout,
            "user_agent": self.user_agent,
            "max_concurrent_requests": self.max_concurrent_requests,
            "follow_redirects": self.follow_redirects,
            "follow_external_links": self.follow_external_links,
            "allowed_domains": self.allowed_domains,
            "blocked_domains": self.blocked_domains,
            "output_format": self.output_format,
            "output_file": self.output_file,
            "include_metadata": self.include_metadata,
            "javascript_enabled": self.javascript_enabled,
            "extract_images": self.extract_images,
            "extract_links": self.extract_links,
            "extract_text": self.extract_text,
            "headers": self.headers,
            # v0.6.x features
            "browser_type": self.browser_type,
            "enable_browser_pooling": self.enable_browser_pooling,
            "pool_size": self.pool_size,
            "headless": self.headless,
            "enable_stealth": self.enable_stealth,
            "enable_screenshot": self.enable_screenshot,
            "bypass_cache": self.bypass_cache,
            "word_count_threshold": self.word_count_threshold,
            "include_raw_html": self.include_raw_html,
            "geolocation": self.geolocation,
            "locale": self.locale,
            "timezone": self.timezone,
            "capture_network_traffic": self.capture_network_traffic,
            "capture_console_logs": self.capture_console_logs,
        }