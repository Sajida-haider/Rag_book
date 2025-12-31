"""Script to explore possible accessible paths on your domain"""

import requests
from urllib.parse import urljoin
import time

def check_path(base_url, path):
    """Check if a specific path is accessible"""
    url = base_url.rstrip('/') + '/' + path.lstrip('/')
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code, len(response.text) if response.status_code == 200 else 0
    except:
        return None, 0

def main():
    base_url = "https://rag-book-ten.vercel.app"

    # Common paths to try
    paths_to_try = [
        "",
        "docs",
        "docs/",
        "blog",
        "blog/",
        "posts",
        "posts/",
        "articles",
        "articles/",
        "guide",
        "guide/",
        "tutorial",
        "tutorial/",
        "manual",
        "manual/",
        "book",
        "book/",
        "content",
        "content/",
        "pages",
        "pages/",
        "learn",
        "learn/",
        "reference",
        "reference/",
        "api",
        "api/",
        "examples",
        "examples/",
        "chapters",
        "chapters/",
        "modules",
        "modules/"
    ]

    print(f"Exploring paths on: {base_url}")
    print("Status | Size  | Path")
    print("-" * 30)

    accessible_paths = []

    for path in paths_to_try:
        status, size = check_path(base_url, path)
        if status == 200:
            print(f"[OK] 200  | {size:4d} | /{path}")
            accessible_paths.append((path, size))
        elif status == 404:
            print(f"[404]     |      | /{path}")
        else:
            print(f"[{status}] |      | /{path}")

        # Be respectful to the server
        time.sleep(0.5)

    print(f"\nFound {len(accessible_paths)} accessible paths:")
    for path, size in accessible_paths:
        print(f"  - {base_url}/{path} ({size} chars)")

if __name__ == "__main__":
    main()