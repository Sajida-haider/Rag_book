"""Service for extracting content from HTML and organizing it"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re


class ContentExtractorService:
    def __init__(self):
        pass

    def extract_content_from_html(self, html: str, url: str) -> Dict[str, str]:
        """Extract main content from HTML, removing navigation and other non-content elements"""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove common navigation and non-content elements
        for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'meta', 'link']):
            element.decompose()

        # Remove elements with common class names for navigation, ads, etc.
        for element in soup.find_all(class_=re.compile(r'nav|menu|sidebar|advertisement|ads|cookie|banner|footer')):
            element.decompose()

        # Try to find the main content area - for Docusaurus sites
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_='main-wrapper') or
            soup.find('div', class_='container') or
            soup.find('div', class_='docPageContainer') or
            soup.find('div', {'role': 'main'}) or
            soup.find('div', class_=lambda x: x and ('doc' in x.lower() or 'content' in x.lower())) or
            soup.find('div', class_=re.compile(r'docItemContainer|docMainContainer|theme-doc')) or
            soup.body
        )

        if main_content:
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else url.split('/')[-1] or 'Untitled'

            # Extract content text, preserving document structure
            content_parts = []
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div', 'span']):
                text = element.get_text().strip()
                if text:
                    # Preserve heading structure
                    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        content_parts.append(f"\n{element.name.upper()}: {text}\n")
                    else:
                        content_parts.append(text)

            content = '\n'.join(content_parts)
        else:
            # Fallback: extract all text from body
            title = url.split('/')[-1] or 'Untitled'
            content = soup.get_text()

        # Clean up the content
        lines = (line.strip() for line in content.splitlines())
        content = '\n'.join(line for line in lines if line)

        return {
            'url': url,
            'title': title,
            'content': content,
            'html': str(main_content) if main_content else html
        }

    def extract_all_page_content(self, html: str, url: str) -> Dict[str, any]:
        """Extract all relevant content from a page"""
        extracted = self.extract_content_from_html(html, url)

        # Additional extraction for metadata
        soup = BeautifulSoup(html, 'html.parser')

        # Extract metadata
        metadata = {
            'url': url,
            'title': extracted['title'],
            'description': '',
            'tags': []
        }

        # Find meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '')

        # Find other meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            if name and 'title' not in name.lower() and 'description' not in name.lower():
                content = meta.get('content', '')
                if content:
                    metadata['tags'].append(f"{name}: {content}")

        return {
            'content': extracted['content'],
            'metadata': metadata,
            'title': extracted['title']
        }