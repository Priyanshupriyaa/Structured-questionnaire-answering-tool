import os
import json
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models import User, Questionnaire, ReferenceDocument
from backend.app.schemas import QuestionnaireResponse, ReferenceDocumentCreate, ReferenceDocumentResponse
from backend.app.auth import get_current_user
from backend.app.config import settings
from backend.app.document_parser import parse_document, extract_questions_from_text

router = APIRouter(prefix="/api/questionnaires", tags=["Questionnaires"])

@router.post("", response_model=QuestionnaireResponse)
async def upload_questionnaire(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a questionnaire file (PDF, Excel, or TXT)."""
    # Validate file type
    allowed_types = ['.pdf', '.xlsx', '.xls', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Save uploaded file
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    file_path = os.path.join(user_upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Parse document
        content, file_type = parse_document(file_path, file.filename)
        
        # Extract questions
        questions = extract_questions_from_text(content)
        questions_json = json.dumps(questions)
        
        # Create database record
        questionnaire = Questionnaire(
            user_id=current_user.id,
            filename=file.filename,
            file_type=file_type,
            content=questions_json,
            status="pending"
        )
        
        db.add(questionnaire)
        db.commit()
        db.refresh(questionnaire)
        
        return questionnaire
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process questionnaire: {str(e)}"
        )

@router.get("", response_model=List[QuestionnaireResponse])
def list_questionnaires(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all questionnaires for current user."""
    questionnaires = db.query(Questionnaire).filter(
        Questionnaire.user_id == current_user.id
    ).order_by(Questionnaire.created_at.desc()).all()
    
    return questionnaires

@router.get("/{questionnaire_id}", response_model=QuestionnaireResponse)
def get_questionnaire(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific questionnaire."""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    return questionnaire

@router.get("/{questionnaire_id}/questions")
def get_questionnaire_questions(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get parsed questions from a questionnaire."""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    if not questionnaire.content:
        return {"questions": []}
    
    questions = json.loads(questionnaire.content)
    return {"questions": questions}

@router.delete("/{questionnaire_id}")
def delete_questionnaire(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a questionnaire and its related data."""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id,
        Questionnaire.user_id == current_user.id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    # Delete related reference documents and answers
    db.query(ReferenceDocument).filter(
        ReferenceDocument.questionnaire_id == questionnaire_id
    ).delete()
    
    db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).delete()
    db.commit()
    
    return {"message": "Questionnaire deleted successfully"}
