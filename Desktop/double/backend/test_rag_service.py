"""Test script for RAG service functionality"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the backend directory to the path so we can import the modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.rag_service import RAGService

# Load environment variables
load_dotenv()

def test_rag_service():
    print("Testing RAG Service...")

    try:
        # Initialize the RAG service
        rag_service = RAGService()
        print("+ RAG Service initialized successfully")

        # Test query - use a sample question that might match book content
        test_questions = [
            "What is RAG?",
            "Explain Retrieval-Augmented Generation",
            "How does a RAG system work?",
            "What are the components of a RAG system?"
        ]

        print("\nTesting queries...")
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Query: {question}")
            try:
                start_time = time.time()

                # Test the query function
                results = rag_service.query(question, top_k=3)

                end_time = time.time()
                print(f"   Time taken: {end_time - start_time:.2f} seconds")
                print(f"   Results found: {len(results)}")

                if results:
                    for j, result in enumerate(results[:2], 1):  # Show first 2 results
                        print(f"   Result {j}:")
                        print(f"     Title: {result['title'][:50]}...")
                        print(f"     URL: {result['url']}")
                        print(f"     Score: {result['score']:.3f}")
                        print(f"     Content preview: {result['content'][:100]}...")
                else:
                    print("   No results found - this might be expected if no content has been ingested yet")

            except Exception as e:
                print(f"   Error querying: {e}")

        # Test context retrieval
        print(f"\nTesting context retrieval...")
        try:
            sample_question = "What is RAG?"
            context = rag_service.get_context_for_generation(sample_question, max_context_length=1000)
            print(f"+ Context retrieved, length: {len(context)} characters")
            if context:
                print(f"Context preview: {context[:200]}...")
            else:
                print("No context available - make sure content has been ingested into the vector database")
        except Exception as e:
            print(f"Error retrieving context: {e}")

        print("\n+ RAG Service tests completed")

    except Exception as e:
        print(f"- Error initializing RAG Service: {e}")
        import traceback
        traceback.print_exc()

def test_ingestion_status():
    """Check if there's any content in the vector database"""
    print("\nChecking ingestion status...")

    try:
        rag_service = RAGService()

        # Try to get all documentation to see what's available
        docs = rag_service.get_all_documentation()
        print(f"+ Found {len(docs)} documents in the vector database")

        if docs:
            print("Sample documents:")
            for i, doc in enumerate(docs[:3], 1):  # Show first 3 documents
                print(f"  {i}. Title: {doc['title'][:50]}...")
                print(f"     URL: {doc['url']}")
                print(f"     Content length: {len(doc['content'])} chars")

    except Exception as e:
        print(f"Error checking ingestion status: {e}")

if __name__ == "__main__":
    print("Running RAG Service tests...")
    test_ingestion_status()
    test_rag_service()
    print("\nTests completed!")