"""
Module for verifying that each chunk's source URL and metadata match correctly.
This module implements functionality to validate source URLs and metadata correspondence.
"""

import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataValidator:
    """
    A class to handle metadata validation for Qdrant chunks.
    """

    def __init__(self):
        """
        Initialize the MetadataValidator.
        """
        # Set up retry strategy for HTTP requests
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set a reasonable timeout
        self.timeout = 10

    def validate_url_accessibility(self, url: str) -> Dict[str, Any]:
        """
        Validate that a source URL is accessible and returns expected content.

        Args:
            url (str): The URL to validate

        Returns:
            Dict[str, Any]: Validation results including status, response time, etc.
        """
        result = {
            "url": url,
            "accessible": False,
            "status_code": None,
            "response_time": None,
            "content_type": None,
            "error": None
        }

        try:
            start_time = time.time()
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            response_time = time.time() - start_time

            result.update({
                "accessible": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": response_time,
                "content_type": response.headers.get('content-type', 'unknown')
            })

            if response.status_code >= 400:
                result["error"] = f"HTTP {response.status_code}"
            else:
                logger.info(f"URL {url} is accessible (status: {response.status_code})")

        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
            logger.warning(f"URL {url} is not accessible: {e}")

        return result

    def validate_url_format(self, url: str) -> bool:
        """
        Validate that a URL has proper format.

        Args:
            url (str): The URL to validate

        Returns:
            bool: True if URL format is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def cross_reference_metadata(self, chunk_metadata: Dict[str, Any], source_document: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Cross-reference metadata with source document information.

        Args:
            chunk_metadata (Dict[str, Any]): Metadata from the chunk
            source_document (Optional[Dict[str, Any]]): Expected source document metadata

        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {
            "metadata_fields_validated": [],
            "mismatches": [],
            "missing_fields": [],
            "extra_fields": []
        }

        if source_document:
            # Compare each field in the chunk metadata with the source document
            chunk_keys = set(chunk_metadata.keys())
            source_keys = set(source_document.keys())

            # Check for extra fields in chunk that aren't in source
            extra_fields = chunk_keys - source_keys
            validation_results["extra_fields"] = list(extra_fields)

            # Check for missing fields in chunk that are in source
            missing_fields = source_keys - chunk_keys
            validation_results["missing_fields"] = list(missing_fields)

            # Validate common fields
            common_keys = chunk_keys & source_keys
            for key in common_keys:
                chunk_value = chunk_metadata.get(key)
                source_value = source_document.get(key)

                if chunk_value != source_value:
                    validation_results["mismatches"].append({
                        "field": key,
                        "chunk_value": chunk_value,
                        "source_value": source_value
                    })
                else:
                    validation_results["metadata_fields_validated"].append(key)
        else:
            # If no source document provided, just validate the structure
            required_fields = ["source", "title", "author", "created_at"]
            present_fields = [field for field in required_fields if field in chunk_metadata]
            missing_fields = [field for field in required_fields if field not in chunk_metadata]

            validation_results["metadata_fields_validated"] = present_fields
            validation_results["missing_fields"] = missing_fields

        return validation_results

    def verify_metadata_correspondence(self, chunks: List[Dict[str, Any]], source_documents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Verify that metadata corresponds correctly to source documents.

        Args:
            chunks (List[Dict[str, Any]]): List of chunks with metadata
            source_documents (Optional[List[Dict[str, Any]]]): List of source documents for comparison

        Returns:
            Dict[str, Any]: Overall validation results
        """
        results = {
            "total_chunks": len(chunks),
            "url_validations": [],
            "metadata_validations": [],
            "overall_accuracy": 0.0,
            "summary": {}
        }

        url_valid_count = 0
        metadata_valid_count = 0

        for i, chunk in enumerate(chunks):
            chunk_metadata = chunk.get("payload", {})
            chunk_id = chunk.get("id", f"chunk_{i}")

            # Validate URL accessibility if present
            source_url = chunk_metadata.get("source", chunk_metadata.get("url", ""))
            if source_url:
                url_result = self.validate_url_accessibility(source_url)
                results["url_validations"].append({
                    "chunk_id": chunk_id,
                    "url": source_url,
                    **url_result
                })
                if url_result["accessible"]:
                    url_valid_count += 1

            # Validate metadata correspondence
            source_doc = source_documents[i] if source_documents and i < len(source_documents) else None
            metadata_result = self.cross_reference_metadata(chunk_metadata, source_doc)
            results["metadata_validations"].append({
                "chunk_id": chunk_id,
                "validation": metadata_result
            })

            # Count valid metadata if no mismatches
            if not metadata_result["mismatches"]:
                metadata_valid_count += 1

        # Calculate accuracy rates
        url_accuracy = url_valid_count / len([c for c in chunks if c.get("payload", {}).get("source") or c.get("payload", {}).get("url")]) if chunks else 0
        metadata_accuracy = metadata_valid_count / len(chunks) if chunks else 0

        results["summary"] = {
            "url_valid_count": url_valid_count,
            "metadata_valid_count": metadata_valid_count,
            "url_accuracy_rate": url_accuracy,
            "metadata_accuracy_rate": metadata_accuracy
        }

        logger.info(f"Metadata validation complete: {metadata_valid_count}/{len(chunks)} chunks have valid metadata")
        logger.info(f"URL accuracy rate: {url_accuracy:.2%}, Metadata accuracy rate: {metadata_accuracy:.2%}")

        return results

    def create_metadata_consistency_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Create a report of metadata consistency validation.

        Args:
            validation_results (Dict[str, Any]): Results from verify_metadata_correspondence

        Returns:
            str: Formatted consistency report
        """
        report_lines = ["Metadata Consistency Validation Report", "=" * 40, ""]

        summary = validation_results.get("summary", {})
        url_valid_count = summary.get("url_valid_count", 0)
        metadata_valid_count = summary.get("metadata_valid_count", 0)
        url_accuracy = summary.get("url_accuracy_rate", 0)
        metadata_accuracy = summary.get("metadata_accuracy_rate", 0)

        report_lines.append(f"Total chunks processed: {validation_results['total_chunks']}")
        report_lines.append(f"URLs validated: {url_valid_count}/{validation_results['total_chunks'] - validation_results['total_chunks'] + len([v for v in validation_results['url_validations'] if v['url']])} accessible")
        report_lines.append(f"Metadata accuracy: {metadata_valid_count}/{validation_results['total_chunks']} valid")
        report_lines.append(f"URL accuracy rate: {url_accuracy:.2%}")
        report_lines.append(f"Metadata accuracy rate: {metadata_accuracy:.2%}")
        report_lines.append("")

        # URL validation details
        url_validations = validation_results.get("url_validations", [])
        if url_validations:
            report_lines.append("URL Validation Details:")
            for validation in url_validations:
                status = "✓" if validation["accessible"] else "✗"
                report_lines.append(f"  {status} {validation['url']} - Status: {validation['status_code']}, Time: {validation['response_time']:.2f}s")
            report_lines.append("")

        # Metadata validation details
        metadata_validations = validation_results.get("metadata_validations", [])
        if metadata_validations:
            report_lines.append("Metadata Validation Details:")
            for validation in metadata_validations:
                chunk_id = validation["chunk_id"]
                val_result = validation["validation"]

                if val_result["mismatches"]:
                    report_lines.append(f"  Chunk {chunk_id}: {len(val_result['mismatches'])} mismatches found")
                    for mismatch in val_result["mismatches"]:
                        report_lines.append(f"    - {mismatch['field']}: '{mismatch['chunk_value']}' != '{mismatch['source_value']}'")
                else:
                    report_lines.append(f"  Chunk {chunk_id}: ✓ All metadata matches")
            report_lines.append("")

        # Summary
        report_lines.append("Validation Summary:")
        report_lines.append(f"  Overall metadata correspondence accuracy: {metadata_accuracy:.2%}")
        report_lines.append(f"  Target accuracy: 99%+")
        report_lines.append(f"  Status: {'PASS' if metadata_accuracy >= 0.99 else 'FAIL'}")

        return "\n".join(report_lines)

    def validate_metadata_field_types(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that metadata fields have appropriate data types.

        Args:
            metadata (Dict[str, Any]): Metadata to validate

        Returns:
            Dict[str, Any]: Validation results for field types
        """
        type_validation = {
            "valid_fields": [],
            "invalid_fields": [],
            "type_errors": []
        }

        # Define expected types for common fields
        expected_types = {
            "source": str,
            "url": str,
            "title": str,
            "author": str,
            "created_at": (str, int, float),
            "updated_at": (str, int, float),
            "page_number": int,
            "chunk_index": int,
            "document_id": str,
            "content_type": str
        }

        for field, value in metadata.items():
            if field in expected_types:
                expected_type = expected_types[field]
                if isinstance(value, expected_type):
                    type_validation["valid_fields"].append(field)
                else:
                    type_validation["invalid_fields"].append(field)
                    type_validation["type_errors"].append({
                        "field": field,
                        "expected_type": expected_type,
                        "actual_type": type(value),
                        "actual_value": value
                    })
            else:
                # For fields not in expected_types, just record them as valid
                type_validation["valid_fields"].append(field)

        return type_validation

    def verify_source_url_consistency(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify consistency of source URLs across chunks.

        Args:
            chunks (List[Dict[str, Any]]): List of chunks with metadata

        Returns:
            Dict[str, Any]: Consistency validation results
        """
        results = {
            "total_chunks": len(chunks),
            "unique_sources": set(),
            "source_distribution": {},
            "inconsistent_chunks": [],
            "consistency_rate": 0.0
        }

        for chunk in chunks:
            chunk_metadata = chunk.get("payload", {})
            source_url = chunk_metadata.get("source", chunk_metadata.get("url", ""))

            if source_url:
                results["unique_sources"].add(source_url)

                # Update distribution count
                if source_url in results["source_distribution"]:
                    results["source_distribution"][source_url] += 1
                else:
                    results["source_distribution"][source_url] = 1
            else:
                results["inconsistent_chunks"].append(chunk.get("id", "unknown"))

        # Calculate consistency rate
        unique_sources_count = len(results["unique_sources"])
        if unique_sources_count > 0:
            # For this validation, we consider it consistent if most chunks have valid source URLs
            chunks_with_sources = len(chunks) - len(results["inconsistent_chunks"])
            results["consistency_rate"] = chunks_with_sources / len(chunks) if len(chunks) > 0 else 0

        return results


def main():
    """
    Main function to demonstrate metadata validation functionality.
    """
    # Initialize the validator
    validator = MetadataValidator()

    # Example usage - in a real scenario, you'd have actual chunks from Qdrant
    sample_chunks = [
        {
            "id": "chunk_1",
            "payload": {
                "source": "https://example.com/book/chapter1",
                "title": "Chapter 1: Introduction",
                "author": "Author Name",
                "created_at": "2023-01-01",
                "page_number": 1,
                "content_type": "text"
            }
        },
        {
            "id": "chunk_2",
            "payload": {
                "source": "https://example.com/book/chapter2",
                "title": "Chapter 2: Background",
                "author": "Author Name",
                "created_at": "2023-01-01",
                "page_number": 2,
                "content_type": "text"
            }
        }
    ]

    # Validate the sample chunks
    validation_results = validator.verify_metadata_correspondence(sample_chunks)

    # Generate consistency report
    report = validator.create_metadata_consistency_report(validation_results)
    print(report)

    # Validate URL format
    for chunk in sample_chunks:
        source_url = chunk["payload"].get("source", "")
        is_valid = validator.validate_url_format(source_url)
        print(f"URL {source_url} format valid: {is_valid}")

    return validation_results


if __name__ == "__main__":
    main()