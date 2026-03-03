# TODO: Structured Questionnaire Answering Tool

## Phase 1: Backend Setup - ✅ COMPLETED
- [x] 1.1 Create project directory structure
- [x] 1.2 Set up Python virtual environment and dependencies
- [x] 1.3 Create database models (SQLAlchemy)
- [x] 1.4 Implement JWT authentication (signup/login)
- [x] 1.5 Create questionnaire upload API
- [x] 1.6 Implement PDF parsing (pdfplumber)
- [x] 1.7 Implement Excel parsing (pandas)
- [x] 1.8 Create reference document upload API
- [x] 1.9 Implement text chunking and FAISS indexing
- [x] 1.10 Implement RAG pipeline with embeddings

## Phase 2: Answer Generation - ✅ COMPLETED
- [x] 2.1 Create answer generation endpoint
- [x] 2.2 Implement retrieval logic with similarity threshold
- [x] 2.3 Implement answer generation with citations
- [x] 2.4 Handle "Not found in references" case
- [x] 2.5 Add confidence scoring
- [x] 2.6 Add evidence snippets

## Phase 3: Review & Export - ✅ COMPLETED
- [x] 3.1 Implement answer editing API
- [x] 3.2 Create answer retrieval endpoint
- [x] 3.3 Implement DOCX export preserving structure

## Phase 4: Frontend - ✅ COMPLETED
- [x] 4.1 Set up React with Vite
- [x] 4.2 Create login/signup pages
- [x] 4.3 Create dashboard
- [x] 4.4 Create upload page
- [x] 4.5 Create review page with table UI
- [x] 4.6 Implement answer editing in frontend
- [x] 4.7 Add coverage summary

## Phase 5: Sample Files & Documentation - ✅ COMPLETED
- [x] 5.1 Create sample questionnaire (TXT)
- [x] 5.2 Create sample reference documents
- [x] 5.3 Write README.md
- [x] 5.4 Test end-to-end flow

## Bug Fix - ✅ COMPLETED
- [x] Fixed question extraction regex patterns in document_parser.py
  - Pattern 1: `r'^(\d+)\.?\s+(.+)$'` - required optional `.` followed by REQUIRED space
  - Pattern 2: `r'^Q(\d*)\:?\s+(.+)$'` - required optional `:` followed by REQUIRED space
  - Now correctly extracts questions from sample_questionnaire.txt (10 questions found)
