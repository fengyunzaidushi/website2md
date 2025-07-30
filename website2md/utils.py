"""
Utility functions for the web crawler
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)


def save_results(results: List[Dict[str, Any]], filename: str, format: str = "json") -> None:
    """
    Save crawl results to file in specified format
    
    Args:
        results: List of crawled page data
        filename: Output filename
        format: Output format (json, csv, xml, txt)
    """
    format = format.lower()
    
    try:
        if format == "json":
            _save_json(results, filename)
        elif format == "csv":
            _save_csv(results, filename)
        elif format == "xml":
            _save_xml(results, filename)
        elif format == "txt":
            _save_txt(results, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        logger.info(f"Results saved to {filename} in {format} format")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise


def _save_json(results: List[Dict[str, Any]], filename: str) -> None:
    """Save results as JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)


def _save_csv(results: List[Dict[str, Any]], filename: str) -> None:
    """Save results as CSV"""
    if not results:
        return
        
    # Get all unique keys from all results
    fieldnames = set()
    for result in results:
        fieldnames.update(result.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Convert complex objects to strings
            row = {}
            for key, value in result.items():
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value, ensure_ascii=False)
                else:
                    row[key] = str(value) if value is not None else ""
            writer.writerow(row)


def _save_xml(results: List[Dict[str, Any]], filename: str) -> None:
    """Save results as XML"""
    root = ET.Element("crawl_results")
    
    for result in results:
        page = ET.SubElement(root, "page")
        
        for key, value in result.items():
            elem = ET.SubElement(page, key)
            if isinstance(value, (dict, list)):
                elem.text = json.dumps(value, ensure_ascii=False)
            else:
                elem.text = str(value) if value is not None else ""
    
    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def _save_txt(results: List[Dict[str, Any]], filename: str) -> None:
    """Save results as plain text"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, result in enumerate(results, 1):
            f.write(f"=== Page {i} ===\n")
            f.write(f"URL: {result.get('url', 'N/A')}\n")
            f.write(f"Title: {result.get('title', 'N/A')}\n")
            f.write(f"Depth: {result.get('depth', 'N/A')}\n")
            f.write(f"Status: {result.get('status_code', 'N/A')}\n")
            
            content = result.get('content', '')
            if content:
                # Truncate very long content
                if len(content) > 1000:
                    content = content[:1000] + "... [truncated]"
                f.write(f"Content:\n{content}\n")
            
            f.write("\n" + "="*50 + "\n\n")


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config from {config_file}: {e}")
        return {}


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and lowercasing domain"""
    try:
        parsed = urlparse(url)
        # Remove fragment and normalize
        normalized = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized
    except Exception:
        return url


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
        
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
    
    return text.strip()


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    if not text:
        return []
        
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(email_pattern, text)))


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    if not text:
        return []
        
    # Simple phone number patterns
    patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{3}\.\d{3}\.\d{4}\b',  # 123.456.7890
        r'\b\d{10}\b',  # 1234567890
    ]
    
    phone_numbers = []
    for pattern in patterns:
        phone_numbers.extend(re.findall(pattern, text))
    
    return list(set(phone_numbers))


def get_file_size(filename: str) -> int:
    """Get file size in bytes"""
    try:
        import os
        return os.path.getsize(filename)
    except Exception:
        return 0


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"