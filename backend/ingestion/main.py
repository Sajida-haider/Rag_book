import os
import logging
from typing import List, Dict
from datetime import datetime
import uuid

from .content_reader import ContentReader
from .cleaner import ContentCleaner
from .chunker import ContentChunker
from .embedder import OpenAIEmbedder
from .vector_store import QdrantVectorStore
from .metadata_store import NeonPostgresMetadataStore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BookIngestionPipeline:
    """
    Main pipeline to orchestrate the entire book content ingestion process
    """

    def __init__(self, book_path: str = "book/", chunk_size: int = 1000, overlap: int = 100):
        self.book_path = book_path
        self.chunk_size = chunk_size
        self.overlap = overlap

        # Initialize all components
        self.content_reader = ContentReader(book_path)
        self.cleaner = ContentCleaner()
        self.chunker = ContentChunker(max_chunk_size=chunk_size, overlap=overlap)
        self.embedder = OpenAIEmbedder()
        self.vector_store = QdrantVectorStore()
        self.metadata_store = NeonPostgresMetadataStore()

        # Track processing statistics
        self.stats = {
            "files_processed": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "start_time": None,
            "end_time": None
        }

    def run_ingestion(self) -> bool:
        """
        Run the complete ingestion pipeline
        """
        logger.info("Starting book content ingestion pipeline")
        self.stats["start_time"] = datetime.now()

        try:
            # Step 1: Connect to databases
            logger.info("Connecting to databases...")
            if not self.metadata_store.connect():
                logger.error("Failed to connect to Neon Postgres")
                return False

            # Step 2: Create necessary tables and collections
            logger.info("Creating database tables and Qdrant collection...")
            self.metadata_store.create_tables()
            self.vector_store.create_collection(vector_size=self.embedder.get_embedding_dimensions())

            # Step 3: Get content manifest
            logger.info("Reading book content...")
            manifest = self.content_reader.get_content_manifest()
            logger.info(f"Found {len(manifest)} files to process")

            # Step 4: Process each file
            all_chunks = []
            all_embeddings = []
            all_metadata = []
            all_ids = []

            for i, file_info in enumerate(manifest):
                logger.info(f"Processing file {i+1}/{len(manifest)}: {file_info['relative_path']}")

                # Read file content
                content = self.content_reader.read_file_content(file_info["file_path"])
                if not content.strip():
                    logger.warning(f"Empty content in {file_info['file_path']}, skipping")
                    continue

                # Clean content
                cleaned_content, headings = self.cleaner.process_content(content)

                # Chunk content
                chunks = self.chunker.chunk_content(cleaned_content, headings)
                logger.info(f"Created {len(chunks)} chunks from {file_info['relative_path']}")

                # Process each chunk
                for j, chunk in enumerate(chunks):
                    chunk_id = f"{file_info['relative_path']}_{j}"
                    unique_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))

                    # Generate embedding
                    try:
                        embedding = self.embedder.generate_single_embedding(chunk['content'])
                    except Exception as e:
                        logger.error(f"Failed to generate embedding for chunk {j} in {file_info['relative_path']}: {e}")
                        continue

                    # Prepare metadata
                    chunk_metadata = {
                        "id": unique_id,
                        "file_path": file_info["file_path"],
                        "module": file_info["module"],
                        "chapter": file_info["chapter"],
                        "relative_path": file_info["relative_path"],
                        "chunk_id": j,
                        "chunk_size": chunk['size'],
                        "content_preview": chunk['content'][:200],  # First 200 chars as preview
                        "headings_hierarchy": headings,
                        "created_at": datetime.now().isoformat()
                    }

                    # Add to collections for batch processing
                    all_chunks.append(chunk['content'])
                    all_embeddings.append(embedding)
                    all_metadata.append(chunk_metadata)
                    all_ids.append(unique_id)

                    # Update stats
                    self.stats["total_chunks"] += 1

                self.stats["files_processed"] += 1

            # Step 5: Store all embeddings in Qdrant (batch operation)
            logger.info(f"Storing {len(all_embeddings)} embeddings in Qdrant...")
            if all_embeddings:
                success = self.vector_store.store_embeddings(
                    all_embeddings,
                    all_chunks,
                    all_metadata,
                    all_ids
                )
                if success:
                    self.stats["total_embeddings"] = len(all_embeddings)
                    logger.info("Successfully stored embeddings in Qdrant")
                else:
                    logger.error("Failed to store embeddings in Qdrant")
                    return False

            # Step 6: Store all metadata in Neon Postgres (batch operation)
            logger.info(f"Storing {len(all_metadata)} metadata records in Neon Postgres...")
            if all_metadata:
                success = self.metadata_store.store_metadata(all_metadata)
                if success:
                    logger.info("Successfully stored metadata in Neon Postgres")
                else:
                    logger.error("Failed to store metadata in Neon Postgres")
                    return False

            # Step 7: Verification
            logger.info("Verifying stored data...")
            qdrant_verification = self.vector_store.verify_stored_vectors(all_ids[:10])  # Verify first 10 as sample
            postgres_verification = self.metadata_store.verify_metadata(all_ids[:10])  # Verify first 10 as sample

            logger.info(f"Qdrant verification (sample): {sum(qdrant_verification.values())}/{len(qdrant_verification)}")
            logger.info(f"Postgres verification (sample): {sum(postgres_verification.values())}/{len(postgres_verification)}")

            # Complete stats
            self.stats["end_time"] = datetime.now()
            duration = self.stats["end_time"] - self.stats["start_time"]
            logger.info(f"Ingestion completed in {duration}")
            logger.info(f"Final stats: {self.stats}")

            return True

        except Exception as e:
            logger.error(f"Error during ingestion pipeline: {e}")
            return False

        finally:
            # Close database connection
            self.metadata_store.close_connection()

    def get_pipeline_stats(self) -> Dict:
        """
        Get statistics about the pipeline execution
        """
        return self.stats

    def verify_ingestion(self) -> Dict:
        """
        Verify that the ingestion was successful by checking both storage systems
        """
        logger.info("Running comprehensive verification...")

        try:
            # Get collection info from Qdrant
            qdrant_info = self.vector_store.get_collection_info()
            logger.info(f"Qdrant collection info: {qdrant_info}")

            # Get modules from Postgres
            modules = self.metadata_store.get_all_modules()
            logger.info(f"Found modules in Postgres: {modules}")

            verification_results = {
                "qdrant_vectors_count": qdrant_info.get("vector_count", 0),
                "postgres_modules_count": len(modules),
                "modules_list": modules
            }

            return verification_results

        except Exception as e:
            logger.error(f"Error during verification: {e}")
            return {"error": str(e)}


def main():
    """
    Main function to run the ingestion pipeline from command line
    """
    import argparse

    parser = argparse.ArgumentParser(description="Book Content Ingestion Pipeline")
    parser.add_argument("--book-path", type=str, default="book/", help="Path to book markdown files")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Maximum chunk size in characters")
    parser.add_argument("--overlap", type=int, default=100, help="Overlap between chunks in characters")

    args = parser.parse_args()

    # Create and run the pipeline
    pipeline = BookIngestionPipeline(
        book_path=args.book_path,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )

    success = pipeline.run_ingestion()

    if success:
        logger.info("Ingestion pipeline completed successfully!")

        # Run verification
        verification = pipeline.verify_ingestion()
        logger.info(f"Verification results: {verification}")

        stats = pipeline.get_pipeline_stats()
        logger.info(f"Pipeline stats: {stats}")
    else:
        logger.error("Ingestion pipeline failed!")
        exit(1)


if __name__ == "__main__":
    main()