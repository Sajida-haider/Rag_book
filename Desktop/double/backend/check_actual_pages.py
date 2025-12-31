"""Script to check which pages actually exist on your domain"""

import requests
from bs4 import BeautifulSoup
import time

def check_page_exists(url):
    """Check if a page exists by making a HEAD request"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def extract_links_from_homepage(url):
    """Extract all internal links from the homepage"""
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

            # Handle relative URLs
            if href.startswith('/'):
                full_url = f"https://{base_domain}{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                continue  # Skip anchor links and other types

            # Only include links from the same domain
            if base_domain in full_url:
                # Exclude external links or file downloads
                if not any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.css', '.js']):
                    if full_url not in internal_links:
                        internal_links.append(full_url)

        return internal_links

    except Exception as e:
        print(f"Error extracting links from homepage: {e}")
        return []

def main():
    base_url = "https://rag-book-ten.vercel.app"

    print(f"Checking which pages actually exist on: {base_url}")

    # Get all links from homepage
    print("Extracting links from homepage...")
    all_links = extract_links_from_homepage(base_url)

    print(f"Found {len(all_links)} potential links on homepage")

    # Check which links actually exist
    print("\nChecking which links are accessible...")
    accessible_pages = []

    for i, link in enumerate(all_links, 1):
        print(f"Checking {i}/{len(all_links)}: {link}", end="... ")
        if check_page_exists(link):
            accessible_pages.append(link)
            print("[OK] EXISTS")
        else:
            print("[404] 404")

        # Be respectful to the server
        time.sleep(0.5)

    print(f"\nSUMMARY:")
    print(f"Total links found on homepage: {len(all_links)}")
    print(f"Accessible pages: {len(accessible_pages)}")

    print(f"\nAccessible pages:")
    for page in accessible_pages:
        print(f"  - {page}")

    # Save accessible pages to file
    with open('accessible_pages.txt', 'w') as f:
        f.write(f"Accessible pages on {base_url}\n")
        f.write(f"Total: {len(accessible_pages)} pages\n\n")
        for page in accessible_pages:
            f.write(f"{page}\n")

    print(f"\nResults saved to accessible_pages.txt")

if __name__ == "__main__":
    main()