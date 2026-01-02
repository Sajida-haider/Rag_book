"""Script to crawl only pages from the specific domain as per strict requirements"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

def is_valid_url(url, base_domain):
    """Check if URL belongs to the specific domain and starts with correct path"""
    parsed = urlparse(url)
    return (
        parsed.netloc == urlparse(base_domain).netloc and
        url.startswith(base_domain + '/docs/')
    )

def extract_content_from_page(url):
    """Extract full readable text content from a page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Try to find main content area (common selectors for Docusaurus sites)
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'container|wrapper|content|doc|main', re.I)) or
            soup.find('div', {'role': 'main'}) or
            soup.body
        )

        if main_content:
            # Extract all text content, preserving paragraph structure
            content_parts = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'section', 'article']):
                # Skip elements that are likely navigation or UI controls
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

        return content.strip()

    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def find_docs_pages(base_url):
    """Find pages under /docs/ path on the specific domain"""
    docs_pages = []

    # Try common Docusaurus docs paths
    common_paths = [
        "/docs",
        "/docs/",
        "/docs/intro",
        "/docs/getting-started",
        "/docs/installation",
        "/docs/configuration",
        "/docs/api",
        "/docs/guide",
        "/docs/tutorial",
        "/docs/reference",
        "/docs/concepts",
        "/docs/modules",
        "/docs/examples"
    ]

    for path in common_paths:
        url = base_url.rstrip('/') + path
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(url, headers=headers, timeout=10)
            if response.status_code == 200:
                docs_pages.append(url)
                print(f"Found: {url}")
        except:
            pass  # URL doesn't exist, continue

    return docs_pages

def main():
    base_url = "https://rag-book-ten.vercel.app"
    print(f"Searching for pages under: {base_url}/docs/")

    # Find available docs pages
    docs_pages = find_docs_pages(base_url)

    # Add the homepage if it exists
    try:
        response = requests.head(base_url, timeout=10)
        if response.status_code == 200:
            print(f"Found: {base_url}")
            docs_pages.append(base_url)
    except:
        pass

    print(f"\nFound {len(docs_pages)} pages to process:")
    for page in docs_pages:
        print(f"  - {page}")

    # Extract content from each page
    all_content = []
    for page_url in docs_pages:
        print(f"\nExtracting content from: {page_url}")
        content = extract_content_from_page(page_url)
        if content:
            all_content.append({
                'url': page_url,
                'title': page_url.split('/')[-1] or 'homepage',
                'content': content
            })
            print(f"  Extracted {len(content)} characters")
        else:
            print(f"  Failed to extract content")

    print(f"\nTotal pages processed: {len(all_content)}")

    # Save content to file for verification
    with open('extracted_content.txt', 'w', encoding='utf-8') as f:
        for item in all_content:
            f.write(f"URL: {item['url']}\n")
            f.write(f"TITLE: {item['title']}\n")
            f.write(f"CONTENT:\n{item['content']}\n")
            f.write("-" * 80 + "\n")

    print("Content saved to extracted_content.txt")

    return all_content

if __name__ == "__main__":
    main()