"""Script to delete all vectors from the Qdrant collection 'humanoid_ai_book'"""

import os
import sys
from dotenv import load_dotenv
import logging

# Add the backend directory to the path so we can import our modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.vector_storage import VectorStorageService

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_all_vectors():
    """Delete all vectors from the Qdrant collection"""
    logger.info("Starting deletion of all vectors from collection...")

    try:
        storage_service = VectorStorageService()

        # Get all records from the collection
        logger.info("Retrieving all records from collection...")
        all_records = storage_service.get_all_records()

        logger.info(f"Found {len(all_records)} total records in the collection")

        # Log each record that will be deleted
        for i, record in enumerate(all_records):
            url = record.payload.get('url', 'N/A')
            title = record.payload.get('title', 'N/A')
            section = record.payload.get('section', 'N/A')
            chunk_index = record.payload.get('chunk_index', 'N/A')

            logger.info(f"Deleting record {i+1}/{len(all_records)} - ID: {record.id}")
            logger.info(f"  URL: {url}")
            logger.info(f"  Title: {title}")
            logger.info(f"  Section: {section}")
            logger.info(f"  Chunk index: {chunk_index}")

        # Delete all records by clearing the entire collection
        logger.info("Clearing the entire collection...")

        # Use the Qdrant client to clear the collection
        result = storage_service.client.delete_collection(storage_service.collection_name)
        logger.info("Collection cleared successfully")

        # Recreate the collection
        from qdrant_client.http import models
        storage_service.client.create_collection(
            collection_name=storage_service.collection_name,
            vectors_config=models.VectorParams(
                size=1024,  # Cohere multilingual-v3.0 embeddings are 1024 dimensions
                distance=models.Distance.COSINE
            )
        )
        logger.info("Collection recreated successfully")

        # Print summary
        logger.info("="*50)
        logger.info("DELETION SUMMARY")
        logger.info("="*50)
        logger.info(f"Total vectors deleted: {len(all_records)}")

        # Check remaining vectors
        remaining_records = storage_service.get_all_records()
        logger.info(f"Remaining vectors in collection: {len(remaining_records)}")
        logger.info("="*50)

        logger.info("All vectors have been successfully deleted!")

    except Exception as e:
        logger.error(f"Error during vector deletion: {e}")
        raise

if __name__ == "__main__":
    delete_all_vectors()