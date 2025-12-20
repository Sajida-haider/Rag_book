# Data Model: Book Content Ingestion & Embeddings

## Entities

### ContentChunk
**Description**: Represents a chunk of processed book content
- **id** (string, required): Unique identifier for the chunk
- **content** (string, required): The cleaned text content
- **headings_hierarchy** (array of objects, optional): Maintains heading structure
- **start_line** (integer, required): Starting line number in source file
- **end_line** (integer, required): Ending line number in source file
- **chunk_size** (integer, required): Size of the chunk in characters
- **embedding_id** (string, required): Reference to the vector embedding

### EmbeddingVector
**Description**: Represents a vector embedding of content
- **id** (string, required): Unique identifier (same as content chunk id)
- **vector** (array of floats, required): The embedding vector
- **model** (string, required): Name of the embedding model used
- **created_at** (datetime, required): Timestamp of creation

### MetadataRecord
**Description**: Metadata stored in Neon Postgres database
- **id** (string, required): Unique identifier (same as content chunk id)
- **file_path** (string, required): Path to the source markdown file
- **module** (string, required): Module name extracted from directory structure
- **chapter** (string, required): Chapter name extracted from file/heading
- **section_title** (string, optional): Title of the specific section
- **url** (string, optional): URL if the content is from a deployed site
- **created_at** (datetime, required): Timestamp of ingestion
- **updated_at** (datetime, required): Timestamp of last update

### ProcessedFile
**Description**: Represents a processed markdown file
- **id** (string, required): Unique identifier
- **file_path** (string, required): Path to the source markdown file
- **total_chunks** (integer, required): Number of chunks created from this file
- **status** (string, required): Processing status (pending, processing, completed, failed)
- **processed_at** (datetime, optional): Timestamp when processing completed

## Relationships

### ContentChunk → EmbeddingVector
- One-to-one relationship via id field
- ContentChunk.id references EmbeddingVector.id

### ContentChunk → MetadataRecord
- One-to-one relationship via id field
- ContentChunk.id references MetadataRecord.id

### ProcessedFile → ContentChunk
- One-to-many relationship
- ProcessedFile.id referenced by ContentChunk.file_id (derived from file_path)

## Validation Rules
- ContentChunk.content must not be empty
- ContentChunk.chunk_size must be greater than 0
- EmbeddingVector.vector must have the correct dimension for the model
- MetadataRecord.file_path must be a valid markdown file path
- All timestamp fields must be in ISO 8601 format

## State Transitions
- ProcessedFile.status: pending → processing → completed OR failed