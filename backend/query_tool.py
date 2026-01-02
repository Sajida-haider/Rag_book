"""
Query tool for the RAG system that can handle command-line arguments.
Usage: python -m backend.query_tool --query "What is ROS2?" --verbose
"""
import sys
import argparse
import os
from dotenv import load_dotenv

# Add backend to path for imports
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

from services.rag_service import RAGService

def main():
    parser = argparse.ArgumentParser(description='Query the RAG system')
    parser.add_argument('--query', '-q', type=str, required=True, help='Query to search for')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return (default: 5)')

    args = parser.parse_args()

    if args.verbose:
        print(f"Query: '{args.query}'")
        print(f"Top K: {args.top_k}")
        print("-" * 50)

    try:
        # Initialize the RAG service
        rag_service = RAGService()

        if args.verbose:
            print("RAG Service initialized successfully")
            print("Processing query...")

        # Perform the query
        results = rag_service.query(args.query, top_k=args.top_k)

        print(f"\nFound {len(results)} results for query: '{args.query}'")
        print("="*60)

        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Section: {result.get('section', 'N/A')}")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Content preview: {result.get('content', '')[:300]}...")
            if len(result.get('content', '')) > 300:
                print(f"  ... (truncated from {len(result.get('content', ''))} characters)")
            print("-" * 40)

        # Also show context that would be used for generation
        if args.verbose:
            print(f"\nGenerating context for LLM...")
            context = rag_service.get_context_for_generation(args.query, max_context_length=2000)
            print(f"Context length: {len(context)} characters")
            print("\nContext that would be used for answer generation:")
            print("="*60)
            print(context[:1000] + "..." if len(context) > 1000 else context)

        return results

    except Exception as e:
        print(f"Error during query: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return None

if __name__ == "__main__":
    main()