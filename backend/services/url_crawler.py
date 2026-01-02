"""Service for crawling and discovering all book pages from a base URL"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Set
import time
import re


class URLCrawlerService:
    def __init__(self, base_url: str, delay: float = 1.0):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay  # Delay between requests to be respectful to the server

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain"""
        parsed = urlparse(url)
        return (
            parsed.netloc == self.base_domain and
            parsed.scheme in ['http', 'https'] and
            not re.search(r'\.(pdf|jpg|jpeg|png|gif|css|js|zip|exe|dmg)$', url, re.IGNORECASE)
        )

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all valid links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)

            # Normalize URL
            parsed = urlparse(full_url)
            normalized_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', parsed.query, ''))

            if self.is_valid_url(normalized_url):
                # Only include documentation routes
                if '/docs' in normalized_url:
                    # Remove trailing slashes for consistency
                    if normalized_url.endswith('/'):
                        normalized_url = normalized_url[:-1]
                    links.add(normalized_url)

        return list(links)

    def crawl(self, max_pages: int = 100, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """Crawl the website to discover all accessible pages"""
        if include_patterns is None:
            include_patterns = []
        if exclude_patterns is None:
            exclude_patterns = []

        visited_urls: Set[str] = set()
        to_visit: List[str] = [self.base_url]
        all_urls: Set[str] = set([self.base_url])

        while to_visit and len(visited_urls) < max_pages:
            current_url = to_visit.pop(0)

            if current_url in visited_urls:
                continue

            try:
                print(f"Crawling: {current_url}")
                time.sleep(self.delay)  # Be respectful to the server
                response = self.session.get(current_url, timeout=30)
                response.raise_for_status()

                visited_urls.add(current_url)

                # Extract links from the current page
                links = self.extract_links(response.text, current_url)

                for link in links:
                    # Check include patterns
                    if include_patterns and not any(re.search(pattern, link) for pattern in include_patterns):
                        continue

                    # Check exclude patterns
                    if exclude_patterns and any(re.search(pattern, link) for pattern in exclude_patterns):
                        continue

                    # Add to crawl queue if not visited and not already in queue
                    if link not in visited_urls and link not in to_visit:
                        to_visit.append(link)
                        all_urls.add(link)

            except requests.RequestException as e:
                print(f"Error crawling {current_url}: {e}")
                continue

        # Remove trailing slashes for consistency
        clean_urls = set()
        for url in all_urls:
            if url.endswith('/'):
                clean_urls.add(url[:-1])
            else:
                clean_urls.add(url)

        return list(clean_urls)

    def get_sitemap_urls(self) -> List[str]:
        """Try to get URLs from sitemap if available"""
        sitemap_url = urljoin(self.base_url, '/sitemap.xml')
        try:
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'xml')
            urls = []
            for loc in soup.find_all('loc'):
                url = loc.text.strip()

                # If the sitemap URL is for a different domain, replace it with our base domain
                parsed_url = urlparse(url)
                if parsed_url.netloc != self.base_domain:
                    # Replace the domain in the URL with our current domain
                    new_url = f"{urlparse(self.base_url).scheme}://{self.base_domain}{parsed_url.path}"
                    if parsed_url.query:
                        new_url += f"?{parsed_url.query}"
                    if parsed_url.fragment:
                        new_url += f"#{parsed_url.fragment}"
                    url = new_url

                # Only include documentation routes
                if self.is_valid_url(url) and '/docs' in url:
                    urls.append(url)
            return urls
        except:
            print(f"No sitemap found at {sitemap_url}")
            return []

    def crawl_with_sitemap(self, max_pages: int = 100) -> List[str]:
        """Crawl using both sitemap and traditional crawling"""
        # First try to get URLs from sitemap
        sitemap_urls = self.get_sitemap_urls()
        print(f"Found {len(sitemap_urls)} URLs from sitemap")

        # Check if sitemap URLs are for the correct domain
        correct_domain_sitemap_urls = [url for url in sitemap_urls if self.base_domain in url]
        print(f"Found {len(correct_domain_sitemap_urls)} URLs from sitemap for correct domain")

        # If sitemap has URLs for the correct domain, use them
        if correct_domain_sitemap_urls:
            return correct_domain_sitemap_urls[:max_pages]
        else:
            # Fall back to traditional crawling
            return self.crawl(max_pages=max_pages)