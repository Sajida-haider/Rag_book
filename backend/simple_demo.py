"""Demo script to showcase the RAG system functionality with book content"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path so we can import the modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.rag_service import RAGService

# Load environment variables
load_dotenv()

def demo_rag_functionality():
    print("RAG System Demo - Book Content Retrieval")
    print("=" * 50)

    # Initialize the RAG service
    rag_service = RAGService()
    print("+ RAG Service initialized successfully")

    # Sample questions to demonstrate the system
    demo_questions = [
        "What is RAG?",
        "Explain Retrieval-Augmented Generation",
        "How does a RAG system work?",
        "What are the components of a RAG system?",
        "Tell me about ROS 2 fundamentals",
        "What is physical AI humanoid robotics?",
    ]

    print(f"\n[BOOK] Available questions to ask the book:")
    for i, question in enumerate(demo_questions, 1):
        print(f"  {i}. {question}")

    print("\n" + "=" * 50)

    print(f"\n[DEMO] Running a quick test query...")

    # Test with a sample query
    test_question = "What is RAG?"
    print(f"Question: {test_question}")

    try:
        # Get the RAG response
        context = rag_service.get_context_for_generation(test_question, max_context_length=2000)
        print(f"\nFound relevant information from the book:")
        print("-" * 30)
        print(context[:500] + "..." if len(context) > 500 else context)  # Limit output
        print("-" * 30)

        # Also show search results for more detail
        results = rag_service.query(test_question, top_k=3)
        print(f"\nTop {len(results)} relevant sections:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Title: {result['title'][:50]}...")
            print(f"     URL: {result['url']}")
            print(f"     Score: {result['score']:.3f}")
            print(f"     Preview: {result['content'][:100]}...")
            print()

    except Exception as e:
        print(f"Error processing test query: {e}")

def show_sample_queries():
    print("\n[SAMPLE] Sample Queries and Results:")
    print("=" * 50)

    rag_service = RAGService()

    sample_questions = [
        "What is RAG?",
        "Physical AI and robotics",
        "ROS 2 fundamentals"
    ]

    for question in sample_questions:
        print(f"\nQuestion: {question}")
        results = rag_service.query(question, top_k=2)

        if results:
            for i, result in enumerate(results[:2], 1):
                print(f"   Result {i}:")
                print(f"     Title: {result['title'][:60]}...")
                print(f"     URL: {result['url']}")
                print(f"     Score: {result['score']:.3f}")
                print(f"     Content preview: {result['content'][:150]}...")
        else:
            print("   No results found")
        print()

if __name__ == "__main__":
    print("Welcome to the RAG System Demo!")
    print("This system allows you to ask questions about book content and get relevant answers.")

    # Show sample queries
    show_sample_queries()

    # Run demo
    demo_rag_functionality()

    print("\nDemo completed successfully!")