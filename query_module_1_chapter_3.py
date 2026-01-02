"""Script to query specifically for Module 1 Chapter 3 content"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.services.rag_service import RAGService

def query_module_1_chapter_3():
    """Query specifically for Module 1 Chapter 3 content about URDF humanoid models"""
    print("=== Querying for Module 1 Chapter 3: Humanoid Robot Description with URDF ===\n")

    try:
        # Initialize RAG service
        rag_service = RAGService()
        print("RAG Service initialized successfully")

        # Specific query for Module 1 Chapter 3
        queries = [
            "Module 1 Chapter 3 humanoid robot description with URDF",
            "humanoid robot description with URDF",
            "URDF humanoid models",
            "Chapter 3 Humanoid Robot Description"
        ]

        for query in queries:
            print(f"\nQuery: '{query}'")
            print("-" * 50)

            # Perform query
            results = rag_service.query(query, top_k=5)
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

                # Check if this is likely Module 1 Chapter 3
                if 'module-1' in url.lower() and ('chapter-3' in url.lower() or 'humanoid' in content.lower() or 'urdf' in content.lower()):
                    print(f"    Content preview: {content[:500]}...")
                    print(f"    Full content length: {len(content)} characters")

                print()

                # If we found the right content, let's print more details
                if 'chapter-3' in url.lower() or ('module-1' in url.lower() and 'humanoid' in content.lower() and 'urdf' in content.lower()):
                    print("FOUND Module 1 Chapter 3 content!")
                    print("="*60)
                    print("First paragraph/section:")
                    # Extract the first paragraph-like content
                    lines = content.split('\n')
                    first_paragraph = ""
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and len(line) > 20:  # Skip headers and short lines
                            first_paragraph = line
                            break
                    print(f"First paragraph: {first_paragraph}")
                    print("="*60)
                    break
            else:
                continue
            break  # Break outer loop if we found the content

    except Exception as e:
        print(f"Error in query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    query_module_1_chapter_3()