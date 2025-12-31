<!-- SYNC IMPACT REPORT
Version change: N/A -> 1.0.0
Modified principles: N/A (new constitution)
Added sections: All sections
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ⚠ pending
- README.md ⚠ pending
Follow-up TODOs: None
-->

# AI & Physical Humanoid Robotics Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
All work must strictly follow written specifications before implementation. No code is written without a corresponding specification that defines the requirements, acceptance criteria, and constraints. Specifications serve as the contract between stakeholders and implementation teams.

### II. Single Source of Truth
The book content serves as the authoritative knowledge base for the chatbot. All information provided by the RAG chatbot must originate directly from the book content, ensuring consistency and accuracy across all user interactions.

### III. Accuracy & Verifiability
All technical explanations must be correct, current, and reproducible. No hallucinated facts or uncited claims are allowed. Every technical assertion must be verifiable through the book content or explicitly defined external sources.

### IV. Clarity & Accessibility
Content must be understandable by beginners while remaining technically correct for advanced readers. Technical concepts should be explained with appropriate examples, analogies, and progressive complexity to serve diverse audiences.

### V. Modularity & Loose Coupling
Book content, chatbot backend, and deployment pipelines must remain loosely coupled. Each component should be independently developable, testable, and maintainable without tight dependencies that create fragility.

### VI. Automation First
Prefer automated generation, testing, and deployment wherever possible. Manual processes should be minimized in favor of repeatable, reliable automated workflows that ensure consistency and reduce human error.

## Constraints & Standards

The following constraints and standards govern all aspects of this project:

- Deployment Target: GitHub Pages
- Backend Hosting: Cloud-compatible (serverless-friendly)
- Database: Neon Serverless Postgres
- Vector DB: Qdrant Cloud Free Tier
- Language: English
- Code Quality: Clean, readable, production-ready
- No hard-coded secrets or API keys in repository
- All generated content must originate from the book itself or explicitly defined sources
- Clear separation between content generation, retrieval logic, and chat response generation
- All APIs, SDKs, and services must be referenced with correct usage patterns

## Development Workflow

The development workflow follows these key practices:

- Content generation using Claude Code guided by Spec-Kit Plus specifications
- Docusaurus-based book building and publishing
- FastAPI for chatbot backend implementation
- OpenAI Agents / ChatKit SDKs for RAG functionality
- Qdrant Cloud for vector storage and retrieval
- Neon Serverless Postgres for metadata and state storage
- All work must pass through specification phase before implementation
- Continuous integration with automated testing and validation

## Governance

This constitution supersedes all other development practices and guidelines. All team members must comply with these principles and constraints. Amendments to this constitution require formal documentation, stakeholder approval, and a migration plan for existing work. All pull requests and reviews must verify constitutional compliance. All work must align with the core mission of creating a production-ready, AI-generated technical book with an integrated RAG chatbot.

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
