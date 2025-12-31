#!/usr/bin/env python3
"""
Quickstart validation script for the book embeddings RAG system
"""

import os
import sys
from pathlib import Path

def validate_setup():
    """Validate that all required files and environment variables are set up correctly"""
    print("Validating setup...")

    # Check that required files exist
    required_files = [
        "requirements.txt",
        "main.py",
        ".env",
        "models.py",
        "services/web_scraper.py",
        "services/content_extractor.py",
        "services/content_cleaner.py",
        "services/url_crawler.py",
        "services/content_chunker.py",
        "services/embedding_generator.py",
        "services/vector_storage.py"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")

    # Check that environment variables are set
    required_env_vars = [
        "COHERE_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "BOOK_URL"
    ]

    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)

    if missing_env_vars:
        print(f"⚠️  Missing environment variables: {missing_env_vars}")
        print("   These are required for full functionality but can be set before running the main script")
    else:
        print("✅ All required environment variables are set")

    # Check that requirements can be imported
    required_packages = [
        "requests",
        "bs4",  # beautifulsoup4
        "cohere",
        "qdrant_client",
        "dotenv"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if package == "bs4":
                __import__("bs4")
            elif package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {missing_packages}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages can be imported")

    print("\n✅ Setup validation passed!")
    return True

def main():
    """Main validation function"""
    print("Running quickstart validation...\n")

    success = validate_setup()

    if success:
        print("\n🎉 Quickstart validation successful!")
        print("\nYou can now run the ingestion pipeline with:")
        print("  python main.py")
        print("\nFor re-ingestion of updated content:")
        print("  python main.py reingest")
    else:
        print("\n❌ Quickstart validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()