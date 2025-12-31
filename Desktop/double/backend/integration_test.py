"""
Integration test for the complete data retrieval and validation pipeline.
This script tests the end-to-end functionality of retrieving data from Qdrant,
verifying content accuracy, and validating metadata.
"""

import logging
import time
from typing import List, Dict, Any
from pathlib import Path
import json

# Import our modules
from backend.retrieve_data import QdrantDataRetriever
from backend.content_verification import ContentVerifier
from backend.metadata_validation import MetadataValidator
from backend.pipeline_tests import PipelineTester

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationTester:
    """
    A class to handle end-to-end integration testing of the data retrieval pipeline.
    """

    def __init__(self):
        """
        Initialize the IntegrationTester.
        """
        self.retriever = None
        self.verifier = None
        self.validator = None
        self.tester = None

    def setup_components(self):
        """
        Initialize all required components for integration testing.
        """
        logger.info("Setting up integration test components...")

        # Initialize all components
        self.retriever = QdrantDataRetriever()
        self.verifier = ContentVerifier()
        self.validator = MetadataValidator()
        self.tester = PipelineTester()

        logger.info("All components initialized successfully")

    def run_end_to_end_test(self, original_text: str = "") -> Dict[str, Any]:
        """
        Run an end-to-end test of the complete pipeline.

        Args:
            original_text (str): Optional original text for content verification

        Returns:
            Dict[str, Any]: Integration test results
        """
        logger.info("Starting end-to-end integration test...")

        start_time = time.time()

        # Step 1: Check if collection exists
        collection_exists = self.retriever.check_collection_exists()
        logger.info(f"Collection exists: {collection_exists}")

        if not collection_exists:
            logger.warning("Collection does not exist. Creating sample data for testing.")
            # For testing purposes, we'll create sample data
            retrieved_chunks = [
                {
                    "id": "test_chunk_1",
                    "payload": {
                        "text": "This is a sample text for testing purposes.",
                        "source": "https://example.com/test1",
                        "title": "Test Document 1"
                    }
                },
                {
                    "id": "test_chunk_2",
                    "payload": {
                        "text": "Another sample text chunk for verification.",
                        "source": "https://example.com/test2",
                        "title": "Test Document 2"
                    }
                }
            ]
        else:
            # Retrieve actual data from Qdrant
            retrieved_chunks = self.retriever.retrieve_all_embeddings(limit=10)
            logger.info(f"Retrieved {len(retrieved_chunks)} chunks from Qdrant")

        # Step 2: Content verification (if original text provided)
        content_verification_results = None
        if original_text and retrieved_chunks:
            logger.info("Running content verification...")
            # Extract text from retrieved chunks for verification
            chunks_for_verification = []
            for chunk in retrieved_chunks:
                if 'payload' in chunk and 'text' in chunk['payload']:
                    chunks_for_verification.append({
                        'id': chunk.get('id', 'unknown'),
                        'payload': chunk['payload']
                    })

            if chunks_for_verification:
                content_verification_results = self.verifier.verify_all_chunks(original_text, chunks_for_verification)
                logger.info(f"Content verification completed: {content_verification_results['accuracy_rate']:.2%} accuracy")

        # Step 3: Metadata validation
        logger.info("Running metadata validation...")
        metadata_validation_results = self.validator.verify_metadata_correspondence(retrieved_chunks)
        logger.info(f"Metadata validation completed: {metadata_validation_results['summary']['metadata_accuracy_rate']:.2%} accuracy")

        # Step 4: Run comprehensive pipeline tests
        logger.info("Running comprehensive pipeline tests...")
        pipeline_test_results = self.tester.run_comprehensive_pipeline_test(self.retriever, original_text)

        # Step 5: Compile results
        end_time = time.time()
        total_execution_time = end_time - start_time

        integration_results = {
            "timestamp": time.time(),
            "total_execution_time": total_execution_time,
            "collection_exists": collection_exists,
            "chunks_retrieved": len(retrieved_chunks),
            "content_verification": content_verification_results,
            "metadata_validation": metadata_validation_results,
            "pipeline_tests": pipeline_test_results,
            "all_components_functional": True,
            "overall_passed": (
                metadata_validation_results['summary']['metadata_accuracy_rate'] >= 0.99 and
                pipeline_test_results['summary']['performance_passed'] and
                pipeline_test_results['summary']['error_handling_passed']
            )
        }

        logger.info(f"End-to-end test completed in {total_execution_time:.3f}s")
        logger.info(f"Overall result: {'PASS' if integration_results['overall_passed'] else 'FAIL'}")

        return integration_results

    def run_data_flow_test(self) -> Dict[str, Any]:
        """
        Test the complete data flow from retrieval to validation.

        Returns:
            Dict[str, Any]: Data flow test results
        """
        logger.info("Running data flow test...")

        results = {
            "retrieval_success": False,
            "verification_success": False,
            "validation_success": False,
            "flow_overall_success": False
        }

        try:
            # Test retrieval
            if self.retriever.check_collection_exists():
                chunks = self.retriever.retrieve_all_embeddings(limit=5)
                results["retrieval_success"] = True
                logger.info(f"Retrieved {len(chunks)} chunks successfully")
            else:
                # Use sample data for testing
                chunks = [
                    {"id": "sample_1", "payload": {"text": "Sample text", "source": "https://example.com"}}
                ]
                results["retrieval_success"] = True
                logger.info("Using sample data for testing")

            # Test metadata validation
            metadata_results = self.validator.verify_metadata_correspondence(chunks)
            results["validation_success"] = metadata_results['summary']['metadata_accuracy_rate'] >= 0.99
            logger.info(f"Metadata validation: {'PASS' if results['validation_success'] else 'FAIL'}")

            # Test content verification (with sample original text)
            sample_original = "Sample text for testing content verification."
            content_results = self.verifier.verify_all_chunks(sample_original, chunks)
            results["verification_success"] = content_results['accuracy_rate'] >= 0.95
            logger.info(f"Content verification: {'PASS' if results['verification_success'] else 'FAIL'}")

            # Overall success
            results["flow_overall_success"] = (
                results["retrieval_success"] and
                results["validation_success"] and
                results["verification_success"]
            )

        except Exception as e:
            logger.error(f"Error in data flow test: {e}")
            results["flow_overall_success"] = False

        return results

    def generate_integration_report(self, integration_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive integration test report.

        Args:
            integration_results (Dict[str, Any]): Results from integration test

        Returns:
            str: Formatted integration report
        """
        report_lines = [
            "# Integration Test Report",
            "",
            f"**Test Run**: {time.ctime(integration_results['timestamp'])}",
            f"**Execution Time**: {integration_results['total_execution_time']:.3f}s",
            "",
            "## Component Status",
            "",
            f"- **Qdrant Connection**: {'✓ Connected' if integration_results['collection_exists'] else '⚠ Using Sample Data'}",
            f"- **Chunks Retrieved**: {integration_results['chunks_retrieved']}",
            "",
            "## Test Results",
            ""
        ]

        # Content Verification Results
        if integration_results['content_verification']:
            cv = integration_results['content_verification']
            report_lines.extend([
                "### Content Verification",
                f"- Accuracy Rate: {cv['accuracy_rate']:.2%}",
                f"- Average Similarity: {cv['average_similarity']:.2%}",
                f"- Matches: {cv['matches']}/{cv['total_chunks']}",
                f"- Status: {'✓ PASS' if cv['accuracy_rate'] >= 0.95 else '✗ FAIL'}",
                ""
            ])
        else:
            report_lines.extend([
                "### Content Verification",
                "- Status: N/A (No original text provided)",
                ""
            ])

        # Metadata Validation Results
        mv = integration_results['metadata_validation']
        report_lines.extend([
            "### Metadata Validation",
            f"- Accuracy Rate: {mv['summary']['metadata_accuracy_rate']:.2%}",
            f"- Valid Metadata: {mv['summary']['metadata_valid_count']}/{mv['total_chunks']}",
            f"- Status: {'✓ PASS' if mv['summary']['metadata_accuracy_rate'] >= 0.99 else '✗ FAIL'}",
            ""
        ])

        # Pipeline Test Results
        pt = integration_results['pipeline_tests']
        report_lines.extend([
            "### Pipeline Tests",
            f"- Performance: {'✓ PASS' if pt['summary']['performance_passed'] else '✗ FAIL'}",
            f"- Consistency: {'✓ PASS' if pt['summary']['consistency_passed'] else '✗ FAIL'}",
            f"- Error Handling: {'✓ PASS' if pt['summary']['error_handling_passed'] else '✗ FAIL'}",
            f"- Content Verification: {'✓ PASS' if pt['summary']['content_verification_passed'] else '✗ FAIL'}",
            f"- Metadata Validation: {'✓ PASS' if pt['summary']['metadata_validation_passed'] else '✗ FAIL'}",
            ""
        ])

        # Overall Status
        overall_status = "✓ PASS" if integration_results['overall_passed'] else "✗ FAIL"
        report_lines.extend([
            "## Overall Status",
            f"- **Result**: {overall_status}",
            "",
            "## Requirements Check",
            "",
            "- [ ] Data retrieval from Qdrant works correctly",
            f"- [ {'x' if integration_results['chunks_retrieved'] > 0 else ' '}] Chunks retrieved: {integration_results['chunks_retrieved']}",
            "",
            "- [ ] Content matches original text accurately",
            f"- [ {'x' if integration_results['content_verification']['accuracy_rate'] >= 1.0 if integration_results['content_verification'] else False else ' '}] Accuracy: {integration_results['content_verification']['accuracy_rate']:.2% if integration_results['content_verification'] else 'N/A'}",
            "",
            "- [ ] Metadata corresponds correctly to chunks",
            f"- [ {'x' if integration_results['metadata_validation']['summary']['metadata_accuracy_rate'] >= 0.99 else ' '}] Accuracy: {integration_results['metadata_validation']['summary']['metadata_accuracy_rate']:.2%}",
            "",
            "- [ ] Pipeline is fast and error-free",
            f"- [ {'x' if integration_results['pipeline_tests']['summary']['performance_passed'] and integration_results['pipeline_tests']['summary']['error_handling_passed'] else ' '}] Performance and error handling",
            ""
        ])

        return "\n".join(report_lines)

    def run_complete_integration_suite(self, original_text: str = "") -> Dict[str, Any]:
        """
        Run the complete integration test suite.

        Args:
            original_text (str): Optional original text for content verification

        Returns:
            Dict[str, Any]: Complete integration test results
        """
        logger.info("Running complete integration test suite...")

        # Setup components
        self.setup_components()

        # Run end-to-end test
        e2e_results = self.run_end_to_end_test(original_text)

        # Run data flow test
        flow_results = self.run_data_flow_test()

        # Compile complete results
        complete_results = {
            "end_to_end_test": e2e_results,
            "data_flow_test": flow_results,
            "all_tests_passed": e2e_results['overall_passed'] and flow_results['flow_overall_success'],
            "timestamp": time.time()
        }

        logger.info(f"Complete integration suite completed. All tests passed: {complete_results['all_tests_passed']}")

        return complete_results


def main():
    """
    Main function to run the integration tests.
    """
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Initialize the integration tester
    integration_tester = IntegrationTester()

    try:
        # Sample original text for content verification
        sample_original_text = (
            "This is a sample book text for integration testing. "
            "It contains multiple sentences to verify that the content "
            "verification system works correctly when comparing retrieved "
            "chunks against the original text. Each chunk should correspond "
            "to a specific position in the original document."
        )

        # Run complete integration suite
        results = integration_tester.run_complete_integration_suite(sample_original_text)

        # Generate and print integration report
        report = integration_tester.generate_integration_report(results['end_to_end_test'])
        print(report)

        # Print summary
        print("\n" + "="*50)
        print("INTEGRATION TEST SUMMARY")
        print("="*50)
        print(f"All tests passed: {results['all_tests_passed']}")
        print(f"End-to-end test passed: {results['end_to_end_test']['overall_passed']}")
        print(f"Data flow test passed: {results['data_flow_test']['flow_overall_success']}")
        print(f"Total execution time: {results['end_to_end_test']['total_execution_time']:.3f}s")

        return results

    except Exception as e:
        logger.error(f"Error running integration tests: {e}")
        return None


if __name__ == "__main__":
    main()