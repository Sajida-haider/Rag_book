"""
Module for verifying that each retrieved chunk matches the original book text accurately.
This module implements functionality to compare chunked content with original book text.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher
import re
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentVerifier:
    """
    A class to handle content verification between retrieved chunks and original text.
    """

    def __init__(self):
        """
        Initialize the ContentVerifier.
        """
        self.mismatch_threshold = 0.9  # 90% similarity threshold

    def load_original_text(self, file_path: str) -> str:
        """
        Load the original book text from a file.

        Args:
            file_path (str): Path to the original text file

        Returns:
            str: The original text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            logger.info(f"Loaded original text from {file_path} ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Error loading original text from {file_path}: {e}")
            return ""

    def create_text_mapping(self, original_text: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Create a mapping of the original text into chunks with position information.

        Args:
            original_text (str): The original book text
            chunk_size (int): Size of each chunk

        Returns:
            List[Dict[str, Any]]: List of chunks with position information
        """
        chunks = []
        start_pos = 0

        while start_pos < len(original_text):
            end_pos = min(start_pos + chunk_size, len(original_text))
            chunk_text = original_text[start_pos:end_pos]

            chunk_info = {
                "text": chunk_text,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "chunk_id": f"chunk_{len(chunks) + 1}",
                "length": len(chunk_text)
            }

            chunks.append(chunk_info)
            start_pos = end_pos

        logger.info(f"Created {len(chunks)} chunks from original text")
        return chunks

    def find_original_position(self, original_text: str, chunk_text: str) -> Tuple[int, int, float]:
        """
        Find the position of a chunk in the original text using sequence matching.

        Args:
            original_text (str): The original book text
            chunk_text (str): The chunk to find

        Returns:
            Tuple[int, int, float]: Start position, end position, and similarity ratio
        """
        if not chunk_text or not original_text:
            return -1, -1, 0.0

        # Use SequenceMatcher to find the best match
        matcher = SequenceMatcher(None, original_text.lower(), chunk_text.lower())

        # Get the best matching block
        match = matcher.find_longest_match(0, len(original_text), 0, len(chunk_text))

        if match.size == 0:
            return -1, -1, 0.0

        # Calculate similarity ratio
        similarity = matcher.ratio()

        # Get the matched portion from original text
        start_pos = match.a
        end_pos = match.a + match.size

        return start_pos, end_pos, similarity

    def compare_chunk_with_original(self, original_text: str, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare a retrieved chunk with the original text.

        Args:
            original_text (str): The original book text
            chunk_data (Dict[str, Any]): Chunk data with text and metadata

        Returns:
            Dict[str, Any]: Comparison results
        """
        retrieved_text = chunk_data.get("text", chunk_data.get("payload", {}).get("text", ""))

        if not retrieved_text:
            return {
                "status": "error",
                "message": "No text found in chunk data",
                "similarity": 0.0,
                "original_position": (-1, -1)
            }

        # Find the position in original text
        start_pos, end_pos, similarity = self.find_original_position(original_text, retrieved_text)

        # Create comparison result
        result = {
            "chunk_id": chunk_data.get("id", chunk_data.get("chunk_id", "unknown")),
            "status": "match" if similarity >= self.mismatch_threshold else "mismatch",
            "similarity": similarity,
            "original_position": (start_pos, end_pos),
            "retrieved_length": len(retrieved_text),
            "original_length": end_pos - start_pos if start_pos != -1 else 0,
            "discrepancies": []
        }

        # If there's a mismatch, identify specific discrepancies
        if similarity < self.mismatch_threshold and start_pos != -1:
            original_chunk = original_text[start_pos:end_pos]
            discrepancies = self.identify_discrepancies(original_chunk, retrieved_text)
            result["discrepancies"] = discrepancies

        return result

    def identify_discrepancies(self, original: str, retrieved: str) -> List[Dict[str, Any]]:
        """
        Identify specific discrepancies between original and retrieved text.

        Args:
            original (str): Original text
            retrieved (str): Retrieved text

        Returns:
            List[Dict[str, Any]]: List of discrepancies with details
        """
        discrepancies = []

        # Use SequenceMatcher to identify differences
        matcher = SequenceMatcher(None, original, retrieved)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                discrepancy = {
                    "type": tag,  # 'replace', 'delete', 'insert'
                    "original_text": original[i1:i2],
                    "retrieved_text": retrieved[j1:j2],
                    "original_pos": (i1, i2),
                    "retrieved_pos": (j1, j2)
                }
                discrepancies.append(discrepancy)

        return discrepancies

    def verify_all_chunks(self, original_text: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify all retrieved chunks against the original text.

        Args:
            original_text (str): The original book text
            retrieved_chunks (List[Dict[str, Any]]): List of retrieved chunks with metadata

        Returns:
            Dict[str, Any]: Verification summary and detailed results
        """
        results = []
        matches = 0
        mismatches = 0
        total_similarity = 0.0

        logger.info(f"Verifying {len(retrieved_chunks)} chunks against original text")

        for chunk_data in retrieved_chunks:
            result = self.compare_chunk_with_original(original_text, chunk_data)
            results.append(result)

            if result["status"] == "match":
                matches += 1
            else:
                mismatches += 1

            total_similarity += result["similarity"]

        # Calculate overall metrics
        total_chunks = len(retrieved_chunks)
        accuracy_rate = matches / total_chunks if total_chunks > 0 else 0
        avg_similarity = total_similarity / total_chunks if total_chunks > 0 else 0

        summary = {
            "total_chunks": total_chunks,
            "matches": matches,
            "mismatches": mismatches,
            "accuracy_rate": accuracy_rate,
            "average_similarity": avg_similarity,
            "results": results
        }

        logger.info(f"Verification complete: {matches} matches, {mismatches} mismatches")
        logger.info(f"Accuracy rate: {accuracy_rate:.2%}, Average similarity: {avg_similarity:.2%}")

        return summary

    def generate_discrepancy_report(self, verification_results: Dict[str, Any]) -> str:
        """
        Generate a detailed report of discrepancies found during verification.

        Args:
            verification_results (Dict[str, Any]): Results from verify_all_chunks

        Returns:
            str: Formatted discrepancy report
        """
        report_lines = ["Content Verification Discrepancy Report", "=" * 40, ""]

        results = verification_results.get("results", [])
        mismatches = [r for r in results if r["status"] == "mismatch"]

        if not mismatches:
            report_lines.append("No discrepancies found. All chunks match the original text.")
        else:
            report_lines.append(f"Found {len(mismatches)} chunks with discrepancies:")
            report_lines.append("")

            for i, result in enumerate(mismatches):
                report_lines.append(f"{i+1}. Chunk ID: {result['chunk_id']}")
                report_lines.append(f"   Similarity: {result['similarity']:.3f}")
                report_lines.append(f"   Original Position: {result['original_position']}")

                discrepancies = result.get("discrepancies", [])
                if discrepancies:
                    report_lines.append("   Discrepancies:")
                    for disc in discrepancies[:3]:  # Show first 3 discrepancies
                        report_lines.append(f"     - {disc['type']}: '{disc['original_text'][:50]}...' -> '{disc['retrieved_text'][:50]}...'")
                    if len(discrepancies) > 3:
                        report_lines.append(f"     ... and {len(discrepancies) - 3} more discrepancies")

                report_lines.append("")

        # Add summary
        report_lines.append("Summary:")
        report_lines.append(f"  Total chunks verified: {verification_results['total_chunks']}")
        report_lines.append(f"  Matches: {verification_results['matches']}")
        report_lines.append(f"  Mismatches: {verification_results['mismatches']}")
        report_lines.append(f"  Accuracy rate: {verification_results['accuracy_rate']:.2%}")
        report_lines.append(f"  Average similarity: {verification_results['average_similarity']:.2%}")

        return "\n".join(report_lines)

    def validate_text_position_accuracy(self, original_text: str, chunk_data: Dict[str, Any]) -> bool:
        """
        Validate that the position mapping between chunks and original text is accurate.

        Args:
            original_text (str): The original book text
            chunk_data (Dict[str, Any]): Chunk data with position information

        Returns:
            bool: True if position mapping is accurate, False otherwise
        """
        # Get the text from the chunk
        chunk_text = chunk_data.get("text", chunk_data.get("payload", {}).get("text", ""))
        expected_start = chunk_data.get("start_pos")
        expected_end = chunk_data.get("end_pos")

        if expected_start is None or expected_end is None:
            # If no position info provided, find the position
            start_pos, end_pos, similarity = self.find_original_position(original_text, chunk_text)
            return similarity >= self.mismatch_threshold

        # Check if the text at the expected position matches the chunk
        if expected_start < len(original_text) and expected_end <= len(original_text):
            original_at_position = original_text[expected_start:expected_end]
            similarity = SequenceMatcher(None, original_at_position.lower(), chunk_text.lower()).ratio()
            return similarity >= self.mismatch_threshold

        return False


def main():
    """
    Main function to demonstrate content verification functionality.
    """
    import json

    # Initialize the verifier
    verifier = ContentVerifier()

    # Example usage - in a real scenario, you'd load actual original text and retrieved chunks
    original_text = "This is a sample book text. It contains multiple sentences and paragraphs. " \
                   "The content verification system needs to match these chunks accurately. " \
                   "Each chunk should correspond to a specific position in the original text. " \
                   "This ensures that the retrieved content is accurate and complete."

    # Simulate retrieved chunks (in practice, these would come from Qdrant)
    retrieved_chunks = [
        {
            "id": "chunk_1",
            "payload": {
                "text": "This is a sample book text. It contains multiple sentences and paragraphs."
            }
        },
        {
            "id": "chunk_2",
            "payload": {
                "text": "The content verification system needs to match these chunks accurately."
            }
        },
        {
            "id": "chunk_3",
            "payload": {
                "text": "Each chunk should correspond to a specific position in the original text."
            }
        },
        {
            "id": "chunk_4",
            "payload": {
                "text": "This ensures that the retrieved content is accurate and complete."
            }
        }
    ]

    # Verify all chunks
    verification_results = verifier.verify_all_chunks(original_text, retrieved_chunks)

    # Generate discrepancy report
    report = verifier.generate_discrepancy_report(verification_results)
    print(report)

    return verification_results


if __name__ == "__main__":
    main()