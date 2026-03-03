from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Questionnaire Schemas
class QuestionnaireCreate(BaseModel):
    filename: str
    file_type: str
    content: Optional[str] = None

class QuestionnaireResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Reference Document Schemas
class ReferenceDocumentCreate(BaseModel):
    filename: str
    file_type: str
    content: Optional[str] = None
    chunks: Optional[str] = None

class ReferenceDocumentResponse(BaseModel):
    id: int
    questionnaire_id: int
    filename: str
    file_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Answer Schemas
class AnswerCreate(BaseModel):
    question: str

class AnswerUpdate(BaseModel):
    answer: str
    citations: Optional[str] = None
    evidence_snippets: Optional[str] = None

class AnswerResponse(BaseModel):
    id: int
    questionnaire_id: int
    question: str
    answer: Optional[str]
    citations: Optional[str]
    evidence_snippets: Optional[str]
    confidence_score: Optional[float]
    status: str
    is_not_found: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Generation Request
class GenerateRequest(BaseModel):
    questionnaire_id: int
    questions: List[str]

class GenerateResponse(BaseModel):
    answers: List[AnswerResponse]
    coverage_summary: dict

# Export
class ExportRequest(BaseModel):
    format: str  # 'pdf' or 'docx'
