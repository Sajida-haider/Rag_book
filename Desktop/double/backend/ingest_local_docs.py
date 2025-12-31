"""Script to ingest local documentation markdown files for all 4 modules from local files and store in Qdrant"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging
import glob
from pathlib import Path
import re
import hashlib

# Add the backend directory to the path so we can import our modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

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

def get_local_markdown_files(docs_path: str) -> List[str]:
    """Get all markdown files from the local docs directory"""
    pattern = os.path.join(docs_path, "module*", "chapter*.md")
    files = glob.glob(pattern)
    logger.info(f"Found {len(files)} markdown files in local docs")
    return files

def extract_title_from_content(content: str) -> str:
    """Extract title from markdown content (first H1 heading)"""
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip('# ').strip()
    return "Untitled"

def extract_content_from_markdown(file_path: str) -> Dict[str, str]:
    """Extract content and metadata from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title from the content
    title = extract_title_from_content(content)

    # Remove frontmatter (metadata between ---)
    content_without_frontmatter = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # Extract just the main content (without H1 title line)
    lines = content_without_frontmatter.split('\n')
    main_content_lines = []
    for line in lines:
        if not line.strip().startswith('# '):  # Skip H1 title line
            main_content_lines.append(line)

    main_content = '\n'.join(main_content_lines).strip()

    # Generate URL based on file path
    # Extract just the module/chapter part from the path
    docs_dir = os.path.join(os.getcwd(), "book", "my-book", "docs")
    rel_path = os.path.relpath(file_path, docs_dir)
    url_path = rel_path.replace('\\', '/').replace('.md', '')
    url = f"https://rag-book-ten.vercel.app/docs/{url_path}"

    return {
        'url': url,
        'title': title,
        'content': main_content,
        'file_path': file_path
    }

def main():
    """Main function to ingest local documentation markdown files"""
    logger.info("Starting local documentation ingestion for all 4 modules...")

    try:
        # Initialize services
        cleaner = ContentCleanerService()
        chunker = ContentChunkerService(max_chunk_size=1000, overlap=100)
        embedding_service = EmbeddingGeneratorService()
        storage_service = VectorStorageService()

        # Define the docs path - go up one level from backend to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs_path = os.path.join(project_root, "book", "my-book", "docs")
        logger.info(f"Looking for docs in: {docs_path}")

        # Get local markdown files
        markdown_files = get_local_markdown_files(docs_path)

        if not markdown_files:
            logger.warning("No markdown files found in local docs directory")
            return

        # Process each markdown file
        all_book_content = []
        failed_files = []
        total_chunks_created = 0
        total_vectors_stored = 0

        for i, file_path in enumerate(markdown_files):
            logger.info(f"Processing file {i+1}/{len(markdown_files)}: {file_path}")

            try:
                # Extract content from markdown file
                extracted_content = extract_content_from_markdown(file_path)

                # Clean the content
                cleaned_content, is_valid = cleaner.clean_and_validate(extracted_content['content'])

                if not is_valid or not cleaned_content.strip():
                    logger.warning(f"Content from {file_path} is empty or invalid for processing (length: {len(cleaned_content)})")
                    failed_files.append((file_path, "Empty or invalid content"))
                    continue

                # Log verification details
                logger.info(f"  - Original content length: {len(extracted_content['content'])} characters")
                logger.info(f"  - Cleaned content length: {len(cleaned_content)} characters")

                # Create BookContent object with metadata
                book_content = BookContent(
                    url=extracted_content['url'],
                    title=extracted_content['title'],
                    content=cleaned_content,
                    section=extracted_content['title'],  # Using title as section
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                # Chunk the content preserving metadata
                chunks = chunker.chunk_book_content(book_content)

                logger.info(f"  - Number of chunks created: {len(chunks)}")

                # Store each chunk in Qdrant
                stored_count = 0
                for chunk in chunks:
                    try:
                        # Check if chunk is a tuple (it might be returned as (content, metadata))
                        if isinstance(chunk, tuple):
                            chunk_content = chunk[0] if len(chunk) > 0 else ""
                            # Create a proper object with content attribute
                            chunk_obj = type('ChunkObj', (), {'content': chunk_content, 'url': book_content.url, 'title': book_content.title, 'section': book_content.section})()
                        else:
                            chunk_obj = chunk

                        # Generate embedding for the chunk - need to provide chunk_id
                        import uuid
                        chunk_id = str(uuid.uuid4())

                        embedding_vector = embedding_service.generate_embedding(chunk_obj.content, chunk_id)

                        # Create VectorRecord with all required information
                        from models import VectorRecord
                        from datetime import datetime as dt
                        record = VectorRecord(
                            id=chunk_id,
                            payload={
                                'content': chunk_obj.content,
                                'url': chunk_obj.url,
                                'title': chunk_obj.title,
                                'section': chunk_obj.section,
                                'source_file': file_path
                            },
                            vector=embedding_vector,
                            created_at=dt.now()
                        )

                        # Store in Qdrant using the VectorRecord
                        storage_service.store_embedding(record)
                        stored_count += 1
                    except Exception as e:
                        logger.error(f"  - Error storing chunk: {e}")
                        continue

                logger.info(f"  - Qdrant insert status: {stored_count}/{len(chunks)} chunks stored")
                logger.info(f"  ✓ Successfully processed: {extracted_content['url']}")

                total_chunks_created += len(chunks)
                total_vectors_stored += stored_count

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                failed_files.append((file_path, str(e)))
                continue

        # Summary
        logger.info(f"\n=== INGESTION SUMMARY ===")
        logger.info(f"Total files processed: {len(markdown_files) - len(failed_files)}/{len(markdown_files)}")
        logger.info(f"Total chunks created: {total_chunks_created}")
        logger.info(f"Total vectors stored: {total_vectors_stored}")
        if failed_files:
            logger.info(f"Failed files: {len(failed_files)}")
            for file_path, error in failed_files:
                logger.info(f"  - {file_path}: {error}")
        logger.info(f"========================")

    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()