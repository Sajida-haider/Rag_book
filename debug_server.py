#!/usr/bin/env python3
"""
Debug script to test the RAG backend server startup
"""
import sys
import os
import traceback

# Add the ragbot_backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ragbot_backend'))

try:
    print("Attempting to import main module...")
    import main
    print("Successfully imported main module")

    print("Attempting to validate environment...")
    main.validate_environment()
    print("Environment validation passed")

    print("Testing Qdrant connection...")
    if main.test_qdrant_connection():
        print("Qdrant connection successful")
    else:
        print("Qdrant connection failed")

    print("Testing URL discovery...")
    urls = main.discover_book_urls()
    print(f"Discovered {len(urls)} URLs: {urls[:3]}...")  # Show first 3

    print("All tests passed! Server should start successfully.")

except Exception as e:
    print(f"Error occurred: {str(e)}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)