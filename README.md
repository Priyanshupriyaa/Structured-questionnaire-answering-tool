# Structured Questionnaire Answering Tool

A powerful end-to-end web application for automating the answering of structured questionnaires (security reviews, vendor assessments, compliance forms) using internal reference documents with AI-powered RAG (Retrieval-Augmented Generation).

## 🎯 Project Overview

**Company:** SecureSync (B2B SaaS - Security & Compliance)  
**Purpose:** Automate questionnaire answering using grounded, verifiable answers from reference documents

---

## ✨ Features

### Core Functionality
- **User Authentication** - Secure signup/login with JWT tokens
- **Document Upload** - Support for PDF, Excel (.xlsx), and TXT files
- **RAG Pipeline** - Local embedding-based retrieval using sentence-transformers
- **Answer Generation** - Grounded answers with mandatory citations
- **Reference Management** - Upload multiple reference documents per questionnaire
- **Manual Editing** - Edit AI-generated answers as needed
- **Export** - Export answers to DOCX format

### Nice-to-Have Features (Implemented)
- ✅ **Evidence Snippets** - Show short text excerpts used to generate each answer
- ✅ **Confidence Score** - Display confidence based on similarity score
- ✅ **Coverage Summary** - Total questions, answered, not found statistics

---

## 🏗️ Architecture

### Tech Stack
| Component | Technology |
|-----------|------------|
| Backend | Python + FastAPI |
| Database | SQLite (local dev) |
| AI/ML | LangChain + sentence-transformers + FAISS |
| Frontend | React + Vite |
| Authentication | JWT |

### System Flow
```
User Login → Upload Questionnaire → Upload References → Generate Answers → Review/Edit → Export
```

---

## 📁 Project Structure

```
Answering_Tool/
├── backend/
│   ├── app/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── auth.py            # JWT authentication
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── document_parser.py # PDF/Excel/TXT parsing
│   │   ├── rag_pipeline.py    # RAG pipeline with embeddings
│   │   └── routes/            # API routes
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React app
│   │   ├── api.js             # API client
│   │   └── pages/             # React pages
│   └── package.json
├── samples/
│   ├── sample_questionnaire.txt
│   └── sample_reference.txt
├── SPEC.md                    # Detailed specification
├── TODO.md                   # Implementation tasks
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Create virtual environment:
```
bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```
bash
pip install -r requirements.txt
```

3. Run the backend server:
```
bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000  
API Documentation: http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```
bash
cd frontend
```

2. Install dependencies:
```
bash
npm install
```

3. Run the frontend:
```
bash
npm run dev
```

The frontend will be available at: http://localhost:3000

---

## 🔧 Usage Guide

### 1. Sign Up / Login
- Access the frontend at http://localhost:3000
- Create a new account or log in with existing credentials

### 2. Upload Questionnaire
- Click "New Questionnaire" 
- Upload a PDF, Excel, or TXT file containing questions
- The system will parse and display extracted questions

### 3. Upload Reference Documents
- In the questionnaire detail view, upload reference documents (PDF, TXT)
- These documents will be used to answer the questions

### 4. Generate Answers
- Click "Generate Answers" to start the RAG pipeline
- The system will:
  - Chunk and embed reference documents
  - For each question, retrieve relevant context
  - Generate answers grounded in the references
  - Include citations for each answer

### 5. Review & Edit
- Review generated answers in the table view
- Edit any answer as needed
- View evidence snippets and confidence scores

### 6. Export
- Export the completed questionnaire with answers to DOCX

---

## 🔍 RAG Constraints

The AI follows strict rules:

- **Use ONLY retrieved reference text** - No hallucinations
- **Mandatory citations** - Every answer must cite sources
- **Not found handling** - Returns "Not found in references." when similarity is below threshold (0.5)

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user

### Questionnaires
- `POST /api/questionnaires` - Upload questionnaire
- `GET /api/questionnaires` - List user's questionnaires
- `GET /api/questionnaires/{id}` - Get questionnaire details
- `DELETE /api/questionnaires/{id}` - Delete questionnaire

### Reference Documents
- `POST /api/questionnaires/{id}/references` - Upload reference doc
- `GET /api/questionnaires/{id}/references` - List reference docs
- `DELETE /api/references/{id}` - Delete reference doc

### Answers
- `POST /api/questionnaires/{id}/generate` - Generate answers
- `GET /api/questionnaires/{id}/answers` - Get all answers
- `PUT /api/answers/{id}` - Update answer

### Export
- `GET /api/questionnaires/{id}/export?format=docx` - Export answers

---

## ⚠️ Assumptions & Trade-offs

### Assumptions
- Single-user reference document association (each questionnaire has its own references)
- SQLite for local development (PostgreSQL recommended for production)
- Local embeddings without cloud API (suitable for air-gapped environments)
- Basic error handling (can be enhanced for production)

### Trade-offs
- **Memory Usage**: sentence-transformers model requires ~500MB RAM
- **Processing Time**: Initial embedding takes time for large documents
- **Offline Mode**: Works completely offline (no internet required)
- **Simple UI**: Focus on functionality over UI polish

---

## 🔮 Improvements with More Time

1. **Enhanced RAG Pipeline**
   - Add re-ranking for better context selection
   - Implement hybrid search (keyword + semantic)
   - Add support for larger context windows

2. **Production Readiness**
   - Switch to PostgreSQL for production database
   - Add rate limiting and request validation
   - Implement caching for embeddings
   - Add background job queue for long-running tasks

3. **Advanced Features**
   - Support for more file types (DOCX, CSV)
   - Collaborative editing
   - Version history for answers
   - Integration with external systems (Slack, Teams)

4. **UI/UX Improvements**
   - Add dark mode
   - Real-time progress for answer generation
   - Drag-and-drop file upload
   - Enhanced data visualization

---



## 📝 Sample Files

The `samples/` directory contains:
- `sample_questionnaire.txt` - Sample security questionnaire (10 questions)
- `sample_reference.txt` - Security policy reference document
- `compliance_certifications.txt` - Compliance certifications and standards
- `incident_response_procedures.txt` - Incident response procedures
- `data_protection_policy.txt` - Data protection and privacy policy
- `backup_disaster_recovery.txt` - Backup and disaster recovery procedures

Use these to test the full workflow!

---

