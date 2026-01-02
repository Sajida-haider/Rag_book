"""Script to extract links from the main page of your book and test their accessibility"""

import requests
from bs4 import BeautifulSoup
import time

def extract_links_from_page(url):
    """Extract all internal links from the main page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        base_domain = "rag-book-ten.vercel.app"
        internal_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Handle relative URLs that start with /
            if href.startswith('/'):
                full_url = f"https://{base_domain}{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                continue  # Skip anchor links and other types

            # Only include links from the same domain and exclude file types
            if base_domain in full_url:
                # Exclude external links or file downloads
                if not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.css', '.js']):
                    if full_url not in internal_links:
                        internal_links.append(full_url)

        return internal_links

    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return []

def test_link_accessibility(url):
    """Test if a link is accessible"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10)
        return response.status_code
    except:
        return None

def main():
    base_url = "https://rag-book-ten.vercel.app"

    print(f"Extracting links from: {base_url}")
    all_links = extract_links_from_page(base_url)

    print(f"\nFound {len(all_links)} links on the main page:")
    for link in all_links:
        print(f"  - {link}")

    print(f"\nTesting accessibility of links...")
    accessible_links = []

    for i, link in enumerate(all_links, 1):
        print(f"Testing {i}/{len(all_links)}: {link}", end="... ")
        status_code = test_link_accessibility(link)
        if status_code == 200:
            print(f"[OK] {status_code}")
            accessible_links.append(link)
        elif status_code == 404:
            print(f"[404] {status_code}")
        elif status_code:
            print(f"[{status_code}]")
        else:
            print("[ERROR]")

        # Be respectful to the server
        time.sleep(0.5)

    print(f"\nSUMMARY:")
    print(f"Total links found: {len(all_links)}")
    print(f"Accessible links: {len(accessible_links)}")

    print(f"\nAccessible links:")
    for link in accessible_links:
        print(f"  - {link}")

    # Save accessible links to file
    with open('accessible_links.txt', 'w') as f:
        f.write(f"Accessible links on {base_url}\n")
        f.write(f"Total: {len(accessible_links)} links\n\n")
        for link in accessible_links:
            f.write(f"{link}\n")

    print(f"\nResults saved to accessible_links.txt")

if __name__ == "__main__":
    main()