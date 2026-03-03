import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional

# Lazy loading for the model to avoid memory issues at startup
_model = None

def get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

class RAGPipeline:
    def __init__(self):
        """Initialize the RAG pipeline with embeddings model."""
        self.chunk_size = 500  # settings.CHUNK_SIZE
        self.chunk_overlap = 50  # settings.CHUNK_OVERLAP
        self.top_k = 3  # settings.TOP_K
        self.similarity_threshold = 0.5  # settings.SIMILARITY_THRESHOLD
        self.dimension = 384  # all-MiniLM-L6-v2 output dimension
        
    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into overlapping chunks with metadata."""
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'start': start,
                'end': end
            })
            
            start = end - self.chunk_overlap
            chunk_id += 1
            
        return chunks
    
    def embed_chunks(self, chunks: List[Dict]) -> np.ndarray:
        """Generate embeddings for all chunks."""
        model = get_model()
        texts = [chunk['text'] for chunk in chunks]
        embeddings = model.encode(texts, show_progress_bar=False)
        return np.array(embeddings).astype('float32')
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a query."""
        model = get_model()
        embedding = model.encode([query], show_progress_bar=False)
        return np.array(embedding).astype('float32')
    
    def create_faiss_index(self, embeddings: np.ndarray):
        """Create FAISS index from embeddings."""
        import faiss
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(self.dimension)
        index.add(embeddings)
        return index
    
    def retrieve(self, query: str, chunks: List[Dict], index, 
                 top_k: Optional[int] = None) -> List[Dict]:
        """Retrieve top-k relevant chunks for a query."""
        if top_k is None:
            top_k = self.top_k
            
        query_embedding = self.embed_query(query)
        import faiss
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = index.search(query_embedding, min(top_k, len(chunks)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= self.similarity_threshold:
                results.append({
                    'chunk': chunks[idx],
                    'score': float(score)
                })
        
        return results
    
    def generate_answer(self, question: str, retrieved_chunks: List[Dict]) -> Tuple[str, List[Dict], float]:
        """Generate answer from retrieved chunks."""
        if not retrieved_chunks:
            return "Not found in references.", [], 0.0
            
        # Calculate average confidence score
        avg_score = np.mean([r['score'] for r in retrieved_chunks])
        
        # Build context from retrieved chunks
        context_parts = []
        citations = []
        
        for result in retrieved_chunks:
            chunk = result['chunk']
            context_parts.append(chunk['text'])
            
            # Create citation
            citation = {
                'document': 'Reference Document',
                'chunk_id': chunk['chunk_id'],
                'position': f"chars {chunk['start']}-{chunk['end']}"
            }
            citations.append(citation)
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using retrieved context
        answer = self._generate_from_context(question, context, citations)
        
        # Extract evidence snippets
        evidence_snippets = []
        for result in retrieved_chunks[:2]:  # Top 2 chunks
            snippet = result['chunk']['text'][:200] + "..." if len(result['chunk']['text']) > 200 else result['chunk']['text']
            evidence_snippets.append(snippet)
        
        return answer, citations, avg_score
    
    def _generate_from_context(self, question: str, context: str, citations: List[Dict]) -> str:
        """Generate answer from context (template-based for local deployment)."""
        # Simple template-based generation
        # In production, replace with actual LLM call
        
        # Extract key sentences that might answer the question
        sentences = context.split('. ')
        relevant_sentences = []
        
        # Simple keyword matching
        question_words = set(question.lower().split())
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence has any overlap with question
            if any(word in sentence_lower for word in question_words if len(word) > 3):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            # Combine relevant sentences
            answer = '. '.join(relevant_sentences[:3])
            if not answer.endswith('.'):
                answer += '.'
            return answer
        else:
            # Return first part of context as answer
            answer = context[:300]
            if len(context) > 300:
                answer += "..."
            return answer

# Create pipeline instance lazily
_rag_pipeline = None

def get_rag_pipeline():
    """Get or create RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline

def process_reference_document(content: str, filename: str) -> Tuple[str, List[Dict], np.ndarray]:
    """Process a reference document: chunk, embed, create index."""
    rag = get_rag_pipeline()
    
    # Chunk the text
    chunks = rag.chunk_text(content)
    
    # Embed chunks
    embeddings = rag.embed_chunks(chunks)
    
    # Store chunks as JSON
    chunks_json = json.dumps(chunks)
    
    return chunks_json, chunks, embeddings

def answer_question(question: str, chunks: List[Dict], embeddings: np.ndarray, 
                    filename: str = "Reference") -> Dict:
    """Answer a single question using RAG."""
    rag = get_rag_pipeline()
    
    # Create FAISS index
    index = rag.create_faiss_index(embeddings)
    
    # Retrieve relevant chunks
    retrieved = rag.retrieve(question, chunks, index)
    
    if not retrieved:
        return {
            'answer': 'Not found in references.',
            'citations': [],
            'evidence_snippets': [],
            'confidence_score': 0.0,
            'is_not_found': True
        }
    
    # Generate answer
    answer_text, citations, confidence = rag.generate_answer(question, retrieved)
    
    # Update citations with filename
    for citation in citations:
        citation['document'] = filename
    
    # Extract evidence snippets
    evidence_snippets = [r['chunk']['text'][:150] + "..." if len(r['chunk']['text']) > 150 
                         else r['chunk']['text'] for r in retrieved[:2]]
    
    return {
        'answer': answer_text,
        'citations': citations,
        'evidence_snippets': evidence_snippets,
        'confidence_score': confidence,
        'is_not_found': False
    }
