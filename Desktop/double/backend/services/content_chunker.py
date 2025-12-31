"""Service for chunking content into appropriate sizes for embedding"""

import re
from typing import List, Tuple
import sys
import os
# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models import BookContent


class ContentChunkerService:
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_content(self, content: str, url: str, title: str) -> List[Tuple[str, dict]]:
        """Chunk content into appropriate sizes with metadata"""
        if not content:
            return []

        # Split content into chunks based on paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            # If adding this paragraph would exceed the chunk size
            if len(current_chunk) + len(paragraph) > self.max_chunk_size:
                # If current chunk is not empty, save it
                if current_chunk.strip():
                    chunks.append((current_chunk.strip(), {
                        'url': url,
                        'title': title,
                        'chunk_index': chunk_index,
                        'section': 'paragraph'
                    }))
                    chunk_index += 1

                # Start new chunk with overlap if possible
                current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append((current_chunk.strip(), {
                'url': url,
                'title': title,
                'chunk_index': chunk_index,
                'section': 'paragraph'
            }))

        # If we still have chunks that are too large, split them by sentences
        final_chunks = []
        for chunk_text, metadata in chunks:
            if len(chunk_text) <= self.max_chunk_size:
                final_chunks.append((chunk_text, metadata))
            else:
                # Split large chunk by sentences
                sentence_chunks = self._split_by_sentences(chunk_text, metadata)
                final_chunks.extend(sentence_chunks)

        return final_chunks

    def _split_by_sentences(self, text: str, metadata: dict) -> List[Tuple[str, dict]]:
        """Split text by sentences if it's too large"""
        # Split text into sentences
        sentences = re.split(r'[.!?]+\s+', text)

        chunks = []
        current_chunk = ""
        chunk_index = metadata['chunk_index']

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                if current_chunk.strip():
                    new_metadata = metadata.copy()
                    new_metadata['chunk_index'] = chunk_index
                    chunks.append((current_chunk.strip(), new_metadata))
                    chunk_index += 1

                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        if current_chunk.strip():
            new_metadata = metadata.copy()
            new_metadata['chunk_index'] = chunk_index
            chunks.append((current_chunk.strip(), new_metadata))

        return chunks

    def chunk_book_content(self, book_content: BookContent) -> List[Tuple[str, dict]]:
        """Chunk a BookContent object into appropriate sizes"""
        return self.chunk_content(
            book_content.content,
            book_content.url,
            book_content.title
        )