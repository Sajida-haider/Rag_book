"""Script to use the RAG service to search for the specific content mentioned"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.services.rag_service import RAGService

def search_for_specific_content():
    """Search for the specific content mentioned by the user"""
    print("=== Searching for specific content in the database ===\n")

    try:
        # Initialize RAG service
        rag_service = RAGService()
        print("RAG Service initialized successfully")

        # Search for the specific content mentioned by the user
        specific_queries = [
            "This capstone chapter integrates all the concepts from the Vision-Language-Action (VLA) module",
            "Vision-Language-Action module capstone autonomous humanoid",
            "overview capstone autonomous humanoid project",
            "perception planning navigation simulation environments",
            "voice command to robot action pipeline"
        ]

        for query in specific_queries:
            print(f"\nSearching for: '{query}'")
            print("-" * 60)

            # Perform query
            results = rag_service.query(query, top_k=3)
            print(f"Found {len(results)} results:")

            for i, result in enumerate(results, 1):
                title = result.get('title', 'N/A')
                url = result.get('url', 'N/A')
                content = result.get('content', '')
                score = result.get('score', 0)

                print(f"  Result {i}:")
                print(f"    Title: {title}")
                print(f"    URL: {url}")
                print(f"    Score: {score:.4f}")
                print(f"    Content preview: {content[:300]}...")
                print()

    except Exception as e:
        print(f"Error in search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_for_specific_content()