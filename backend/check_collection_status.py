#!/usr/bin/env python3
"""
Script to check Qdrant collection status and existing vectors before ingestion
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.vector_storage import VectorStorageService

def check_collection_status():
    """Check the status of the Qdrant collection"""
    try:
        storage_service = VectorStorageService()

        # Get collection info
        collection_info = storage_service.client.get_collection(storage_service.collection_name)

        print(f"Collection: {storage_service.collection_name}")
        print(f"Points count: {collection_info.points_count}")
        print(f"Status: {collection_info.status}")

        # Check configuration
        if hasattr(collection_info.config.params, 'vectors'):
            vector_config = collection_info.config.params.vectors
            if hasattr(vector_config, 'size'):
                print(f"Vector size: {vector_config.size}")
            if hasattr(vector_config, 'distance'):
                print(f"Distance: {vector_config.distance}")

        return collection_info.points_count
    except Exception as e:
        print(f"Error checking collection status: {e}")
        return 0

def main():
    print("Checking Qdrant collection status...")
    print("=" * 50)

    vector_count = check_collection_status()

    print("=" * 50)
    print(f"Found {vector_count} vectors in the collection")
    print("You can now proceed with ingestion, and duplicate vectors will be skipped.")

if __name__ == "__main__":
    main()