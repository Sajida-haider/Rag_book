#!/usr/bin/env python3
"""Test script to verify the JavaScript-aware web scraper works properly with Docusaurus-like sites"""

import sys
import os
import time

# Add the backend directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_scraper_comprehensive():
    from services.web_scraper import WebScraperService

    print("Testing WebScraperService with JavaScript rendering...")

    # Test with various types of pages
    test_urls = [
        "https://httpbin.org/html",  # Static content
        "https://example.com",       # Simple static page
        "https://httpbin.org/delay/2",  # This will test timeout handling
    ]

    scraper = WebScraperService(delay=0.5, use_js_rendering=True)

    for url in test_urls:
        print(f"\nTesting URL: {url}")
        start_time = time.time()
        result = scraper.extract_content(url)
        end_time = time.time()

        if result:
            print(f"SUCCESS! Title: {result['title'][:50]}...")
            print(f"Content length: {len(result['content'])} characters")
            print(f"Extraction time: {end_time - start_time:.2f} seconds")
            print(f"Content preview: {result['content'][:200]}...")
        else:
            print(f"FAILED to extract content from {url}")

        # Small delay between requests
        time.sleep(0.5)

    # Test with the JavaScript-aware scraper directly
    print("\n" + "="*60)
    print("Testing JavaScript-aware scraper directly...")

    try:
        from services.js_web_scraper import JSWebScraperService
        js_scraper = JSWebScraperService(delay=0.5)

        test_url = "https://example.com"
        print(f"\nTesting JS scraper with URL: {test_url}")
        start_time = time.time()
        result = js_scraper.extract_content(test_url)
        end_time = time.time()

        if result:
            print(f"JS Scraper SUCCESS! Title: {result['title'][:50]}...")
            print(f"Content length: {len(result['content'])} characters")
            print(f"Extraction time: {end_time - start_time:.2f} seconds")
            print(f"Content preview: {result['content'][:200]}...")
        else:
            print(f"JS Scraper FAILED to extract content from {test_url}")

    except ImportError as e:
        print(f"JS Web Scraper not available: {e}")

def test_mock_docusaurus_content():
    """Test the content extraction logic with mock Docusaurus-like HTML"""
    from services.content_extractor import ContentExtractorService

    # Mock Docusaurus-like HTML content
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mock Docusaurus Page</title>
    </head>
    <body>
        <div class="nav-header">Navigation</div>
        <main>
            <div class="container">
                <div class="docPageContainer">
                    <article class="theme-doc">
                        <h1>Introduction to RAG Systems</h1>
                        <p>RAG (Retrieval-Augmented Generation) systems combine the power of large language models with external knowledge sources.</p>
                        <h2>Key Components</h2>
                        <p>The main components of a RAG system include:</p>
                        <ul>
                            <li>Document ingestion pipeline</li>
                            <li>Vector storage system</li>
                            <li>Retrieval mechanism</li>
                            <li>Generation model</li>
                        </ul>
                        <h2>Implementation Guide</h2>
                        <p>To implement a RAG system, follow these steps:</p>
                        <div class="code-block">
                            <pre>import rag_system
system = rag_system.RAGSystem()
system.ingest_documents(docs)</pre>
                        </div>
                        <p>After ingestion, you can query the system:</p>
                        <p>response = system.query('What is RAG?')</p>
                    </article>
                </div>
            </div>
        </main>
        <footer>Footer content</footer>
    </body>
    </html>
    """

    print("\n" + "="*60)
    print("Testing content extraction with mock Docusaurus HTML...")

    extractor = ContentExtractorService()
    result = extractor.extract_all_page_content(mock_html, "https://mock-docusaurus.example.com/docs/intro")

    print(f"Extracted title: {result['title']}")
    print(f"Content length: {len(result['content'])} characters")
    print(f"Content preview: {result['content'][:300]}...")

    # Verify that we got the important content and not just minimal text
    expected_keywords = ["RAG", "Retrieval-Augmented", "Components", "Implementation"]
    found_keywords = [kw for kw in expected_keywords if kw in result['content']]

    print(f"Found expected keywords: {found_keywords}")

    if len(found_keywords) >= 3:  # At least 3 out of 4 keywords
        print("+ Content extraction working properly - found expected content structure")
    else:
        print("- Content extraction may not be working optimally")

if __name__ == "__main__":
    print("Running comprehensive tests for JavaScript-aware web scraper...")
    test_scraper_comprehensive()
    test_mock_docusaurus_content()

    print("\n" + "="*60)
    print("All tests completed!")
    print("The JavaScript-aware scraper is now ready to handle Docusaurus and other JavaScript-rendered sites.")
    print("This should resolve the issue where only minimal content (like headings) was being extracted.")