import os
import json
import shutil
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models import User, Questionnaire, ReferenceDocument, Answer
from backend.app.schemas import ReferenceDocumentResponse
from backend.app.auth import get_current_user
from backend.app.config import settings
from backend.app.document_parser import parse_document
from backend.app.rag_pipeline import process_reference_document, answer_question, get_rag_pipeline

router = APIRouter(prefix="/api", tags=["Reference Documents"])

@router.post("/questionnaires/{questionnaire_id}/references", response_model=ReferenceDocumentResponse)
async def upload_reference_document(
    questionnaire_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a reference document for a questionnaire."""
    # Verify questionnaire belongs to user
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    # Validate file type
    allowed_types = ['.pdf', '.txt', '.xlsx', '.xls']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Save uploaded file
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id), str(questionnaire_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    file_path = os.path.join(user_upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Parse document
        content, file_type = parse_document(file_path, file.filename)
        
        # Process for RAG: chunk and embed
        chunks_json, chunks, embeddings = process_reference_document(content, file.filename)
        
        # Create database record
        reference_doc = ReferenceDocument(
            user_id=current_user.id,
            questionnaire_id=questionnaire_id,
            filename=file.filename,
            file_type=file_type,
            content=content,
            chunks=chunks_json
        )
        
        db.add(reference_doc)
        db.commit()
        db.refresh(reference_doc)
        
        # Save embeddings to file (for persistence)
        embeddings_path = os.path.join(user_upload_dir, f"{reference_doc.id}_embeddings.npy")
        np.save(embeddings_path, embeddings)
        
        return reference_doc
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process reference document: {str(e)}"
        )

@router.get("/questionnaires/{questionnaire_id}/references", response_model=List[ReferenceDocumentResponse])
def list_reference_documents(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all reference documents for a questionnaire."""
    # Verify questionnaire belongs to user
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    reference_docs = db.query(ReferenceDocument).filter(
        ReferenceDocument.questionnaire_id == questionnaire_id
    ).all()
    
    return reference_docs

@router.delete("/references/{reference_id}")
def delete_reference_document(
    reference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a reference document."""
    reference_doc = db.query(ReferenceDocument).filter(
        ReferenceDocument.id == reference_id,
        ReferenceDocument.user_id == current_user.id
    ).first()
    
    if not reference_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference document not found"
        )
    
    # Delete embeddings file if exists
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id), str(reference_doc.questionnaire_id))
    embeddings_path = os.path.join(user_upload_dir, f"{reference_id}_embeddings.npy")
    if os.path.exists(embeddings_path):
        os.remove(embeddings_path)
    
    db.delete(reference_doc)
    db.commit()
    
    return {"message": "Reference document deleted successfully"}

@router.post("/questionnaires/{questionnaire_id}/generate")
def generate_answers(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate answers for all questions using RAG."""
    # Verify questionnaire belongs to user
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    # Get reference documents
    reference_docs = db.query(ReferenceDocument).filter(
        ReferenceDocument.questionnaire_id == questionnaire_id
    ).all()
    
    if not reference_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No reference documents uploaded. Please upload reference documents first."
        )
    
    # Get questions
    if not questionnaire.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions found in questionnaire."
        )
    
    questions = json.loads(questionnaire.content)
    
    # Load embeddings and chunks from all reference documents
    all_chunks = []
    all_embeddings = []
    doc_info = {}
    
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id), str(questionnaire_id))
    
    for ref_doc in reference_docs:
        # Load chunks
        chunks = json.loads(ref_doc.chunks)
        
        # Load embeddings
        embeddings_path = os.path.join(user_upload_dir, f"{ref_doc.id}_embeddings.npy")
        if os.path.exists(embeddings_path):
            embeddings = np.load(embeddings_path)
        else:
            # Re-process if embeddings not found
            _, chunks, embeddings = process_reference_document(ref_doc.content, ref_doc.filename)
        
        # Add document info to chunks
        for chunk in chunks:
            chunk['document_name'] = ref_doc.filename
            chunk['document_id'] = ref_doc.id
        
        all_chunks.extend(chunks)
        all_embeddings.append(embeddings)
        
        doc_info[ref_doc.id] = ref_doc.filename
    
    # Combine all embeddings
    if all_embeddings:
        combined_embeddings = np.vstack(all_embeddings)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process reference documents."
        )
    
    # Delete existing answers
    db.query(Answer).filter(Answer.questionnaire_id == questionnaire_id).delete()
    
    # Generate answers for each question
    answers = []
    for question in questions:
        # Use RAG to answer
        result = answer_question(question, all_chunks, combined_embeddings)
        
        # Create answer record
        answer = Answer(
            questionnaire_id=questionnaire_id,
            question=question,
            answer=result['answer'],
            citations=json.dumps(result['citations']),
            evidence_snippets=json.dumps(result['evidence_snippets']),
            confidence_score=result['confidence_score'],
            status="generated",
            is_not_found=result['is_not_found']
        )
        
        db.add(answer)
        answers.append(answer)
    
    # Update questionnaire status
    questionnaire.status = "generated"
    
    db.commit()
    
    # Refresh answers
    for answer in answers:
        db.refresh(answer)
    
    return {
        "message": "Answers generated successfully",
        "answers": answers,
        "total": len(answers)
    }

@router.get("/questionnaires/{questionnaire_id}/answers")
def get_answers(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all answers for a questionnaire."""
    # Verify questionnaire belongs to user
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    answers = db.query(Answer).filter(Answer.questionnaire_id == questionnaire_id).all()
    
    # Generate coverage summary
    total = len(answers)
    answered = sum(1 for a in answers if a.answer and not a.is_not_found)
    not_found = sum(1 for a in answers if a.is_not_found)
    edited = sum(1 for a in answers if a.status == 'edited')
    
    avg_confidence = 0.0
    answered_with_scores = [a.confidence_score for a in answers if a.confidence_score and a.confidence_score > 0]
    if answered_with_scores:
        avg_confidence = sum(answered_with_scores) / len(answered_with_scores)
    
    return {
        "answers": answers,
        "coverage_summary": {
            "total_questions": total,
            "answered": answered,
            "not_found": not_found,
            "edited": edited,
            "average_confidence": round(avg_confidence, 3)
        }
    }

@router.put("/answers/{answer_id}")
def update_answer(
    answer_id: int,
    answer_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an answer (manual edit)."""
    answer = db.query(Answer).join(Questionnaire).filter(
        Answer.id == answer_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    
    answer.answer = answer_text
    answer.status = "edited"
    
    db.commit()
    db.refresh(answer)
    
    return answer
