import os
import psycopg
from typing import List, Dict, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class NeonPostgresMetadataStore:
    """
    Module to store metadata in Neon Postgres database
    """

    def __init__(self):
        # Set up Neon Postgres connection using environment variables
        database_url = os.getenv("NEON_DATABASE_URL")
        if not database_url:
            raise ValueError("NEON_DATABASE_URL environment variable is required")

        self.database_url = database_url
        self.connection = None

    def connect(self) -> bool:
        """
        Establish connection to Neon Postgres database
        """
        try:
            self.connection = psycopg.connect(self.database_url)
            logger.info("Connected to Neon Postgres database")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Neon Postgres: {e}")
            return False

    def create_tables(self) -> bool:
        """
        Create required tables for metadata storage
        """
        if not self.connection:
            if not self.connect():
                return False

        try:
            with self.connection.cursor() as cursor:
                # Create embeddings_metadata table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings_metadata (
                        id VARCHAR(255) PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        module VARCHAR(255) NOT NULL,
                        chapter VARCHAR(255) NOT NULL,
                        section_title VARCHAR(500),
                        url TEXT,
                        chunk_id INTEGER,
                        chunk_size INTEGER,
                        content_preview TEXT,
                        headings_hierarchy JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Create index for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_module_chapter
                    ON embeddings_metadata (module, chapter);
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_file_path
                    ON embeddings_metadata (file_path);
                """)

                self.connection.commit()
                logger.info("Tables created successfully")
                return True

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.connection.rollback()
            return False

    def store_metadata(self, metadata_list: List[Dict]) -> bool:
        """
        Store metadata records in Neon Postgres
        """
        if not self.connection:
            if not self.connect():
                return False

        try:
            with self.connection.cursor() as cursor:
                for metadata in metadata_list:
                    # Prepare the SQL statement
                    sql = """
                        INSERT INTO embeddings_metadata
                        (id, file_path, module, chapter, section_title, url, chunk_id, chunk_size, content_preview, headings_hierarchy)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            file_path = EXCLUDED.file_path,
                            module = EXCLUDED.module,
                            chapter = EXCLUDED.chapter,
                            section_title = EXCLUDED.section_title,
                            url = EXCLUDED.url,
                            chunk_id = EXCLUDED.chunk_id,
                            chunk_size = EXCLUDED.chunk_size,
                            content_preview = EXCLUDED.content_preview,
                            headings_hierarchy = EXCLUDED.headings_hierarchy,
                            updated_at = CURRENT_TIMESTAMP;
                    """

                    # Execute the SQL with metadata values
                    cursor.execute(sql, (
                        metadata.get('id'),
                        metadata.get('file_path'),
                        metadata.get('module'),
                        metadata.get('chapter'),
                        metadata.get('section_title'),
                        metadata.get('url'),
                        metadata.get('chunk_id'),
                        metadata.get('chunk_size'),
                        metadata.get('content_preview', '')[:500],  # Limit preview size
                        metadata.get('headings_hierarchy')  # This should be JSON serializable
                    ))

                self.connection.commit()
                logger.info(f"Stored {len(metadata_list)} metadata records in Neon Postgres")
                return True

        except Exception as e:
            logger.error(f"Error storing metadata: {e}")
            self.connection.rollback()
            return False

    def store_single_metadata(self, metadata: Dict) -> bool:
        """
        Store a single metadata record
        """
        return self.store_metadata([metadata])

    def get_metadata_by_id(self, id: str) -> Optional[Dict]:
        """
        Retrieve metadata record by ID
        """
        if not self.connection:
            if not self.connect():
                return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, file_path, module, chapter, section_title, url, chunk_id,
                           chunk_size, content_preview, headings_hierarchy, created_at, updated_at
                    FROM embeddings_metadata
                    WHERE id = %s;
                """, (id,))

                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'file_path': result[1],
                        'module': result[2],
                        'chapter': result[3],
                        'section_title': result[4],
                        'url': result[5],
                        'chunk_id': result[6],
                        'chunk_size': result[7],
                        'content_preview': result[8],
                        'headings_hierarchy': result[9],
                        'created_at': result[10],
                        'updated_at': result[11]
                    }
                return None

        except Exception as e:
            logger.error(f"Error retrieving metadata by ID: {e}")
            return None

    def get_metadata_by_module_chapter(self, module: str, chapter: str) -> List[Dict]:
        """
        Retrieve metadata records by module and chapter
        """
        if not self.connection:
            if not self.connect():
                return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, file_path, module, chapter, section_title, url, chunk_id,
                           chunk_size, content_preview, headings_hierarchy, created_at, updated_at
                    FROM embeddings_metadata
                    WHERE module = %s AND chapter = %s
                    ORDER BY chunk_id;
                """, (module, chapter))

                results = cursor.fetchall()
                metadata_list = []
                for result in results:
                    metadata_list.append({
                        'id': result[0],
                        'file_path': result[1],
                        'module': result[2],
                        'chapter': result[3],
                        'section_title': result[4],
                        'url': result[5],
                        'chunk_id': result[6],
                        'chunk_size': result[7],
                        'content_preview': result[8],
                        'headings_hierarchy': result[9],
                        'created_at': result[10],
                        'updated_at': result[11]
                    })
                return metadata_list

        except Exception as e:
            logger.error(f"Error retrieving metadata by module/chapter: {e}")
            return []

    def get_all_modules(self) -> List[str]:
        """
        Get all unique modules in the database
        """
        if not self.connection:
            if not self.connect():
                return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT module FROM embeddings_metadata ORDER BY module;")
                results = cursor.fetchall()
                return [result[0] for result in results]

        except Exception as e:
            logger.error(f"Error retrieving modules: {e}")
            return []

    def verify_metadata(self, ids: List[str]) -> Dict[str, bool]:
        """
        Verify that specific metadata records exist in Neon Postgres
        """
        if not self.connection:
            if not self.connect():
                return {id: False for id in ids}

        verification_results = {}

        try:
            for id in ids:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM embeddings_metadata WHERE id = %s;", (id,))
                    count = cursor.fetchone()[0]
                    verification_results[id] = count > 0

            success_count = sum(1 for verified in verification_results.values() if verified)
            logger.info(f"Verified {success_count}/{len(ids)} metadata records in Neon Postgres")
            return verification_results

        except Exception as e:
            logger.error(f"Error verifying metadata: {e}")
            return {id: False for id in ids}

    def close_connection(self):
        """
        Close the database connection
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Neon Postgres connection closed")


# Example usage
if __name__ == "__main__":
    try:
        # Initialize the metadata store
        metadata_store = NeonPostgresMetadataStore()

        # Connect and create tables
        if metadata_store.connect():
            metadata_store.create_tables()

            # Example metadata records (these would come from the ingestion process)
            sample_metadata = [
                {
                    'id': 'chunk-1',
                    'file_path': '/book/intro/getting-started.md',
                    'module': 'introduction',
                    'chapter': 'getting-started',
                    'section_title': 'Getting Started',
                    'url': 'https://example.com/book/intro/getting-started',
                    'chunk_id': 0,
                    'chunk_size': 250,
                    'content_preview': 'This is the beginning of the book...',
                    'headings_hierarchy': [{'level': 1, 'text': 'Introduction'}, {'level': 2, 'text': 'Getting Started'}]
                },
                {
                    'id': 'chunk-2',
                    'file_path': '/book/advanced/deep-dive.md',
                    'module': 'advanced',
                    'chapter': 'deep-dive',
                    'section_title': 'Deep Dive',
                    'url': 'https://example.com/book/advanced/deep-dive',
                    'chunk_id': 1,
                    'chunk_size': 320,
                    'content_preview': 'This section covers advanced topics...',
                    'headings_hierarchy': [{'level': 1, 'text': 'Advanced Topics'}, {'level': 2, 'text': 'Deep Dive'}]
                }
            ]

            # Store metadata
            success = metadata_store.store_metadata(sample_metadata)
            print(f"Metadata stored: {success}")

            # Verify stored records
            ids_to_verify = [m['id'] for m in sample_metadata]
            verification = metadata_store.verify_metadata(ids_to_verify)
            print(f"Verification results: {verification}")

            # Close connection
            metadata_store.close_connection()

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Metadata storage requires NEON_DATABASE_URL in environment variables")