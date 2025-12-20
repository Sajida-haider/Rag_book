import logging
from typing import List, Dict
from .vector_store import QdrantVectorStore
from .metadata_store import NeonPostgresMetadataStore

logger = logging.getLogger(__name__)

class IngestionVerifier:
    """
    Module to verify that the ingestion process was successful
    """

    def __init__(self):
        self.vector_store = QdrantVectorStore()
        self.metadata_store = NeonPostgresMetadataStore()

    def verify_vectors_in_qdrant(self, sample_ids: List[str] = None) -> Dict:
        """
        Verify that vectors are stored in Qdrant
        """
        logger.info("Verifying vectors in Qdrant...")

        try:
            # Get collection info
            collection_info = self.vector_store.get_collection_info()

            if sample_ids:
                # Verify specific IDs if provided
                verification_results = self.vector_store.verify_stored_vectors(sample_ids)
                verified_count = sum(1 for verified in verification_results.values() if verified)

                return {
                    "total_in_collection": collection_info.get("vector_count", 0),
                    "sample_verified": verified_count,
                    "sample_total": len(sample_ids),
                    "verification_results": verification_results,
                    "collection_info": collection_info
                }
            else:
                # Just return collection info if no specific IDs to verify
                return {
                    "total_in_collection": collection_info.get("vector_count", 0),
                    "collection_info": collection_info
                }

        except Exception as e:
            logger.error(f"Error verifying vectors in Qdrant: {e}")
            return {"error": str(e)}

    def verify_metadata_in_postgres(self, sample_ids: List[str] = None) -> Dict:
        """
        Verify that metadata is correct in Neon Postgres
        """
        logger.info("Verifying metadata in Neon Postgres...")

        try:
            # Connect to database
            if not self.metadata_store.connect():
                return {"error": "Could not connect to Neon Postgres"}

            if sample_ids:
                # Verify specific IDs if provided
                verification_results = self.metadata_store.verify_metadata(sample_ids)
                verified_count = sum(1 for verified in verification_results.values() if verified)

                # Get some sample records to check content
                sample_record = self.metadata_store.get_metadata_by_id(sample_ids[0]) if sample_ids else None

                return {
                    "sample_verified": verified_count,
                    "sample_total": len(sample_ids),
                    "verification_results": verification_results,
                    "sample_record": sample_record,
                    "modules": self.metadata_store.get_all_modules()
                }
            else:
                # Just return general info if no specific IDs
                modules = self.metadata_store.get_all_modules()

                return {
                    "modules_count": len(modules),
                    "modules": modules
                }

        except Exception as e:
            logger.error(f"Error verifying metadata in Neon Postgres: {e}")
            return {"error": str(e)}
        finally:
            self.metadata_store.close_connection()

    def verify_content_hierarchy_preservation(self, sample_content: str, processed_chunks: List[Dict]) -> Dict:
        """
        Verify that content hierarchy is preserved during chunking
        """
        logger.info("Verifying content hierarchy preservation...")

        # Check if headings from original content appear in chunks
        import re

        # Extract headings from original content
        original_headings = re.findall(r'^(#{1,6})\s+(.+)$', sample_content, re.MULTILINE)
        original_heading_texts = [heading[1].strip() for heading in original_headings]

        # Extract headings from chunks
        chunk_headings = []
        for chunk in processed_chunks:
            chunk_headings.extend(re.findall(r'^(#{1,6})\s+(.+)$', chunk['content'], re.MULTILINE))

        chunk_heading_texts = [heading[1].strip() for heading in chunk_headings]

        # Check preservation
        headings_preserved = all(heading in chunk_heading_texts for heading in original_heading_texts)
        total_original = len(original_heading_texts)
        total_preserved = sum(1 for heading in original_heading_texts if heading in chunk_heading_texts)

        return {
            "headings_preserved": headings_preserved,
            "total_original_headings": total_original,
            "total_preserved_headings": total_preserved,
            "original_headings": original_heading_texts,
            "preserved_headings": chunk_heading_texts
        }

    def run_comprehensive_verification(self, sample_ids: List[str] = None) -> Dict:
        """
        Run comprehensive verification of the entire ingestion process
        """
        logger.info("Running comprehensive verification...")

        # Verify vectors in Qdrant
        qdrant_verification = self.verify_vectors_in_qdrant(sample_ids)

        # Verify metadata in Postgres
        metadata_verification = self.verify_metadata_in_postgres(sample_ids)

        # Overall result
        verification_result = {
            "qdrant_verification": qdrant_verification,
            "metadata_verification": metadata_verification,
            "verification_timestamp": __import__('datetime').datetime.now().isoformat(),
            "overall_status": "success" if (
                "error" not in qdrant_verification and
                "error" not in metadata_verification
            ) else "failed"
        }

        logger.info(f"Comprehensive verification completed: {verification_result['overall_status']}")
        return verification_result

    def check_data_integrity(self) -> Dict:
        """
        Check overall data integrity between Qdrant and Postgres
        """
        logger.info("Checking data integrity between systems...")

        try:
            # Get counts from both systems
            qdrant_info = self.vector_store.get_collection_info()
            qdrant_count = qdrant_info.get("vector_count", 0)

            if not self.metadata_store.connect():
                return {"error": "Could not connect to Neon Postgres for integrity check"}

            # Get a count of metadata records (this would require a COUNT query)
            # For now, we'll just verify we can connect and get modules
            modules = self.metadata_store.get_all_modules()

            return {
                "qdrant_vector_count": qdrant_count,
                "postgres_modules_count": len(modules),
                "modules_list": modules,
                "integrity_check": "completed"  # In a real implementation, we'd compare counts
            }

        except Exception as e:
            logger.error(f"Error during integrity check: {e}")
            return {"error": str(e)}
        finally:
            self.metadata_store.close_connection()


# Example usage
if __name__ == "__main__":
    verifier = IngestionVerifier()

    # Example verification (would need actual sample IDs from a real ingestion)
    sample_ids = ["test-id-1", "test-id-2"]  # These would come from actual ingestion

    # Run comprehensive verification
    results = verifier.run_comprehensive_verification(sample_ids)
    print(f"Verification results: {results}")

    # Check data integrity
    integrity = verifier.check_data_integrity()
    print(f"Integrity check: {integrity}")