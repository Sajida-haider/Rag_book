"""Service for scraping content from web pages with support for both static and JavaScript-rendered content"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import urllib.parse
from urllib.parse import urljoin, urlparse


class WebScraperService:
    def __init__(self, delay: float = 1.0, use_js_rendering: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay  # Delay between requests to be respectful to the server
        self.use_js_rendering = use_js_rendering  # Whether to use JS rendering for complex sites

        # Import Playwright-based scraper if needed
        if self.use_js_rendering:
            try:
                from .js_web_scraper import JSWebScraperService
                self.js_scraper = JSWebScraperService(delay=delay)
            except ImportError:
                print("JS Web Scraper not available, falling back to requests-based scraper only")
                self.js_scraper = None
                self.use_js_rendering = False

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch the HTML content of a single page - with fallback to JS rendering if needed"""
        if self.use_js_rendering and self.js_scraper:
            # Try JavaScript rendering first for complex sites like Docusaurus
            html = self.js_scraper.fetch_page_content(url)

            # If JS rendering fails or returns minimal content, fallback to requests
            if html and len(html.strip()) > 100:  # If we got substantial content
                return html

        # Fallback to traditional requests-based scraping
        try:
            time.sleep(self.delay)  # Be respectful to the server
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding  # Handle encoding properly
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str, url: str) -> Dict[str, str]:
        """Parse HTML and extract relevant content"""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else urlparse(url).path.split('/')[-1] or 'Untitled'

        # Try to find the main content area - for Docusaurus sites
        # Docusaurus typically uses specific classes for main content
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_='main-wrapper') or
            soup.find('div', class_='container') or
            soup.find('div', class_='docPageContainer') or
            soup.find('div', class_='theme-doc') or
            soup.find('div', class_=lambda x: x and 'docItem' in x) or
            soup.find('div', class_=lambda x: x and 'docMain' in x) or
            soup.find('div', {'role': 'main'}) or
            soup.find('div', class_=lambda x: x and ('doc' in x.lower() or 'content' in x.lower())) or
            soup.body
        )

        if main_content:
            # Extract text content, preserving document structure
            content_parts = []

            # Look for content in multiple possible containers
            content_containers = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'section', 'article', 'span', 'pre', 'code'])

            for element in content_containers:
                # Skip elements that are likely navigation or UI elements
                classes = element.get('class', [])
                element_id = element.get('id', '')

                # Skip navigation, sidebar, header, footer elements
                skip_patterns = ['nav', 'menu', 'sidebar', 'footer', 'header', 'cookie', 'banner', 'table-of-contents', 'toc', 'pagination', 'footer', 'navbar', 'navigation']

                if any(skip_class in ' '.join(classes).lower() for skip_class in skip_patterns) or any(skip_class in element_id.lower() for skip_class in skip_patterns):
                    continue

                # Get text, but handle code blocks and preformatted text specially
                if element.name in ['pre', 'code']:
                    text = element.get_text().strip()
                else:
                    text = element.get_text().strip()

                # Only include text that is substantial (more than 10 characters)
                if text and len(text) > 10:
                    content_parts.append(text)

            content = '\n\n'.join(content_parts)
        else:
            # Fallback: extract all text from body
            content = soup.get_text()

        # Clean up the content - remove extra whitespace and newlines
        lines = (line.strip() for line in content.splitlines())
        content = '\n'.join(line for line in lines if line)

        return {
            'url': url,
            'title': title,
            'content': content
        }

    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract content from a single URL"""
        html = self.fetch_page(url)
        if html:
            return self.parse_html(html, url)
        return None