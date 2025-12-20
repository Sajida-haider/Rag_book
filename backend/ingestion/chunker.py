import re
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class ContentChunker:
    """
    Module to chunk content into logical sections optimized for embeddings
    """

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_by_headings(self, content: str, headings_hierarchy: List[Tuple[int, str]] = None) -> List[Dict]:
        """
        Chunk content based on headings hierarchy to maintain context
        """
        if headings_hierarchy is None:
            headings_hierarchy = []

        # Split content by headings to maintain document structure
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())

            if heading_match:
                # If we have accumulated content and adding this heading would exceed size,
                # save the current chunk first
                if current_chunk and current_size + len(line) > self.max_chunk_size:
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append({
                            'content': chunk_text,
                            'size': len(chunk_text),
                            'start_line': i - len(current_chunk),
                            'end_line': i - 1
                        })

                    # Start a new chunk with the heading
                    current_chunk = [line]
                    current_size = len(line)
                else:
                    current_chunk.append(line)
                    current_size += len(line)
            else:
                # Regular content line
                if current_size + len(line) > self.max_chunk_size and current_chunk:
                    # Current chunk would be too large, so save it
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append({
                            'content': chunk_text,
                            'size': len(chunk_text),
                            'start_line': i - len(current_chunk),
                            'end_line': i - 1
                        })

                    # Add overlap from the end of the previous chunk if available
                    if chunks and self.overlap > 0:
                        prev_chunk = chunks[-1]['content']
                        overlap_lines = prev_chunk.split('\n')[-3:]  # Take last few lines as overlap
                        current_chunk = overlap_lines + [line]
                        current_size = sum(len(l) for l in current_chunk)
                    else:
                        current_chunk = [line]
                        current_size = len(line)
                else:
                    current_chunk.append(line)
                    current_size += len(line)

            i += 1

        # Add the last chunk if it has content
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append({
                    'content': chunk_text,
                    'size': len(chunk_text),
                    'start_line': len(lines) - len(current_chunk),
                    'end_line': len(lines) - 1
                })

        logger.info(f"Chunked content into {len(chunks)} chunks")
        return chunks

    def chunk_by_paragraph(self, content: str) -> List[Dict]:
        """
        Alternative method: chunk content by paragraphs
        """
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        current_size = 0

        for paragraph in paragraphs:
            if len(paragraph.strip()) == 0:
                continue

            if current_size + len(paragraph) > self.max_chunk_size and current_chunk:
                # Current chunk would be too large, so save it
                chunks.append({
                    'content': current_chunk.strip(),
                    'size': len(current_chunk),
                    'paragraph_count': len(current_chunk.split('\n\n'))
                })

                # Add overlap if needed
                if self.overlap > 0:
                    # Take last part of the saved chunk as overlap
                    overlap_start = max(0, len(current_chunk) - self.overlap)
                    overlap_text = current_chunk[overlap_start:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_size = len(current_chunk)
                else:
                    current_chunk = paragraph
                    current_size = len(paragraph)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                    current_size += len(paragraph) + 2
                else:
                    current_chunk = paragraph
                    current_size = len(paragraph)

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'size': len(current_chunk),
                'paragraph_count': len(current_chunk.split('\n\n'))
            })

        logger.info(f"Chunked content into {len(chunks)} chunks by paragraphs")
        return chunks

    def chunk_content(self, content: str, headings_hierarchy: List[Tuple[int, str]] = None) -> List[Dict]:
        """
        Main method to chunk content using the best available method
        """
        if headings_hierarchy and len(headings_hierarchy) > 0:
            # Use heading-based chunking if headings are available
            return self.chunk_by_headings(content, headings_hierarchy)
        else:
            # Fall back to paragraph-based chunking
            return self.chunk_by_paragraph(content)

    def optimize_chunk_size(self, chunks: List[Dict], target_size: int = 800) -> List[Dict]:
        """
        Optimize chunks to be closer to the target size
        """
        optimized_chunks = []
        i = 0

        while i < len(chunks):
            current = chunks[i]

            # If this chunk is already close to target size, keep it
            if current['size'] >= target_size * 0.8 or i == len(chunks) - 1:
                optimized_chunks.append(current)
                i += 1
            else:
                # Try to merge with next chunk if it doesn't exceed max size
                if i + 1 < len(chunks):
                    next_chunk = chunks[i + 1]
                    combined_size = current['size'] + next_chunk['size']

                    if combined_size <= self.max_chunk_size:
                        # Merge chunks
                        merged_content = current['content'] + "\n\n" + next_chunk['content']
                        optimized_chunks.append({
                            'content': merged_content,
                            'size': len(merged_content),
                            'merged_from': [current.get('id', i), next_chunk.get('id', i+1)]
                        })
                        i += 2  # Skip next chunk since we merged it
                    else:
                        optimized_chunks.append(current)
                        i += 1
                else:
                    optimized_chunks.append(current)
                    i += 1

        logger.info(f"Optimized from {len(chunks)} to {len(optimized_chunks)} chunks")
        return optimized_chunks

# Example usage
if __name__ == "__main__":
    chunker = ContentChunker(max_chunk_size=200, overlap=50)

    sample_content = """
# Introduction

This is the introduction to the book. It contains important information that readers need to understand before proceeding.

## Chapter 1

Chapter 1 covers the basics of the topic. This section is essential for understanding the fundamentals.

### Section 1.1

This is a detailed subsection that goes deeper into specific concepts. Understanding this section requires knowledge from the previous sections.

### Section 1.2

This section builds on the previous one and introduces additional concepts that are important for the overall understanding.

## Chapter 2

Chapter 2 covers more advanced topics. This chapter assumes that readers have a good understanding of the concepts from Chapter 1.

### Section 2.1

Advanced concepts that build on the foundation established in Chapter 1. This section contains complex ideas that require careful study.

### Section 2.2

The final section of Chapter 2, which ties together all the concepts from this chapter and prepares readers for the next chapter.
"""

    headings = [
        (1, "Introduction"),
        (2, "Chapter 1"),
        (3, "Section 1.1"),
        (3, "Section 1.2"),
        (2, "Chapter 2"),
        (3, "Section 2.1"),
        (3, "Section 2.2")
    ]

    chunks = chunker.chunk_content(sample_content, headings)

    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} (size: {chunk['size']}):")
        print(f"Lines {chunk.get('start_line', 'N/A')}-{chunk.get('end_line', 'N/A')}")
        print(chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content'])