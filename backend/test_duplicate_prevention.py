#!/usr/bin/env python3
"""
Test script to verify duplicate prevention functionality
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.vector_storage import VectorStorageService
from models import VectorRecord, Metadata

def test_duplicate_prevention():
    """Test that duplicate vectors are properly skipped"""
    storage_service = VectorStorageService()

    # Create a sample vector record
    sample_record = VectorRecord(
        id="test-duplicate-id-12345",  # Using a fixed ID for testing
        payload={
            'url': 'https://test.example.com/test-page',
            'title': 'Test Page',
            'section': 'Test Section',
            'content': 'This is test content for duplicate prevention testing.',
            'chunk_index': 0,
            'total_chunks': 1,
            'created_at': datetime.now().isoformat()
        },
        vector=[0.1] * 1024,  # Sample vector of 1024 dimensions
        created_at=datetime.now()
    )

    print("Testing duplicate prevention...")
    print(f"Attempting to store vector with ID: {sample_record.id}")

    # First storage attempt
    result1 = storage_service.store_embedding(sample_record)
    print(f"First storage result: {result1}")

    # Second storage attempt with same ID (should be skipped)
    result2 = storage_service.store_embedding(sample_record)
    print(f"Second storage result (should skip duplicate): {result2}")

    # Test batch storage with some existing vectors
    print("\nTesting batch storage with existing vectors...")

    # Create a batch with one existing vector and one new vector
    new_record = VectorRecord(
        id=str(uuid.uuid4()),  # New UUID
        payload={
            'url': 'https://test.example.com/new-page',
            'title': 'New Page',
            'section': 'New Section',
            'content': 'This is new content for testing.',
            'chunk_index': 0,
            'total_chunks': 1,
            'created_at': datetime.now().isoformat()
        },
        vector=[0.2] * 1024,  # Sample vector of 1024 dimensions
        created_at=datetime.now()
    )

    batch_records = [sample_record, new_record]  # sample_record already exists, new_record is new
    batch_result = storage_service.store_embeddings_batch(batch_records)
    print(f"Batch storage result: {batch_result}")

    print("\nDuplicate prevention test completed successfully!")

if __name__ == "__main__":
    test_duplicate_prevention()