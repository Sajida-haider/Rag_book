"""Main ingestion pipeline for book embeddings RAG system"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import services directly - each service file handles its own path setup
from services.web_scraper import WebScraperService
from services.content_extractor import ContentExtractorService
from services.content_cleaner import ContentCleanerService
from services.url_crawler import URLCrawlerService
from services.content_chunker import ContentChunkerService
from services.embedding_generator import EmbeddingGeneratorService
from services.vector_storage import VectorStorageService
from services.change_detector import ChangeDetectorService
from services.re_ingestion import ReIngestionService
from models import BookContent, Metadata, VectorRecord


def main():
    """Main function to orchestrate the full ingestion pipeline"""
    logger.info("Starting book content ingestion pipeline...")

    try:
        # Initialize services
        scraper = WebScraperService(delay=0.5)
        extractor = ContentExtractorService()
        cleaner = ContentCleanerService()
        crawler = URLCrawlerService(base_url=os.getenv("BOOK_URL", "https://rag-book-ten.vercel.app"), delay=0.5)
        chunker = ContentChunkerService(max_chunk_size=1000, overlap=100)
        embedding_service = EmbeddingGeneratorService()
        storage_service = VectorStorageService()
        change_detector = ChangeDetectorService()
        re_ingestion_service = ReIngestionService()

        # Get book URL from environment or use default
        book_url = os.getenv("BOOK_URL", "https://rag-book-ten.vercel.app")
        logger.info(f"Fetching content from: {book_url}")

        # Check if this is a re-ingestion run
        is_reingestion = len(sys.argv) > 1 and sys.argv[1] == "reingest"
        logger.info(f"Mode: {'Re-ingestion' if is_reingestion else 'Initial ingestion'}")

        # Step 1: Crawl the book website to discover all pages
        logger.info("Crawling book website to discover pages...")
        urls = crawler.crawl_with_sitemap(max_pages=50)  # Limit to 50 pages for initial implementation
        logger.info(f"Discovered {len(urls)} pages")

        # Step 2: Extract content from each page
        all_book_content = []
        failed_pages = []

        for i, url in enumerate(urls):
            logger.info(f"Processing page {i+1}/{len(urls)}: {url}")

            # Fetch page content
            page_html = scraper.fetch_page(url)
            if not page_html:
                logger.warning(f"Failed to fetch content from {url}")
                failed_pages.append((url, "Failed to fetch HTML"))
                continue

            # Extract content from HTML
            extracted_content = extractor.extract_all_page_content(page_html, url)

            # Clean the content
            cleaned_content, is_valid = cleaner.clean_and_validate(extracted_content['content'])
            if not is_valid:
                logger.warning(f"Content from {url} is not valid for processing")
                failed_pages.append((url, "Content validation failed"))
                continue

            # Log verification details
            logger.info(f"  - HTML length: {len(page_html)} characters")
            logger.info(f"  - Extracted content length: {len(extracted_content['content'])} characters")
            logger.info(f"  - Cleaned content length: {len(cleaned_content)} characters")

            # Create BookContent object
            book_content = BookContent(
                url=url,
                title=extracted_content['title'],
                content=cleaned_content,
                section=extracted_content['metadata'].get('title', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            all_book_content.append(book_content)

            # Log successful processing
            logger.info(f"  - Successfully processed: {url}")

        # Log processing summary before proceeding
        logger.info(f"Successfully processed {len(all_book_content)} pages, {len(failed_pages)} pages failed")

        logger.info(f"Successfully extracted content from {len(all_book_content)} pages")

        if is_reingestion:
            # Re-ingestion mode: detect changes and only process changed content
            logger.info("Running in re-ingestion mode...")
            stats = re_ingestion_service.update_content(all_book_content)

            logger.info("\n--- Re-Ingestion Summary ---")
            logger.info(f"Added: {stats['added']}")
            logger.info(f"Modified: {stats['modified']}")
            logger.info(f"Removed: {stats['removed']}")
            logger.info(f"Unchanged: {stats['unchanged']}")
            logger.info(f"Storage collection: {os.getenv('COLLECTION_NAME', 'humanoid_ai_book')}")
            logger.info("--------------------------")
        else:
            # Initial ingestion mode: process all content
            # Step 3: Chunk the content
            logger.info("Chunking content for embedding...")
            all_chunks = []
            chunk_id = 0

            for book_content in all_book_content:
                chunks = chunker.chunk_book_content(book_content)
                for chunk_text, chunk_metadata in chunks:
                    import uuid
                    chunk_uuid = str(uuid.uuid4())
                    all_chunks.append({
                        'text': chunk_text,
                        'metadata': chunk_metadata,
                        'chunk_id': chunk_uuid,
                        'book_content': book_content
                    })
                    chunk_id += 1

            logger.info(f"Created {len(all_chunks)} content chunks")

            # Step 4: Generate embeddings for each chunk
            logger.info("Generating embeddings...")
            vector_records = []

            for i, chunk_info in enumerate(all_chunks):
                logger.info(f"Processing chunk {i+1}/{len(all_chunks)}")

                # Generate embedding for the chunk
                embedding = embedding_service.generate_embedding(
                    text=chunk_info['text'],
                    chunk_id=chunk_info['chunk_id']
                )

                # Create metadata for the vector record
                metadata = Metadata(
                    source_url=chunk_info['book_content'].url,
                    page_title=chunk_info['book_content'].title,
                    section_info=chunk_info['book_content'].section,
                    chunk_index=chunk_info['metadata']['chunk_index'],
                    total_chunks=len([c for c in all_chunks if c['book_content'] == chunk_info['book_content']]),  # Count chunks for this book content
                    created_at=datetime.now()
                )

                # Create vector record with proper UUID
                import uuid
                record_id = str(uuid.uuid4())  # Generate a proper UUID
                vector_record = VectorRecord(
                    id=record_id,
                    payload={
                        'url': metadata.source_url,
                        'title': metadata.page_title,
                        'section': metadata.section_info,
                        'content': chunk_info['text'],
                        'chunk_index': metadata.chunk_index,
                        'total_chunks': metadata.total_chunks,
                        'created_at': datetime.now().isoformat()
                    },
                    vector=embedding.vector,
                    created_at=datetime.now()
                )

                vector_records.append(vector_record)

            logger.info(f"Generated embeddings for {len(vector_records)} chunks")

            # Step 5: Store embeddings in Qdrant
            logger.info("Storing embeddings in Qdrant...")

            # Use batch storage for better performance
            success = storage_service.store_embeddings_batch(vector_records)
            if success:
                success_count = len(vector_records)
            else:
                # Fallback to individual storage if batch fails
                logger.warning("Batch storage failed, falling back to individual storage...")
                success_count = 0
                for i, record in enumerate(vector_records):
                    logger.info(f"Storing record {i+1}/{len(vector_records)}")
                    record_success = storage_service.store_embedding(record)
                    if record_success:
                        success_count += 1

            logger.info(f"Successfully stored {success_count} out of {len(vector_records)} embeddings")

            # Save content hashes for future re-ingestion
            re_ingestion_service.save_current_hashes(all_book_content)

            # Step 6: Summary
            logger.info("\n--- Ingestion Summary ---")
            logger.info(f"Pages processed: {len(all_book_content)}")
            logger.info(f"Content chunks created: {len(all_chunks)}")
            logger.info(f"Embeddings generated: {len(vector_records)}")
            logger.info(f"Embeddings stored: {success_count}")
            logger.info(f"Storage collection: {os.getenv('COLLECTION_NAME', 'humanoid_ai_book')}")
            logger.info("--------------------------")

        logger.info("Book content ingestion pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Error in ingestion pipeline: {e}")
        raise


if __name__ == "__main__":
    main()