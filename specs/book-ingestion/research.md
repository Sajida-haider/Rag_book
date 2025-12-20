# Research: Book Content Ingestion & Embeddings

## Decision: Embedding Provider Choice
**Rationale**: OpenAI embeddings API was chosen because of its proven reliability, high-quality embeddings, and good documentation. It provides consistent performance for semantic search in RAG applications.

## Alternatives Considered:
- Cohere embeddings: Good alternative but OpenAI has more established ecosystem
- Hugging Face models: Self-hosted options but require more infrastructure
- Sentence Transformers: Free but may not be as accurate as OpenAI

## Decision: Content Processing Approach
**Rationale**: Processing markdown files directly from the Docusaurus book structure preserves the original content hierarchy and formatting while allowing for proper cleaning of unnecessary elements.

## Decision: Chunking Strategy
**Rationale**: Using semantic chunking that respects document hierarchy (headings, paragraphs) rather than fixed-size token chunks ensures that retrieved content maintains context and readability.

## Decision: Storage Architecture
**Rationale**: Separating vector storage (Qdrant) from metadata storage (Neon Postgres) follows the principle of using the right tool for the job - Qdrant for vector similarity search, Neon for structured metadata queries.

## Decision: Content Cleaning Strategy
**Rationale**: Preserving headings hierarchy while removing unnecessary formatting ensures that the semantic structure of the content is maintained for better RAG performance.

## Chunk Size Optimization
Research shows that for RAG applications, chunk sizes between 500-1000 tokens work well for balancing context preservation and retrieval precision. For markdown content, this translates to logical sections based on headings and paragraphs.

## Metadata Schema Considerations
The metadata will include:
- File path for source identification
- Module and chapter for content organization
- Headings hierarchy for context
- Content boundaries for proper context reconstruction