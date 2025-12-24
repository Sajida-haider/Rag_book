import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BOOK_URL = "https://rag-book-three.vercel.app"

def test_discover_urls():
    urls = set()
    sitemap_url = BOOK_URL.rstrip('/') + '/sitemap.xml'
    print(f"Trying to access sitemap at: {sitemap_url}")

    try:
        response = requests.get(sitemap_url)
        print(f"Sitemap response status: {response.status_code}")

        if response.status_code == 200:
            # Try to parse as XML, fall back to html parser if needed
            try:
                soup = BeautifulSoup(response.content, 'xml')
            except:
                # If xml parser is not available, try html parser which can handle XML
                soup = BeautifulSoup(response.content, 'html.parser')

            print(f"Found {len(soup.find_all('loc'))} <loc> tags in sitemap")

            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                print(f"Raw URL from sitemap: {url}")

                # Handle sitemap URLs that might be from a different domain (e.g., old deployment URLs)
                if url.startswith('http'):
                    # Extract the path from the sitemap URL and reconstruct with current BOOK_URL
                    parsed_url = urlparse(url)
                    path = parsed_url.path
                    query = parsed_url.query

                    # Create the URL using our BOOK_URL base with the path from the sitemap
                    # This handles cases where the sitemap has old/deployed URLs
                    if path:
                        final_url = BOOK_URL.rstrip('/') + path
                        if query:
                            final_url += '?' + query
                        urls.add(final_url)
                        print(f"Processed URL: {final_url}")

            print(f"Processed sitemap, found {len(urls)} URLs")
        else:
            print(f"No sitemap found (status {response.status_code}), will crawl")
    except Exception as e:
        print(f"Sitemap access failed: {str(e)}")

    if not urls:
        print("No URLs found from sitemap, trying crawling...")
        to_visit = [BOOK_URL]
        visited = set()
        while to_visit and len(visited) < 10:  # Limit to 10 for testing
            current_url = to_visit.pop(0)
            # Check if the current URL is from the same domain as BOOK_URL
            current_domain = current_url.lstrip('https://').split('/')[0]
            book_domain = BOOK_URL.lstrip('https://').split('/')[0]
            if current_url in visited or current_domain != book_domain:
                continue
            visited.add(current_url)
            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    urls.add(current_url)
                    print(f"Added URL from crawling: {current_url}")
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(current_url, href)
                        # Check if the full_url is from the same domain as BOOK_URL
                        full_domain = full_url.lstrip('https://').split('/')[0]
                        book_domain = BOOK_URL.lstrip('https://').split('/')[0]
                        if full_domain == book_domain and full_url not in visited and full_url not in to_visit:
                            to_visit.append(full_url)
                            if len(to_visit) > 10:  # Limit for testing
                                break
            except Exception as e:
                print(f"Error crawling {current_url}: {str(e)}")
                continue

    print(f"Final discovered URLs: {list(urls)}")
    return list(urls)

if __name__ == "__main__":
    test_discover_urls()