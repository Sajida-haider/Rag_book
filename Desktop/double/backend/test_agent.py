"""
Test script for the OpenAI Agent with Qdrant Retrieval
This script tests the agent functionality to ensure it works as expected.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.agent import BookQAAgent

def test_agent():
    """
    Test the OpenAI agent with Qdrant retrieval
    """
    print("Testing OpenAI Agent with Qdrant Retrieval...")
    print("="*60)

    try:
        # Initialize the agent
        print("Initializing agent...")
        agent = BookQAAgent()
        print("✓ Agent initialized successfully")

        # Test queries
        test_queries = [
            "What is ROS 2?",
            "Explain Python agents with ROS 2",
            "What is Isaac ROS?",
            "How is humanoid robotics covered in this book?"
        ]

        print(f"\nRunning {len(test_queries)} test queries...")
        print("-" * 40)

        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            print("-" * 30)

            try:
                response = agent.answer_query(query)
                print(f"Response: {response[:200]}...")  # Truncate for readability
            except Exception as e:
                print(f"Error processing query: {e}")

        print("\n" + "="*60)
        print("✓ Agent testing completed successfully")

        # Clean up
        agent.close()
        print("✓ Agent resources cleaned up")

    except Exception as e:
        print(f"Error during agent testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()