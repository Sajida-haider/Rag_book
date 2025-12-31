---
id: 1
title: Create Constitution
stage: constitution
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: KARAKORUM TRADERS
command: /sp.constitution
labels: [constitution,spec-driven-development,ai-book,humanoid-robotics]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
/sp.constitution

Project:
AI & Physical Humanoid Robotics — Unified Spec-Driven Book with Embedded RAG Chatbot

Purpose:
Create a production-ready, AI-generated technical book using Spec-Kit Plus and Claude Code, published with Docusaurus on GitHub Pages, and enhanced with an embedded Retrieval-Augmented Generation (RAG) chatbot that answers questions directly from the book's content.

Core Principles:
- Spec-Driven Development: All work must strictly follow written specifications before implementation.
- Single Source of Truth: The book content is the authoritative knowledge base for the chatbot.
- Accuracy & Verifiability: All technical explanations must be correct, current, and reproducible.
- Clarity & Accessibility: Content must be understandable by beginners while remaining technically correct for advanced readers.
- Modularity: Book content, chatbot backend, and deployment pipelines must remain loosely coupled.
- Automation First: Prefer automated generation, testing, and deployment wherever possible.

Primary Deliverables:
1. AI-Generated Book
   - Written using Claude Code guided by Spec-Kit Plus specifications
   - Built with Docusaurus
   - Deployed to GitHub Pages
   - Covers Physical AI, Humanoid Robotics, and supporting software systems
   - Structured as chapters, sections, and diagrams suitable for long-term maintenance

2. Integrated RAG Chatbot
   - Embedded directly into the published book UI
   - Uses OpenAI Agents / ChatKit SDKs
   - Backend implemented with FastAPI
   - Vector storage using Qdrant Cloud (Free Tier)
   - Metadata & state stored in Neon Serverless Postgres
   - Must answer:
     - General questions about the full book
     - Questions restricted only to user-selected text

Key Standards:
- All generated content must originate from:
  - The book itself
  - Explicitly defined sources
- No hallucinated facts or uncited claims
- Clear separation between:
  - Content generation
  - Retrieval logic
  - Chat response generation
- All APIs, SDKs, and services must be referenced with correct usage patterns

Constraints:
- Deployment Target: GitHub Pages
- Backend Hosting: Cloud-compatible (serverless-friendly)
- Database: Neon Serverless Postgres
- Vector DB: Qdrant Cloud Free Tier
- Language: English
- Code Quality: Clean, readable, production-ready
- No hard-coded secrets or API keys in repository

Non-Functional Requirements:
- Performance: Chat responses should be fast and context-aware
- Security: User input must be sanitized
- Scalability: Architecture must support future content expansion
- Maintainability: Specs must allow future contributors to extend the project
- Observability: Clear logging for chatbot requests and failures

Success Criteria:
- Book successfully builds and deploys on GitHub Pages
- Chatbot correctly answers questions using only book content
- Selected-text question answering works accurately
- Specs fully drive implementation with minimal manual intervention
- Project is hackathon-ready, demo-friendly, and reproducible

Governance Rules:
- No implementatio
```

## Response snapshot

Created the project constitution for the AI & Physical Humanoid Robotics book project. The constitution includes six core principles: Spec-Driven Development (NON-NEGOTIABLE), Single Source of Truth, Accuracy & Verifiability, Clarity & Accessibility, Modularity & Loose Coupling, and Automation First. It also defines constraints and standards, development workflow practices, and governance rules. The constitution establishes version 1.0.0 and is ratified on 2025-12-16.

## Outcome

- ✅ Impact: Created foundational project constitution that establishes guiding principles and constraints
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with project-specific constitution
- 🔁 Next prompts: Proceed with creating specifications for the book and chatbot components
- 🧠 Reflection: The constitution captures all the essential principles from the project description and provides a solid foundation for future development decisions

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin creating the feature specifications based on the constitution