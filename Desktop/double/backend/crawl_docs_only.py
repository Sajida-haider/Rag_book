"""Script to crawl only docs pages from the specific domain as per strict requirements"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit
import time
import re

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
            soup.find('div', class_=lambda x: x and ('doc' in x.lower() or 'content' in x.lower())) or
            soup.body
        )

        if main_content:
            # Extract all text content, preserving paragraph structure
            content_parts = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'section', 'article', 'pre', 'code']):
                # Skip elements that are likely navigation or UI controls
                classes = element.get('class', [])
                if any(skip_class in ' '.join(classes).lower() for skip_class in ['nav', 'menu', 'sidebar', 'footer', 'header', 'cookie', 'banner', 'toc']):
                    continue

                text = element.get_text().strip()
                if text and len(text) > 5:  # Filter out very short text fragments
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

def get_all_links_on_page(url):
    """Get all links from a page that belong to the same domain and start with /docs/"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        base_domain = 'rag-book-ten.vercel.app'
        docs_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Join relative URLs with the base URL
            full_url = urljoin(url, href)

            # Parse the URL to check domain and path
            parsed = urlparse(full_url)

            # Check if it's the same domain and starts with /docs/
            if parsed.netloc == base_domain and parsed.path.startswith('/docs/'):
                # Make sure it's not a file extension like .pdf, .jpg, etc.
                if not any(parsed.path.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.zip', '.exe']):
                    docs_links.append(full_url)

        # Remove duplicates while preserving order
        unique_links = []
        for link in docs_links:
            if link not in unique_links:
                unique_links.append(link)

        return unique_links

    except Exception as e:
        print(f"Error getting links from {url}: {e}")
        return []

def crawl_docs_pages(base_url):
    """Crawl docs pages starting from the base URL"""
    print(f"Starting crawl from: {base_url}")

    # Get all links from the main page that lead to docs
    docs_links = get_all_links_on_page(base_url)
    print(f"Found {len(docs_links)} docs links on main page")

    # Also check the /docs/ page directly
    docs_base_url = base_url.rstrip('/') + '/docs/'
    try:
        docs_base_links = get_all_links_on_page(docs_base_url)
        print(f"Found {len(docs_base_links)} docs links on /docs/ page")
        docs_links.extend(docs_base_links)

        # Remove duplicates
        docs_links = list(dict.fromkeys(docs_links))  # Preserve order while deduplicating
    except:
        print(f"/docs/ page not accessible or doesn't exist")

    print(f"Total unique docs links found: {len(docs_links)}")

    for link in docs_links:
        print(f"  - {link}")

    return docs_links

def main():
    base_url = "https://rag-book-ten.vercel.app"
    print(f"Searching for docs pages under domain: {base_url}")

    # Find all docs pages on the domain
    docs_pages = crawl_docs_pages(base_url)

    # Add the homepage if it exists
    homepage_content = extract_content_from_page(base_url)
    if homepage_content:
        print(f"Found homepage content with {len(homepage_content)} characters")

    print(f"\nAttempting to extract content from {len(docs_pages)} docs pages:")

    # Extract content from each docs page
    all_content = []

    # Add homepage content first
    if homepage_content:
        all_content.append({
            'url': base_url,
            'title': 'Homepage',
            'content': homepage_content
        })

    for i, page_url in enumerate(docs_pages, 1):
        print(f"\n{i}. Extracting content from: {page_url}")
        content = extract_content_from_page(page_url)
        if content and len(content) > 50:  # Only add if content is substantial
            all_content.append({
                'url': page_url,
                'title': page_url.split('/')[-1] or 'index',
                'content': content
            })
            print(f"   Extracted {len(content)} characters")
        else:
            print(f"   Failed to extract content or content too short")

    print(f"\nTotal pages processed: {len(all_content)}")

    # Save content to file for verification
    with open('docs_extracted_content.txt', 'w', encoding='utf-8') as f:
        for item in all_content:
            f.write(f"URL: {item['url']}\n")
            f.write(f"TITLE: {item['title']}\n")
            f.write(f"CONTENT:\n{item['content'][:1000]}...\n")  # First 1000 chars
            f.write("=" * 80 + "\n")

    print("Content saved to docs_extracted_content.txt")

    return all_content

if __name__ == "__main__":
    main()