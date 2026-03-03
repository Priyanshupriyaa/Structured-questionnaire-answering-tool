# Structured Questionnaire Answering Tool - Specification

## Project Overview

**Project Name:** Structured Questionnaire Answering Tool  
**Company:** SecureSync (B2B SaaS - Security & Compliance)  
**Purpose:** Automates answering structured questionnaires using internal reference documents with RAG-based AI

---

## System Architecture

### Tech Stack
- **Backend:** Python + FastAPI
- **Database:** SQLite (for local dev simplicity)
- **AI/ML:** LangChain + sentence-transformers + FAISS
- **Frontend:** React with Vite
- **Authentication:** JWT

### Components
1. **Auth Service** - JWT-based user authentication
2. **Document Service** - PDF/Excel/TXT parsing
3. **RAG Pipeline** - Embedding + FAISS retrieval + answer generation
4. **Review Service** - Answer editing
5. ** and managementExport Service** - PDF/DOCX export preserving structure

---

## Database Schema

### Users Table
```
sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Questionnaires Table
```
sql
CREATE TABLE questionnaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL, -- 'pdf', 'excel'
    content TEXT, -- parsed questions in JSON
    status TEXT DEFAULT 'pending', -- pending, generated, reviewed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Reference Documents Table
```
sql
CREATE TABLE reference_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    questionnaire_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    content TEXT, -- parsed text content
    chunks TEXT, -- JSON array of text chunks with embeddings metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id)
);
```

### Answers Table
```
sql
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questionnaire_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    citations TEXT, -- JSON array of citations
    evidence_snippets TEXT, -- JSON array of evidence excerpts
    confidence_score REAL,
    status TEXT DEFAULT 'pending', -- pending, generated, edited
    is_not_found BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id)
);
```

---

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `GET /api/auth/me` - Get current user

### Questionnaires
- `POST /api/questionnaires` - Upload questionnaire
- `GET /api/questionnaires` - List user's questionnaires
- `GET /api/questionnaires/{id}` - Get questionnaire details
- `DELETE /api/questionnaires/{id}` - Delete questionnaire

### Reference Documents
- `POST /api/questionnaires/{id}/references` - Upload reference docs
- `GET /api/questionnaires/{id}/references` - List reference docs
- `DELETE /api/references/{id}` - Delete reference doc

### Answers
- `POST /api/questionnaires/{id}/generate` - Generate answers using RAG
- `GET /api/questionnaires/{id}/answers` - Get all answers
- `PUT /api/answers/{id}` - Update answer (manual edit)
- `POST /api/answers/regenerate` - Regenerate selected answers

### Export
- `GET /api/questionnaires/{id}/export` - Export to PDF/DOCX

---

## RAG Pipeline Design

### 1. Document Processing
- **PDF:** Use pdfplumber to extract text page by page
- **Excel:** Use pandas to read all sheets, convert to text
- **TXT:** Direct text extraction

### 2. Chunking Strategy
- Chunk size: 500 characters
- Overlap: 50 characters
- Preserve context within chunks

### 3. Embedding
- Model: sentence-transformers (all-MiniLM-L6-v2)
- Embed each chunk and store in FAISS index

### 4. Retrieval
- For each question:
  - Embed question using same model
  - Search FAISS for top-k=3 similar chunks
  - Similarity threshold: 0.5
  - Below threshold → "Not found in references."

### 5. Answer Generation
- Strictly use retrieved context
- Include citations: document name + chunk reference
- If not found → return "Not found in references."

---

## Frontend UI Design

### Pages
1. **Login/Signup** - Simple form
2. **Dashboard** - List of questionnaires with status
3. **Upload** - Drag-drop for questionnaire + reference docs
4. **Review** - Table view with columns:
   - Question | Answer | Citations | Confidence | Actions
5. **Export** - Download button

### Features
- Manual answer editing
- Confidence score display
- Evidence snippets expand
- Coverage summary (total/answered/not found)

---

## Acceptance Criteria

1. ✅ User can signup and login
2. ✅ User can upload PDF/Excel questionnaire
3. ✅ User can upload PDF/TXT reference documents
4. ✅ System parses questions from questionnaire
5. ✅ System generates answers using RAG
6. ✅ Every answer has at least one citation
7. ✅ "Not found" returned when no relevant context
8. ✅ User can edit answers manually
9. ✅ Export preserves structure (Q&A format)
10. ✅ At least 2 nice-to-have features implemented:
    - Evidence Snippets
    - Confidence Score
    - Coverage Summary

---

## Sample Files to Create

1. `sample_questionnaire.pdf` - Sample security questionnaire
2. `sample_reference.txt` - Security policy document
3. `sample_reference2.pdf` - Compliance guide

---

## Trade-offs & Assumptions

- Using SQLite for simplicity (PostgreSQL for production)
- Local embeddings (no cloud API needed)
- Single-user reference document association
- Basic error handling (can be enhanced)
- Simple React UI (Material UI or custom CSS)
