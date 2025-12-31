"""Script to ingest all documentation pages for all 4 modules from the sitemap and store in Qdrant"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Add the backend directory to the path so we can import our modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.web_scraper import WebScraperService
from services.content_extractor import ContentExtractorService
from services.content_cleaner import ContentCleanerService
from services.content_chunker import ContentChunkerService
from services.embedding_generator import EmbeddingGeneratorService
from services.vector_storage import VectorStorageService
from models import BookContent, Metadata, VectorRecord

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_all_module_urls(sitemap_url: str) -> List[str]:
    """Extract URLs for all 4 modules from sitemap that match the /docs/module-[1-4]/ pattern"""
    try:
        logger.info(f"Fetching sitemap from: {sitemap_url}")
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'xml')
        urls = []

        for loc in soup.find_all('loc'):
            url = loc.text.strip()

            # Only include documentation routes for modules 1-4
            if '/docs/module-' in url:
                # Check if it's one of the 4 modules
                for module_num in range(1, 5):  # Modules 1, 2, 3, 4
                    if f'/docs/module-{module_num}/' in url:
                        # Additional filtering to exclude unwanted paths
                        parsed_url = urlparse(url)
                        path = parsed_url.path

                        # Exclude blog, tags, archive, and other non-docs routes
                        excluded_patterns = ['/blog', '/tags', '/archive', '/supporters', '/team', '/changelog']
                        if not any(pattern in path for pattern in excluded_patterns):
                            # Fix domain - replace any old domain with the correct one
                            fixed_url = url.replace('my-book-efxlpl0go-sajida-haiders-projects.vercel.app', 'rag-book-ten.vercel.app')
                            fixed_url = fixed_url.replace('rag-book-qwxt6rjup-sajida-haiders-projects.vercel.app', 'rag-book-ten.vercel.app')
                            urls.append(fixed_url)
                            break  # Found a matching module, no need to check other module numbers

        logger.info(f"Found {len(urls)} module documentation URLs from sitemap")

        # Sort URLs by module and chapter for organized processing
        urls.sort()
        for i, url in enumerate(urls):
            logger.info(f"  {i+1}. {url}")

        return urls
    except Exception as e:
        logger.error(f"Error fetching sitemap: {e}")
        return []

def main():
    """Main function to ingest all module documentation pages from sitemap"""
    logger.info("Starting documentation ingestion for all 4 modules...")

    # Get sitemap URL from environment or use default
    sitemap_url = os.getenv("SITEMAP_URL", "https://rag-book-ten.vercel.app/sitemap.xml")
    logger.info(f"Using sitemap URL: {sitemap_url}")

    try:
        # Initialize services
        scraper = WebScraperService(delay=0.5)
        extractor = ContentExtractorService()
        cleaner = ContentCleanerService()
        chunker = ContentChunkerService(max_chunk_size=1000, overlap=100)
        embedding_service = EmbeddingGeneratorService()
        storage_service = VectorStorageService()

        # Get URLs for all 4 modules from sitemap
        urls = get_all_module_urls(sitemap_url)

        if not urls:
            logger.warning("No module documentation URLs found in sitemap")
            return

        # Process each URL
        all_book_content = []
        failed_pages = []
        total_chunks_created = 0
        total_vectors_stored = 0

        for i, url in enumerate(urls):
            logger.info(f"Processing page {i+1}/{len(urls)}: {url}")

            try:
                # Load fully rendered HTML using the scraper
                page_html = scraper.fetch_page(url)

                if not page_html:
                    logger.warning(f"Failed to fetch content from {url}")
                    failed_pages.append((url, "Failed to fetch HTML"))
                    continue

                # Extract the full visible chapter content
                extracted_content = extractor.extract_all_page_content(page_html, url)

                # Clean the content
                cleaned_content, is_valid = cleaner.clean_and_validate(extracted_content['content'])

                if not is_valid or not cleaned_content.strip():
                    logger.warning(f"Content from {url} is empty or invalid for processing (length: {len(cleaned_content)})")
                    failed_pages.append((url, "Empty or invalid content"))
                    continue

                # Log verification details
                logger.info(f"  - Rendered HTML length: {len(page_html)} characters")
                logger.info(f"  - Extracted text length: {len(extracted_content['content'])} characters")
                logger.info(f"  - Cleaned text length: {len(cleaned_content)} characters")

                # Create BookContent object with metadata
                book_content = BookContent(
                    url=url,
                    title=extracted_content['title'],
                    content=cleaned_content,
                    section=extracted_content['metadata'].get('title', ''),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                # Chunk the content preserving metadata
                chunks = chunker.chunk_book_content(book_content)

                logger.info(f"  - Number of chunks created: {len(chunks)}")

                # Store each chunk in Qdrant
                chunks_stored = 0
                for j, (chunk_text, chunk_metadata) in enumerate(chunks):
                    import uuid
                    chunk_uuid = str(uuid.uuid4())

                    # Generate embedding for the chunk
                    embedding = embedding_service.generate_embedding(
                        text=chunk_text,
                        chunk_id=chunk_uuid
                    )

                    # Create metadata for the vector record
                    metadata = Metadata(
                        source_url=url,
                        page_title=extracted_content['title'],
                        section_info=extracted_content['metadata'].get('title', ''),
                        chunk_index=chunk_metadata['chunk_index'],
                        total_chunks=len(chunks),
                        created_at=datetime.now()
                    )

                    # Create vector record with proper UUID
                    record_id = str(uuid.uuid4())
                    vector_record = VectorRecord(
                        id=record_id,
                        payload={
                            'url': metadata.source_url,
                            'title': metadata.page_title,
                            'section': metadata.section_info,
                            'content': chunk_text,
                            'chunk_index': metadata.chunk_index,
                            'total_chunks': metadata.total_chunks,
                            'created_at': datetime.now().isoformat()
                        },
                        vector=embedding.vector,
                        created_at=datetime.now()
                    )

                    # Store in Qdrant
                    success = storage_service.store_embedding(vector_record)

                    if success:
                        chunks_stored += 1
                        total_vectors_stored += 1
                    else:
                        logger.warning(f"Failed to store chunk {j+1} for {url}")

                logger.info(f"  - Qdrant insert status: {chunks_stored}/{len(chunks)} chunks stored")

                total_chunks_created += len(chunks)
                all_book_content.append(book_content)

                # Log successful processing
                logger.info(f"  ✓ Successfully processed: {url}")

            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                failed_pages.append((url, str(e)))
                continue

            # Small delay between requests to be respectful to the server
            time.sleep(0.5)

        # Print deterministic summary
        logger.info("\n" + "="*60)
        logger.info("MODULES INGESTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total pages processed: {len(all_book_content)}")
        logger.info(f"Pages skipped (empty or invalid): {len(failed_pages)}")
        logger.info(f"Total chunks created: {total_chunks_created}")
        logger.info(f"Total vectors stored: {total_vectors_stored}")
        logger.info(f"Storage collection: {os.getenv('COLLECTION_NAME', 'humanoid_ai_book')}")

        if failed_pages:
            logger.info("\nFailed/skipped pages:")
            for url, error in failed_pages[:10]:  # Show first 10 failures
                logger.info(f"  - {url}: {error}")
            if len(failed_pages) > 10:
                logger.info(f"  ... and {len(failed_pages) - 10} more failures")

        logger.info("="*60)
        logger.info("All modules documentation ingestion completed!")

    except Exception as e:
        logger.error(f"Error in ingestion process: {e}")
        raise

if __name__ == "__main__":
    main()