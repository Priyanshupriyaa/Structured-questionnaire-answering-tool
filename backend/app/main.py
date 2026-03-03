from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import init_db
from backend.app.routes.auth import router as auth_router
from backend.app.routes.questionnaires import router as questionnaires_router
from backend.app.routes.references import router as references_router
from backend.app.routes.export import router as export_router
from backend.app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Structured Questionnaire Answering Tool using RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(questionnaires_router)
app.include_router(references_router)
app.include_router(export_router)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to SecureSync Questionnaire Answering Tool",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
