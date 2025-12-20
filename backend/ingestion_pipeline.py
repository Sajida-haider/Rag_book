import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGIngestionPipeline:
    def __init__(self):
        # Configure Cohere client
        cohere_api_key = os.getenv("COHERE_API_KEY")
        if not cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")
        self.cohere_client = cohere.Client(cohere_api_key)

        # Configure Qdrant client
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if qdrant_api_key:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.qdrant_client = QdrantClient(url=qdrant_url)

        self.collection_name = "rag_embeddings"

    def get_urls(self):
        """
        Fetch all URLs from the deployed book
        """
        base_url = os.getenv("BOOK_URL", "https://vercel.com/sajida-haiders-projects/my-book-nowf")
        logger.info(f"Fetching URLs from: {base_url}")

        try:
            response = requests.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links in the book
            links = soup.find_all('a', href=True)
            urls = set()

            for link in links:
                href = link['href']
                full_url = urljoin(base_url, href)

                # Only include URLs from the same domain and avoid external links
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url.startswith(base_url):
                        urls.add(full_url)

            # Add the base URL as well
            urls.add(base_url)

            logger.info(f"Found {len(urls)} URLs")
            return list(urls)

        except Exception as e:
            logger.error(f"Error fetching URLs: {e}")
            return [base_url]  # Return base URL as fallback

    def extract_text_from_url(self, url):
        """
        Extract and clean text from a given URL
        """
        logger.info(f"Extracting text from: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            logger.info(f"Extracted {len(text)} characters from {url}")
            return text

        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return ""

    def chunk_text(self, text, chunk_size=1000, overlap=100):
        """
        Chunk text into logical sections suitable for RAG
        """
        logger.info(f"Chunking text of {len(text)} characters")

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # If we're near the end, include the rest
            if end > len(text):
                end = len(text)

            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position with overlap
            start = end - overlap if end < len(text) else end

        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def embed(self, chunks):
        """
        Generate embeddings for each chunk using Cohere
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        try:
            response = self.cohere_client.embed(
                texts=chunks,
                model="embed-english-v3.0",
                input_type="search_document"
            )

            embeddings = response.embeddings
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []

    def create_collection(self, name):
        """
        Create Qdrant collection for storing embeddings
        """
        logger.info(f"Creating Qdrant collection: {name}")

        try:
            # Check if collection already exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if name in collection_names:
                logger.info(f"Collection {name} already exists, recreating...")
                self.qdrant_client.delete_collection(name)

            # Create new collection
            self.qdrant_client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=1024,  # Cohere embed-english-v3.0 returns 1024-dimensional vectors
                    distance=models.Distance.COSINE
                )
            )

            logger.info(f"Collection {name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return False

    def upsert_to_qdrant(self, chunks, embeddings, urls):
        """
        Upsert embeddings and metadata to Qdrant
        """
        logger.info(f"Upserting {len(chunks)} vectors to Qdrant")

        try:
            points = []
            for i, (chunk, embedding, url) in enumerate(zip(chunks, embeddings, urls)):
                point = models.PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "url": url,
                        "chunk_id": i,
                        "module": "book_module",  # This would be extracted from URL structure in a real implementation
                        "chapter": "book_chapter"  # This would be extracted from URL structure in a real implementation
                    }
                )
                points.append(point)

            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Successfully upserted {len(points)} points to Qdrant")
            return True

        except Exception as e:
            logger.error(f"Error upserting to Qdrant: {e}")
            return False

    def run_pipeline(self):
        """
        Run the complete ingestion pipeline
        """
        logger.info("Starting RAG ingestion pipeline")

        # Step 1: Get URLs
        urls = self.get_urls()
        if not urls:
            logger.error("No URLs found, stopping pipeline")
            return False

        # Step 2: Create collection
        if not self.create_collection(self.collection_name):
            logger.error("Failed to create Qdrant collection, stopping pipeline")
            return False

        # Process each URL
        all_chunks = []
        all_embeddings = []
        all_urls = []

        for url in urls:
            logger.info(f"Processing URL: {url}")

            # Extract text
            text = self.extract_text_from_url(url)
            if not text.strip():
                logger.warning(f"No text extracted from {url}, skipping")
                continue

            # Chunk text
            chunks = self.chunk_text(text)

            # Generate embeddings for chunks
            if chunks:
                embeddings = self.embed(chunks)

                if len(embeddings) == len(chunks):
                    # Add to overall lists
                    all_chunks.extend(chunks)
                    all_embeddings.extend(embeddings)
                    all_urls.extend([url] * len(chunks))
                else:
                    logger.warning(f"Embedding count mismatch for {url}: {len(chunks)} chunks vs {len(embeddings)} embeddings")

        # Step 3: Upsert all data to Qdrant
        if all_chunks and all_embeddings and len(all_chunks) == len(all_embeddings):
            success = self.upsert_to_qdrant(all_chunks, all_embeddings, all_urls)
            if success:
                logger.info("RAG ingestion pipeline completed successfully!")
                return True
            else:
                logger.error("Failed to upsert data to Qdrant")
                return False
        else:
            logger.error("No data to upsert to Qdrant")
            return False

def main():
    """
    Main function to run the ingestion pipeline
    """
    logger.info("Initializing RAG Ingestion Pipeline")

    try:
        pipeline = RAGIngestionPipeline()
        success = pipeline.run_pipeline()

        if success:
            logger.info("Pipeline completed successfully!")
        else:
            logger.error("Pipeline failed!")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        raise

if __name__ == "__main__":
    main()