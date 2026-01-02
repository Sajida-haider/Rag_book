"""Service for scraping content from JavaScript-rendered web pages using Playwright"""

import asyncio
from typing import Dict, Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


class JSWebScraperService:
    def __init__(self, delay: float = 1.0, wait_for_selector: Optional[str] = None):
        self.delay = delay  # Delay between requests to be respectful to the server
        self.wait_for_selector = wait_for_selector  # Optional selector to wait for before scraping

    def fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch the HTML content of a JavaScript-rendered page using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser (use headless=False for debugging)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Set a realistic user agent
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })

                # Navigate to the page
                page.goto(url, wait_until="networkidle")  # Wait until network is idle

                # Wait for Docusaurus content to load - try common Docusaurus selectors
                docusaurus_selectors = [
                    'main div[class*="markdown"]',
                    'div[class*="docItem"]',
                    'div[class*="theme-doc"]',
                    'article',
                    'main',
                    '[role="main"]',
                    'div[class*="doc"]'
                ]

                # Try to wait for Docusaurus content to load
                for selector in docusaurus_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        break  # If one selector is found, continue
                    except:
                        continue  # Try the next selector

                # Wait a bit more for dynamic content to load
                page.wait_for_timeout(3000)

                # Get the fully rendered HTML content
                html_content = page.content()

                browser.close()
                return html_content
        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}")
            return None

    def parse_html(self, html: str, url: str) -> Dict[str, str]:
        """Parse HTML and extract relevant content"""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        else:
            from urllib.parse import urlparse
            title = urlparse(url).path.split('/')[-1] or 'Untitled'

        # Try to find the main content area - for Docusaurus sites
        # Docusaurus typically uses specific classes for main content
        # Try multiple selectors in order of specificity
        content_selectors = [
            'main div.markdown',  # Most specific for Docusaurus markdown content
            'div[class*="markdown"]',  # Docusaurus markdown containers
            'div[class*="docItem"] div[class*="markdown"]',  # Docusaurus doc item markdown
            'article div.markdown',
            'main article',
            'main',  # General main content
            'article',
            'div.theme-doc-markdown',  # Docusaurus specific class
            'div[class*="docItem"]',  # Docusaurus doc item container
            'div.theme-doc',  # Docusaurus theme container
            'div[class*="docMain"]',  # Docusaurus main doc container
            'div.docPageContainer',  # Docusaurus page container
            'div.main-wrapper',  # General wrapper
            'div.container',  # General container
            'div[role="main"]',  # ARIA main role
            soup.body  # Fallback to body
        ]

        main_content = None
        for selector in content_selectors:
            if isinstance(selector, str):
                if selector.startswith('div[') or '.' in selector or '#' in selector:
                    found = soup.select_one(selector)
                else:
                    found = soup.find(selector)
                if found:
                    main_content = found
                    break
            else:
                # If it's not a string (like soup.body), use it directly
                if selector:
                    main_content = selector
                    break

        if main_content:
            # Extract text content, preserving document structure
            content_parts = []

            # Look for content elements in a more comprehensive way
            content_elements = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'section', 'article', 'span', 'pre', 'code'])

            for element in content_elements:
                # Skip elements that are likely navigation or UI elements
                classes = element.get('class', [])
                element_id = element.get('id', '')

                # Skip navigation, sidebar, header, footer elements
                skip_patterns = ['nav', 'menu', 'sidebar', 'footer', 'header', 'cookie', 'banner', 'table-of-contents', 'toc', 'pagination', 'footer', 'navbar', 'navigation', 'sidebar', 'nav', 'menu']

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
        """Extract content from a single URL using Playwright for JavaScript-rendered pages"""
        html = self.fetch_page_content(url)
        if html:
            return self.parse_html(html, url)
        return None


# Async version for better performance when scraping multiple pages
class AsyncJSWebScraperService:
    def __init__(self, delay: float = 1.0, wait_for_selector: Optional[str] = None):
        self.delay = delay
        self.wait_for_selector = wait_for_selector

    async def fetch_page_content(self, url: str) -> Optional[str]:
        """Async version to fetch the HTML content of a JavaScript-rendered page"""
        try:
            async with sync_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })

                await page.goto(url, wait_until="networkidle")

                if self.wait_for_selector:
                    try:
                        await page.wait_for_selector(self.wait_for_selector, timeout=10000)
                    except:
                        pass

                await page.wait_for_timeout(2000)
                html_content = await page.content()

                await browser.close()
                return html_content
        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}")
            return None

    def parse_html(self, html: str, url: str) -> Dict[str, str]:
        """Parse HTML and extract relevant content (same as sync version)"""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        else:
            from urllib.parse import urlparse
            title = urlparse(url).path.split('/')[-1] or 'Untitled'

        # Try to find the main content area - for Docusaurus sites
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
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'section', 'article']):
                # Skip elements that are likely navigation or UI elements
                classes = element.get('class', [])
                if any(skip_class in ' '.join(classes).lower() for skip_class in ['nav', 'menu', 'sidebar', 'footer', 'header', 'cookie', 'banner']):
                    continue

                text = element.get_text().strip()
                if text and len(text) > 10:  # Filter out very short text fragments
                    content_parts.append(text)

            content = '\n\n'.join(content_parts)
        else:
            # Fallback: extract all text from body
            content = soup.get_text()

        # Clean up the content
        lines = (line.strip() for line in content.splitlines())
        content = '\n'.join(line for line in lines if line)

        return {
            'url': url,
            'title': title,
            'content': content
        }

    async def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Async version to extract content from a single URL"""
        html = await self.fetch_page_content(url)
        if html:
            return self.parse_html(html, url)
        return None


if __name__ == "__main__":
    # Example usage
    scraper = JSWebScraperService()

    # Test with a Docusaurus site
    test_url = "https://rag-book.vercel.app/docs/introduction"  # Example Docusaurus URL
    result = scraper.extract_content(test_url)

    if result:
        print(f"Title: {result['title']}")
        print(f"Content length: {len(result['content'])} characters")
        print(f"First 500 chars: {result['content'][:500]}...")
    else:
        print("Failed to extract content")