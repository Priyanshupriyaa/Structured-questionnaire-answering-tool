from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    questionnaires = relationship("Questionnaire", back_populates="user")
    
class Questionnaire(Base):
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # 'pdf', 'excel'
    content = Column(Text, nullable=True)  # JSON string of parsed questions
    status = Column(String(20), default="pending")  # pending, generated, reviewed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="questionnaires")
    reference_documents = relationship("ReferenceDocument", back_populates="questionnaire")
    answers = relationship("Answer", back_populates="questionnaire")

class ReferenceDocument(Base):
    __tablename__ = "reference_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # 'pdf', 'txt', 'excel'
    content = Column(Text, nullable=True)  # Parsed text content
    chunks = Column(Text, nullable=True)  # JSON array of text chunks
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    questionnaire = relationship("Questionnaire", back_populates="reference_documents")

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    citations = Column(Text, nullable=True)  # JSON array of citations
    evidence_snippets = Column(Text, nullable=True)  # JSON array of evidence excerpts
    confidence_score = Column(Float, nullable=True)
    status = Column(String(20), default="pending")  # pending, generated, edited
    is_not_found = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    questionnaire = relationship("Questionnaire", back_populates="answers")
