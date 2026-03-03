import pdfplumber
import pandas as pd
import json
import re
from typing import List, Tuple
from pathlib import Path

def parse_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def parse_excel(file_path: str) -> str:
    """Extract text from Excel file (all sheets)."""
    text = ""
    try:
        excel_file = pd.ExcelFile(file_path)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            for idx, row in df.iterrows():
                row_text = " | ".join([str(val) for val in row if pd.notna(val)])
                if row_text.strip():
                    text += row_text + "\n"
    except Exception as e:
        try:
            df = pd.read_csv(file_path)
            for idx, row in df.iterrows():
                row_text = " | ".join([str(val) for val in row if pd.notna(val)])
                if row_text.strip():
                    text += row_text + "\n"
        except Exception as e2:
            raise ValueError(f"Failed to parse Excel file: {str(e2)}")
    return text

def parse_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return text

def extract_questions_from_text(text: str) -> List[str]:
    """Extract individual questions from questionnaire text."""
    questions = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip header/title lines
        if line.isupper() or len(line) < 10:
            continue
        
        # Pattern 1: "1. What is..." or "1) What is..." - numbered questions
        match = re.match(r'^(\d+)\.?\s+(.+)$', line)
        if match:
            question_text = match.group(2).strip()
            if question_text and len(question_text) > 5:
                questions.append(question_text)
            continue
        
        # Pattern 2: "Q: What is..." or "Q1: What is..."
        match = re.match(r'^Q(\d*)\:?\s+(.+)$', line, re.IGNORECASE)
        if match:
            question_text = match.group(2).strip()
            if question_text and len(question_text) > 5:
                questions.append(question_text)
            continue
        
        # Pattern 3: Line ends with "?" - direct question
        if line.endswith('?') and len(line) > 10:
            cleaned = re.sub(r'^[\d\-\*\•]+\.?\s*', '', line)
            if cleaned and len(cleaned) > 5:
                questions.append(cleaned)
            continue
    
    # Fallback: If no questions found, try to extract any line with question mark
    if not questions:
        for line in lines:
            if '?' in line and len(line) > 15:
                parts = line.split('?')
                for i, part in enumerate(parts[:-1]):
                    q = part.strip()
                    if q and len(q) > 10:
                        words = q.split()
                        if len(words) > 3:
                            q = ' '.join(words[-15:])
                            questions.append(q + '?')
                if questions:
                    break
    
    # Final fallback: look for question words in lines
    if not questions:
        question_starts = ['what', 'how', 'do', 'does', 'can', 'are', 'is', 'will', 'would', 'could', 'should', 'may', 'did']
        for line in lines:
            line_lower = line.lower().strip()
            if any(line_lower.startswith(w) for w in question_starts) and len(line) > 20:
                cleaned = re.sub(r'^[\d\-\*\•]+\.?\s*', '', line)
                if cleaned and len(cleaned) > 10:
                    questions.append(cleaned)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_questions = []
    for q in questions:
        q_lower = q.lower()
        if q_lower not in seen:
            seen.add(q_lower)
            unique_questions.append(q)
    
    return unique_questions

def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = Path(filename).suffix.lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    elif ext == '.txt':
        return 'txt'
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def parse_document(file_path: str, filename: str) -> Tuple[str, str]:
    """Parse document and return content and file type."""
    file_type = get_file_type(filename)
    
    if file_type == 'pdf':
        content = parse_pdf(file_path)
    elif file_type == 'excel':
        content = parse_excel(file_path)
    elif file_type == 'txt':
        content = parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return content, file_type

