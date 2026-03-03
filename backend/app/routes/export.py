import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import User, Questionnaire, Answer
from backend.app.auth import get_current_user
from backend.app.export_utils import export_to_docx, generate_coverage_summary

router = APIRouter(prefix="/api/questionnaires", tags=["Export"])

@router.get("/{questionnaire_id}/export")
def export_questionnaire(
    questionnaire_id: int,
    format: str = "docx",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export questionnaire with answers to PDF or DOCX format."""
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
    
    # Get answers
    answers = db.query(Answer).filter(Answer.questionnaire_id == questionnaire_id).all()
    
    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers to export. Please generate answers first."
        )
    
    # Determine format
    if format not in ['pdf', 'docx']:
        format = 'docx'  # Default to docx
    
    # Create output filename
    output_filename = f"{os.path.splitext(questionnaire.filename)[0]}_answered.{format}"
    output_dir = "./exports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        # Export to DOCX
        export_to_docx(questionnaire, answers, output_path)
        
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export: {str(e)}"
        )

@router.get("/{questionnaire_id}/coverage")
def get_coverage_summary(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get coverage summary for a questionnaire."""
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
    
    # Get answers
    answers = db.query(Answer).filter(Answer.questionnaire_id == questionnaire_id).all()
    
    return generate_coverage_summary(answers)
