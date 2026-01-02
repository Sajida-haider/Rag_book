"""
Test script to query the RAG system with 'explain Ros 2'
This script demonstrates how to use the existing RAG service to answer queries.
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path for imports
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

from services.rag_service import RAGService

def test_query():
    """
    Test the RAG service with the specific query 'explain Ros 2'
    """
    print("Initializing RAG Service...")

    try:
        # Initialize the RAG service
        rag_service = RAGService()
        print("RAG Service initialized successfully")

        # Test query
        query = "explain Ros 2"
        print(f"\nQuery: '{query}'")

        # Perform the query
        results = rag_service.query(query, top_k=5)

        print(f"\nFound {len(results)} results:")
        print("="*50)

        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Section: {result.get('section', 'N/A')}")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Content preview: {result.get('content', '')[:200]}...")
            print("-" * 30)

        # Also get the full context that would be used for generation
        print(f"\nGetting context for generation...")
        context = rag_service.get_context_for_generation(query, max_context_length=1000)
        print(f"Context length: {len(context)} characters")

        if context:
            print("\nContext preview:")
            print("="*50)
            print(context[:500] + "..." if len(context) > 500 else context)
        else:
            print("No context found for this query.")

        return results

    except Exception as e:
        print(f"Error during query: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_query()