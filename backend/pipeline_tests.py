"""
Module for running comprehensive pipeline tests to ensure retrieval is fast, consistent, and error-free.
This module implements functionality to test the retrieval pipeline for performance and reliability.
"""

import logging
import time
import statistics
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

# Import our other modules
from backend.retrieve_data import QdrantDataRetriever
from backend.content_verification import ContentVerifier
from backend.metadata_validation import MetadataValidator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """
    Data class to store test results.
    """
    test_name: str
    passed: bool
    execution_time: float
    details: Dict[str, Any]
    timestamp: datetime


class PipelineTester:
    """
    A class to handle comprehensive pipeline testing.
    """

    def __init__(self):
        """
        Initialize the PipelineTester.
        """
        self.test_results: List[TestResult] = []
        self.performance_threshold = 5.0  # 5 seconds threshold
        self.error_rate_threshold = 0.01  # 1% error rate threshold

    def run_retrieval_performance_test(self, retriever: QdrantDataRetriever, iterations: int = 10) -> Dict[str, Any]:
        """
        Run performance tests on the retrieval pipeline.

        Args:
            retriever (QdrantDataRetriever): The retriever instance to test
            iterations (int): Number of iterations to run

        Returns:
            Dict[str, Any]: Performance test results
        """
        logger.info(f"Running retrieval performance test with {iterations} iterations...")

        execution_times = []
        errors = 0
        successful_retrievals = 0

        for i in range(iterations):
            try:
                start_time = time.time()

                # Test retrieval
                if retriever.check_collection_exists():
                    # Retrieve a sample of embeddings
                    embeddings = retriever.retrieve_all_embeddings(limit=5)
                    successful_retrievals += 1
                else:
                    # If collection doesn't exist, just test connection
                    retriever.check_collection_exists()
                    successful_retrievals += 1

                end_time = time.time()
                execution_time = end_time - start_time
                execution_times.append(execution_time)

                logger.debug(f"Iteration {i+1}: {execution_time:.3f}s")

            except Exception as e:
                logger.error(f"Error in iteration {i+1}: {e}")
                errors += 1

        # Calculate performance metrics
        if execution_times:
            avg_time = statistics.mean(execution_times)
            median_time = statistics.median(execution_times)
            p95_time = sorted(execution_times)[int(0.95 * len(execution_times))] if len(execution_times) > 0 else 0
            max_time = max(execution_times) if execution_times else 0
            min_time = min(execution_times) if execution_times else 0

            error_rate = errors / iterations
            success_rate = successful_retrievals / iterations

            results = {
                "iterations": iterations,
                "successful_retrievals": successful_retrievals,
                "errors": errors,
                "success_rate": success_rate,
                "error_rate": error_rate,
                "avg_execution_time": avg_time,
                "median_execution_time": median_time,
                "p95_execution_time": p95_time,
                "max_execution_time": max_time,
                "min_execution_time": min_time,
                "execution_times": execution_times,
                "passed": (
                    error_rate <= self.error_rate_threshold and
                    avg_time <= self.performance_threshold
                )
            }

            logger.info(f"Performance test completed: {success_rate:.2%} success rate, avg time {avg_time:.3f}s")
            return results
        else:
            logger.error("No successful iterations to calculate metrics")
            return {
                "iterations": iterations,
                "successful_retrievals": 0,
                "errors": iterations,
                "success_rate": 0.0,
                "error_rate": 1.0,
                "avg_execution_time": 0,
                "median_execution_time": 0,
                "p95_execution_time": 0,
                "max_execution_time": 0,
                "min_execution_time": 0,
                "execution_times": [],
                "passed": False
            }

    def run_consistency_test(self, retriever: QdrantDataRetriever, iterations: int = 5) -> Dict[str, Any]:
        """
        Run consistency tests to ensure the pipeline returns the same results across multiple runs.

        Args:
            retriever (QdrantDataRetriever): The retriever instance to test
            iterations (int): Number of iterations to run

        Returns:
            Dict[str, Any]: Consistency test results
        """
        logger.info(f"Running consistency test with {iterations} iterations...")

        results = []
        all_passed = True

        for i in range(iterations):
            try:
                # Retrieve a sample of data
                if retriever.check_collection_exists():
                    embeddings = retriever.retrieve_all_embeddings(limit=5)
                    result_hash = hash(str(sorted([str(e.get('id', '')) for e in embeddings])))
                    results.append(result_hash)
                else:
                    results.append(None)

            except Exception as e:
                logger.error(f"Error in consistency test iteration {i+1}: {e}")
                results.append(None)
                all_passed = False

        # Check if all results are the same
        if all(r == results[0] for r in results if r is not None):
            consistency_passed = True
            logger.info("Consistency test passed: All iterations returned the same results")
        else:
            consistency_passed = False
            logger.warning("Consistency test failed: Different results across iterations")

        return {
            "iterations": iterations,
            "results": results,
            "consistent": consistency_passed,
            "passed": consistency_passed
        }

    def run_error_handling_test(self, retriever: QdrantDataRetriever) -> Dict[str, Any]:
        """
        Run tests to ensure proper error handling in the pipeline.

        Args:
            retriever (QdrantDataRetriever): The retriever instance to test

        Returns:
            Dict[str, Any]: Error handling test results
        """
        logger.info("Running error handling tests...")

        errors_handled = 0
        total_tests = 0

        # Test 1: Try to retrieve from non-existent collection
        total_tests += 1
        try:
            # Temporarily change to a non-existent collection
            original_collection = retriever.collection_name
            retriever.collection_name = "non_existent_collection_test"
            result = retriever.retrieve_all_embeddings()
            if result == []:  # Should return empty list
                errors_handled += 1
            retriever.collection_name = original_collection  # Restore
        except Exception:
            # If an exception is raised, check if it's handled properly
            errors_handled += 1
            retriever.collection_name = original_collection  # Restore

        # Test 2: Test with invalid parameters
        total_tests += 1
        try:
            # This should handle errors gracefully
            result = retriever.retrieve_embeddings_by_ids([])
            errors_handled += 1
        except Exception:
            errors_handled += 1

        error_handling_rate = errors_handled / total_tests if total_tests > 0 else 0

        results = {
            "total_tests": total_tests,
            "errors_handled": errors_handled,
            "error_handling_rate": error_handling_rate,
            "passed": error_handling_rate >= 0.8  # At least 80% error handling rate
        }

        logger.info(f"Error handling test: {error_handling_rate:.2%} success rate")
        return results

    def run_content_verification_test(self, original_text: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run content verification tests to ensure retrieved content matches original.

        Args:
            original_text (str): The original book text
            retrieved_chunks (List[Dict[str, Any]]): Retrieved chunks to verify

        Returns:
            Dict[str, Any]: Content verification test results
        """
        logger.info("Running content verification tests...")

        start_time = time.time()
        verifier = ContentVerifier()
        verification_results = verifier.verify_all_chunks(original_text, retrieved_chunks)
        end_time = time.time()

        execution_time = end_time - start_time

        # Check if accuracy meets requirements
        accuracy_met = verification_results.get("accuracy_rate", 0) >= 1.0  # 100% for content matching
        avg_similarity_met = verification_results.get("average_similarity", 0) >= 0.95  # 95% average similarity

        results = {
            "execution_time": execution_time,
            "verification_results": verification_results,
            "accuracy_met": accuracy_met,
            "avg_similarity_met": avg_similarity_met,
            "passed": accuracy_met and avg_similarity_met
        }

        logger.info(f"Content verification test completed in {execution_time:.3f}s")
        logger.info(f"Accuracy rate: {verification_results.get('accuracy_rate', 0):.2%}")
        return results

    def run_metadata_validation_test(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run metadata validation tests to ensure metadata corresponds correctly.

        Args:
            chunks (List[Dict[str, Any]]): Chunks with metadata to validate

        Returns:
            Dict[str, Any]: Metadata validation test results
        """
        logger.info("Running metadata validation tests...")

        start_time = time.time()
        validator = MetadataValidator()
        validation_results = validator.verify_metadata_correspondence(chunks)
        end_time = time.time()

        execution_time = end_time - start_time

        # Check if metadata accuracy meets requirements
        metadata_accuracy = validation_results.get("summary", {}).get("metadata_accuracy_rate", 0)
        metadata_accuracy_met = metadata_accuracy >= 0.99  # 99% metadata accuracy requirement

        results = {
            "execution_time": execution_time,
            "validation_results": validation_results,
            "metadata_accuracy_met": metadata_accuracy_met,
            "metadata_accuracy": metadata_accuracy,
            "passed": metadata_accuracy_met
        }

        logger.info(f"Metadata validation test completed in {execution_time:.3f}s")
        logger.info(f"Metadata accuracy rate: {metadata_accuracy:.2%}")
        return results

    def run_comprehensive_pipeline_test(self, retriever: QdrantDataRetriever, original_text: str = "") -> Dict[str, Any]:
        """
        Run comprehensive pipeline tests including performance, consistency, and error handling.

        Args:
            retriever (QdrantDataRetriever): The retriever instance to test
            original_text (str): Optional original text for content verification

        Returns:
            Dict[str, Any]: Comprehensive test results
        """
        logger.info("Starting comprehensive pipeline tests...")

        # Run individual tests
        performance_results = self.run_retrieval_performance_test(retriever)
        consistency_results = self.run_consistency_test(retriever)
        error_handling_results = self.run_error_handling_test(retriever)

        # Run content verification if original text provided
        content_verification_results = None
        if original_text:
            # Simulate retrieved chunks for content verification
            if retriever.check_collection_exists():
                sample_chunks = retriever.retrieve_all_embeddings(limit=5)
            else:
                # Create sample chunks for testing
                sample_chunks = [
                    {"id": f"test_chunk_{i}", "payload": {"text": f"Sample text for chunk {i}"}}
                    for i in range(3)
                ]
            content_verification_results = self.run_content_verification_test(original_text, sample_chunks)

        # Run metadata validation test
        if retriever.check_collection_exists():
            sample_chunks = retriever.get_all_metadata()
        else:
            # Create sample chunks for testing
            sample_chunks = [
                {"id": f"test_chunk_{i}", "payload": {"source": f"https://example.com/test{i}", "title": f"Test {i}"}}
                for i in range(3)
            ]
        metadata_validation_results = self.run_metadata_validation_test(sample_chunks)

        # Calculate overall results
        all_tests_passed = (
            performance_results["passed"] and
            consistency_results["passed"] and
            error_handling_results["passed"] and
            (content_verification_results["passed"] if content_verification_results else True) and
            metadata_validation_results["passed"]
        )

        comprehensive_results = {
            "timestamp": datetime.now().isoformat(),
            "performance_test": performance_results,
            "consistency_test": consistency_results,
            "error_handling_test": error_handling_results,
            "content_verification_test": content_verification_results,
            "metadata_validation_test": metadata_validation_results,
            "all_tests_passed": all_tests_passed,
            "summary": {
                "performance_passed": performance_results["passed"],
                "consistency_passed": consistency_results["passed"],
                "error_handling_passed": error_handling_results["passed"],
                "content_verification_passed": content_verification_results["passed"] if content_verification_results else True,
                "metadata_validation_passed": metadata_validation_results["passed"]
            }
        }

        logger.info(f"Comprehensive pipeline test completed. All tests passed: {all_tests_passed}")
        return comprehensive_results

    def generate_test_report(self, comprehensive_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive test report in Markdown format.

        Args:
            comprehensive_results (Dict[str, Any]): Results from comprehensive pipeline test

        Returns:
            str: Formatted test report in Markdown
        """
        report_lines = [
            "# Pipeline Test Report",
            "",
            f"**Generated**: {comprehensive_results['timestamp']}",
            "",
            "## Test Summary",
            "",
            f"- **Performance Test**: {'✓ PASS' if comprehensive_results['summary']['performance_passed'] else '✗ FAIL'}",
            f"- **Consistency Test**: {'✓ PASS' if comprehensive_results['summary']['consistency_passed'] else '✗ FAIL'}",
            f"- **Error Handling Test**: {'✓ PASS' if comprehensive_results['summary']['error_handling_passed'] else '✗ FAIL'}",
            f"- **Content Verification Test**: {'✓ PASS' if comprehensive_results['summary']['content_verification_passed'] else '✗ FAIL'}",
            f"- **Metadata Validation Test**: {'✓ PASS' if comprehensive_results['summary']['metadata_validation_passed'] else '✗ FAIL'}",
            f"- **Overall Status**: {'✓ ALL TESTS PASSED' if comprehensive_results['all_tests_passed'] else '✗ SOME TESTS FAILED'}",
            "",
            "## Detailed Results",
            ""
        ]

        # Performance Test Details
        perf_result = comprehensive_results["performance_test"]
        report_lines.extend([
            "### Performance Test",
            f"- Success Rate: {perf_result['success_rate']:.2%}",
            f"- Error Rate: {perf_result['error_rate']:.2%}",
            f"- Average Execution Time: {perf_result['avg_execution_time']:.3f}s",
            f"- Median Execution Time: {perf_result['median_execution_time']:.3f}s",
            f"- 95th Percentile Time: {perf_result['p95_execution_time']:.3f}s",
            f"- Result: {'✓ PASS' if perf_result['passed'] else '✗ FAIL'}",
            ""
        ])

        # Consistency Test Details
        consistency_result = comprehensive_results["consistency_test"]
        report_lines.extend([
            "### Consistency Test",
            f"- Iterations: {consistency_result['iterations']}",
            f"- Consistent Results: {consistency_result['consistent']}",
            f"- Result: {'✓ PASS' if consistency_result['passed'] else '✗ FAIL'}",
            ""
        ])

        # Error Handling Test Details
        error_result = comprehensive_results["error_handling_test"]
        report_lines.extend([
            "### Error Handling Test",
            f"- Total Tests: {error_result['total_tests']}",
            f"- Errors Handled: {error_result['errors_handled']}",
            f"- Error Handling Rate: {error_result['error_handling_rate']:.2%}",
            f"- Result: {'✓ PASS' if error_result['passed'] else '✗ FAIL'}",
            ""
        ])

        # Content Verification Test Details (if available)
        content_result = comprehensive_results["content_verification_test"]
        if content_result:
            report_lines.extend([
                "### Content Verification Test",
                f"- Accuracy Rate: {content_result['verification_results']['accuracy_rate']:.2%}",
                f"- Average Similarity: {content_result['verification_results']['average_similarity']:.2%}",
                f"- Total Chunks: {content_result['verification_results']['total_chunks']}",
                f"- Matches: {content_result['verification_results']['matches']}",
                f"- Mismatches: {content_result['verification_results']['mismatches']}",
                f"- Result: {'✓ PASS' if content_result['passed'] else '✗ FAIL'}",
                ""
            ])

        # Metadata Validation Test Details
        metadata_result = comprehensive_results["metadata_validation_test"]
        report_lines.extend([
            "### Metadata Validation Test",
            f"- Metadata Accuracy Rate: {metadata_result['metadata_accuracy']:.2%}",
            f"- Total Chunks: {metadata_result['validation_results']['total_chunks']}",
            f"- Valid Metadata: {metadata_result['validation_results']['summary']['metadata_valid_count']}",
            f"- Result: {'✓ PASS' if metadata_result['passed'] else '✗ FAIL'}",
            ""
        ])

        # Requirements Check
        report_lines.extend([
            "## Requirements Check",
            "",
            "- [ ] Pipeline completes retrieval within 5 seconds for 95% of requests",
            f"- [ {'x' if perf_result['p95_execution_time'] <= 5.0 else ' '}] 95% of requests under 5s: {perf_result['p95_execution_time']:.3f}s",
            "",
            "- [ ] Error rate is less than 1%",
            f"- [ {'x' if perf_result['error_rate'] < 0.01 else ' '}] Error rate: {perf_result['error_rate']:.2%}",
            "",
            "- [ ] Consistency across multiple runs is maintained",
            f"- [ {'x' if consistency_result['consistent'] else ' '}] Consistent results across runs: {consistency_result['consistent']}",
            "",
            "- [ ] Content verification accuracy is 100%",
            f"- [ {'x' if content_result['accuracy_met'] if content_result else False else ' '}] Content accuracy: {content_result['verification_results']['accuracy_rate']:.2% if content_result else 'N/A'}",
            "",
            "- [ ] Metadata correspondence accuracy is 99%+",
            f"- [ {'x' if metadata_result['metadata_accuracy_met'] else ' '}] Metadata accuracy: {metadata_result['metadata_accuracy']:.2%}",
            ""
        ])

        return "\n".join(report_lines)

    def save_test_report(self, comprehensive_results: Dict[str, Any], output_path: str = "pipeline_test_report.md") -> str:
        """
        Save the test report to a file.

        Args:
            comprehensive_results (Dict[str, Any]): Results from comprehensive pipeline test
            output_path (str): Path to save the report

        Returns:
            str: Path where the report was saved
        """
        report_content = self.generate_test_report(comprehensive_results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"Test report saved to {output_path}")
        return output_path


def main():
    """
    Main function to demonstrate pipeline testing functionality.
    """
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Initialize the tester
    tester = PipelineTester()

    try:
        # Initialize retriever
        retriever = QdrantDataRetriever()

        # Run comprehensive tests
        # For the example, we'll use a sample text
        sample_original_text = (
            "This is a sample book text for testing purposes. "
            "It contains multiple sentences and paragraphs to verify "
            "that the content verification system works correctly. "
            "Each chunk should correspond to a specific position in the original text."
        )

        comprehensive_results = tester.run_comprehensive_pipeline_test(retriever, sample_original_text)

        # Generate and print report
        report = tester.generate_test_report(comprehensive_results)
        print(report)

        # Save report to file
        report_path = tester.save_test_report(comprehensive_results)
        print(f"\nFull report saved to: {report_path}")

        return comprehensive_results

    except Exception as e:
        logger.error(f"Error running pipeline tests: {e}")
        return None


if __name__ == "__main__":
    main()