---
description: "Task list for Live Deployed Book RAG Backend implementation"
---

# Tasks: Live Deployed Book RAG Backend (Cohere + Qdrant)

**Input**: Design documents from `/specs/001-rag-backend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `ragbot_backend/` at repository root
- **Single file**: `ragbot_backend/main.py` as the only file
- Paths shown below assume single project with single file - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create ragbot_backend folder structure
- [x] T002 [P] Install Python dependencies (requests, beautifulsoup4, cohere, qdrant-client, fastapi, uvicorn) using uv
- [x] T003 Create main.py as the single entry point file in ragbot_backend/main.py
- [x] T004 [P] Create .env.example file with required environment variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Setup FastAPI application in ragbot_backend/main.py
- [x] T006 [P] Configure environment variable loading using python-dotenv in ragbot_backend/main.py
- [x] T007 [P] Configure Cohere client with API key from environment in ragbot_backend/main.py
- [x] T008 [P] Configure Qdrant client with URL and API key from environment in ragbot_backend/main.py
- [x] T009 Create utility functions for logging and error handling in ragbot_backend/main.py
- [x] T010 Test Qdrant connection and create "rag_embedding" collection if it doesn't exist in ragbot_backend/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Content Ingestion from Live Book (Priority: P1) 🎯 MVP

**Goal**: Automatically discover and ingest all accessible pages from the deployed Docusaurus book so that content can be used for question answering

**Independent Test**: Can be fully tested by running the ingestion process and verifying that all book pages are successfully crawled, cleaned, and stored in the vector database

### Implementation for User Story 1

- [x] T011 Implement function to discover all accessible URLs from the deployed book site (sitemap and crawling) in ragbot_backend/main.py
- [x] T012 Implement function to fetch HTML content from each discovered URL in ragbot_backend/main.py
- [x] T013 [P] Implement HTML cleaning and text extraction logic to remove navigation, headers, footers in ragbot_backend/main.py
- [x] T014 [P] Implement text chunking logic with appropriate size and overlap in ragbot_backend/main.py
- [x] T015 Implement function to generate Cohere embeddings for each text chunk in ragbot_backend/main.py
- [x] T016 Implement function to store embeddings in Qdrant with metadata (URL, chunk index, title) in ragbot_backend/main.py
- [x] T017 Create single ingestion execution function that runs the full pipeline in ragbot_backend/main.py
- [x] T018 Implement POST /ingest endpoint to trigger content ingestion in ragbot_backend/main.py
- [x] T019 Add error handling for external service unavailability (Cohere, Qdrant, book site) in ragbot_backend/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Question Answering Service (Priority: P2)

**Goal**: Allow users to ask questions about the book content and receive accurate answers based on the ingested information

**Independent Test**: Can be fully tested by querying the system with sample questions and verifying that relevant answers are returned based on the ingested content

### Implementation for User Story 2

- [x] T020 Implement semantic similarity search using vector embeddings to find relevant content in ragbot_backend/main.py
- [x] T021 Implement function to retrieve relevant text chunks based on query embedding in ragbot_backend/main.py
- [x] T022 [P] Implement function to generate contextual answers based on retrieved passages in ragbot_backend/main.py
- [x] T023 Create POST /query endpoint that accepts user queries and returns relevant responses in ragbot_backend/main.py
- [x] T024 Add confidence scoring to query responses in ragbot_backend/main.py
- [x] T025 Include source references in query responses in ragbot_backend/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Vector Database Management (Priority: P3)

**Goal**: Properly manage the Qdrant vector database with Cohere embeddings so that content is efficiently stored and retrieved

**Independent Test**: Can be fully tested by verifying that embeddings are properly generated, stored in Qdrant, and can be retrieved for similarity search

### Implementation for User Story 3

- [x] T026 Implement health check endpoint to verify Cohere, Qdrant, and book source connections in ragbot_backend/main.py
- [x] T027 Create GET /health endpoint that returns service status in ragbot_backend/main.py
- [x] T028 Implement statistics endpoint to get indexed content metrics in ragbot_backend/main.py
- [x] T029 Create GET /stats endpoint with total documents, chunks, tokens, and last ingestion time in ragbot_backend/main.py
- [ ] T030 Add proper metadata handling for Qdrant payloads with content, source_url, title, chunk_index in ragbot_backend/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 [P] Add comprehensive error handling and validation across all endpoints in ragbot_backend/main.py
- [x] T032 Add beginner-friendly comments and documentation in ragbot_backend/main.py
- [x] T033 [P] Implement rate limiting and request validation in ragbot_backend/main.py
- [x] T034 Add performance logging and monitoring in ragbot_backend/main.py
- [x] T035 Run quickstart.md validation to ensure all functionality works as expected

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on User Story 1 (needs ingested content)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Can work in parallel with other stories

### Within Each User Story

- Core implementation before endpoints
- Story complete before moving to next priority
- Note: User Story 2 depends on User Story 1 completion (needs ingested content)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- User Story 3 can run in parallel with User Story 2 (after foundational phase)
- Different components within stories marked [P] can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all components for User Story 2 together:
Task: "Implement semantic similarity search using vector embeddings to find relevant content in ragbot_backend/main.py"
Task: "Implement function to retrieve relevant text chunks based on query embedding in ragbot_backend/main.py"
Task: "Implement function to generate contextual answers based on retrieved passages in ragbot_backend/main.py"
Task: "Create POST /query endpoint that accepts user queries and returns relevant responses in ragbot_backend/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2 (after US1 completion)
   - Developer C: User Story 3 (can work in parallel with US2)

---

## Notes

- [P] tasks = different files, no dependencies or can be done in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Note: User Story 2 requires User Story 1 to be complete (needs ingested content)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence