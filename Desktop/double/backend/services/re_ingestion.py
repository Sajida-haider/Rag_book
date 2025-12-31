"""Service for re-ingesting updated book content"""

import os
from typing import List, Dict
from datetime import datetime
import sys
import os
# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models import BookContent, VectorRecord
from services.change_detector import ChangeDetectorService
from services.vector_storage import VectorStorageService
from services.embedding_generator import EmbeddingGeneratorService
from services.content_chunker import ContentChunkerService


class ReIngestionService:
    def __init__(self):
        self.change_detector = ChangeDetectorService()
        self.storage_service = VectorStorageService()
        self.embedding_service = EmbeddingGeneratorService()
        self.chunker = ContentChunkerService(max_chunk_size=1000, overlap=100)
        self.hashes_file = os.getenv("HASHES_FILE", "content_hashes.json")

    def load_previous_hashes(self) -> Dict[str, str]:
        """Load previously stored content hashes"""
        return self.change_detector.load_hashes_from_file(self.hashes_file)

    def save_current_hashes(self, content_list: List[BookContent]):
        """Save current content hashes for future comparisons"""
        hashes = self.change_detector.store_content_hashes(content_list)
        self.change_detector.save_hashes_to_file(hashes, self.hashes_file)

    def update_content(self, new_content: List[BookContent]) -> Dict[str, int]:
        """Update content by detecting changes and re-ingesting only changed items"""
        # Load previous hashes
        previous_hashes = self.load_previous_hashes()

        # Detect changes
        changes = self.change_detector.detect_changes(new_content, previous_hashes)

        # Process each type of change
        stats = {
            'added': 0,
            'modified': 0,
            'removed': 0,
            'unchanged': 0
        }

        # Handle added and modified content
        all_changed_urls = changes['added'] + changes['modified']
        for content in new_content:
            if content.url in all_changed_urls:
                # Remove old records from storage (if modified)
                if content.url in changes['modified']:
                    self._remove_content_from_storage(content.url)

                # Process and store new/updated content
                success = self._process_and_store_content(content)
                if success:
                    if content.url in changes['added']:
                        stats['added'] += 1
                    else:  # modified
                        stats['modified'] += 1
            else:
                stats['unchanged'] += 1

        # Handle removed content
        for url in changes['removed']:
            self._remove_content_from_storage(url)
            stats['removed'] += 1

        # Save current hashes
        self.save_current_hashes(new_content)

        return stats

    def _process_and_store_content(self, book_content: BookContent) -> bool:
        """Process and store a single content item"""
        try:
            # Chunk the content
            chunks = self.chunker.chunk_book_content(book_content)

            # Process each chunk
            for i, (chunk_text, chunk_metadata) in enumerate(chunks):
                # Generate embedding for the chunk
                embedding = self.embedding_service.generate_embedding(
                    text=chunk_text,
                    chunk_id=f"{book_content.url}_chunk_{i}"
                )

                # Create vector record
                vector_record = VectorRecord(
                    id=f"{book_content.url}_chunk_{i}",
                    payload={
                        'url': book_content.url,
                        'title': book_content.title,
                        'section': book_content.section,
                        'content': chunk_text,
                        'chunk_index': chunk_metadata['chunk_index'],
                        'total_chunks': len(chunks),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    },
                    vector=embedding.vector,
                    created_at=datetime.now()
                )

                # Store in vector database
                success = self.storage_service.store_embedding(vector_record)
                if not success:
                    return False

            return True
        except Exception as e:
            print(f"Error processing content {book_content.url}: {e}")
            return False

    def _remove_content_from_storage(self, url: str) -> bool:
        """Remove content from storage by URL (in a real implementation, this would be more sophisticated)"""
        # Note: Qdrant doesn't have a direct way to delete points by payload value
        # In a real implementation, we would need to search for points with the URL
        # and delete them by ID. For now, we'll just note that deletion would happen here.
        print(f"Would remove content for URL: {url}")
        return True  # Placeholder - implement actual deletion logic as needed

    def full_reingestion(self, all_content: List[BookContent]) -> Dict[str, int]:
        """Perform a full re-ingestion of all content"""
        # For a full reingestion, we'd typically clear the collection and re-add everything
        # But for this implementation, we'll just update as normal
        stats = self.update_content(all_content)
        return stats