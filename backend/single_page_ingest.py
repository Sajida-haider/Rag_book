"""Script to ingest content from just the main page of your book"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(__file__))

from services.web_scraper import WebScraperService
from services.content_extractor import ContentExtractorService
from services.content_cleaner import ContentCleanerService
from services.embedding_generator import EmbeddingGeneratorService
from services.vector_storage import VectorStorageService
from models import BookContent, Metadata, VectorRecord
import uuid

def main():
    print("Starting ingestion from main page only...")

    # Initialize services
    scraper = WebScraperService(delay=0.5)
    extractor = ContentExtractorService()
    cleaner = ContentCleanerService()
    embedding_service = EmbeddingGeneratorService()
    storage_service = VectorStorageService()

    # Use only the main page URL
    book_url = "https://rag-book-ten.vercel.app"

    print(f"Fetching content from: {book_url}")

    # Fetch the main page
    page_html = scraper.fetch_page(book_url)
    if not page_html:
        print(f"Failed to fetch content from {book_url}")
        return

    print("Page fetched successfully")

    # Extract content from HTML
    extracted_content = extractor.extract_all_page_content(page_html, book_url)

    # Clean the content
    cleaned_content, is_valid = cleaner.clean_and_validate(extracted_content['content'])
    if not is_valid:
        print(f"Content from {book_url} is not valid for processing")
        return

    print(f"Content extracted and cleaned ({len(cleaned_content)} characters)")

    # Create BookContent object
    book_content = BookContent(
        url=book_url,
        title=extracted_content['title'],
        content=cleaned_content,
        section=extracted_content['metadata'].get('title', ''),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    print("Content chunking...")
    # Simple chunking for the single page content
    chunk_size = 1000
    content_chunks = []

    if len(book_content.content) <= chunk_size:
        content_chunks.append((book_content.content, {'chunk_index': 0}))
    else:
        # Split into chunks
        for i in range(0, len(book_content.content), chunk_size):
            chunk_text = book_content.content[i:i + chunk_size]
            content_chunks.append((chunk_text, {'chunk_index': i // chunk_size}))

    print(f"Created {len(content_chunks)} chunks")

    # Process each chunk
    vector_records = []
    for i, (chunk_text, chunk_metadata) in enumerate(content_chunks):
        print(f"Processing chunk {i+1}/{len(content_chunks)}")

        # Generate embedding for the chunk
        embedding = embedding_service.generate_embedding(
            text=chunk_text,
            chunk_id=f"chunk_{i}"
        )

        # Create metadata for the vector record
        metadata = Metadata(
            source_url=book_content.url,
            page_title=book_content.title,
            section_info=book_content.section,
            chunk_index=chunk_metadata['chunk_index'],
            total_chunks=len(content_chunks),
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

        vector_records.append(vector_record)

    print(f"Generated embeddings for {len(vector_records)} chunks")

    # Store embeddings in Qdrant
    print("Storing embeddings in Qdrant...")
    success_count = 0

    for i, record in enumerate(vector_records):
        print(f"Storing record {i+1}/{len(vector_records)}")
        success = storage_service.store_embedding(record)
        if success:
            success_count += 1

    print(f"Successfully stored {success_count} out of {len(vector_records)} embeddings")

    print("\n--- Ingestion Summary ---")
    print(f"Pages processed: 1")
    print(f"Content chunks created: {len(content_chunks)}")
    print(f"Embeddings generated: {len(vector_records)}")
    print(f"Embeddings stored: {success_count}")
    print(f"Storage collection: humanoid_ai_book")
    print("--------------------------")

if __name__ == "__main__":
    main()