import React, { useState, useEffect, useRef } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';

function Upload({ token }) {
  const { questionnaireId } = useParams();
  const [questionnaire, setQuestionnaire] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [references, setReferences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [generating, setGenerating] = useState(false);
  const navigate = useNavigate();
  
  const questionnaireInputRef = useRef(null);
  const referenceInputRef = useRef(null);

  useEffect(() => {
    if (questionnaireId) {
      loadQuestionnaire();
      loadReferences();
    }
  }, [questionnaireId]);

  const loadQuestionnaire = async () => {
    try {
      const data = await api.getQuestionnaire(questionnaireId, token);
      setQuestionnaire(data);
      
      const questionsData = await api.getQuestions(questionnaireId, token);
      setQuestions(questionsData.questions || []);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadReferences = async () => {
    try {
      const data = await api.getReferences(questionnaireId, token);
      setReferences(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleQuestionnaireUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await api.uploadQuestionnaire(file, token);
      setQuestionnaire(data);
      
      // Re-fetch to get the parsed questions
      const questionsData = await api.getQuestions(data.id, token);
      setQuestions(questionsData.questions || []);
      
      // Navigate to references upload page
      navigate(`/upload/${data.id}`);
      setSuccess('Questionnaire uploaded successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReferenceUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !questionnaireId) return;
    
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.uploadReference(questionnaireId, file, token);
      setSuccess('Reference document uploaded successfully!');
      loadReferences();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteReference = async (refId) => {
    if (!confirm('Delete this reference document?')) return;
    
    try {
      await api.deleteReference(refId, token);
      loadReferences();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleGenerate = async () => {
    if (references.length === 0) {
      setError('Please upload at least one reference document');
      return;
    }

    setGenerating(true);
    setError('');
    setSuccess('');

    try {
      await api.generateAnswers(questionnaireId, token);
      setSuccess('Answers generated successfully!');
      navigate(`/review/${questionnaireId}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const triggerQuestionnaireUpload = () => {
    questionnaireInputRef.current?.click();
  };

  const triggerReferenceUpload = () => {
    referenceInputRef.current?.click();
  };

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-brand">SecureSync Questionnaire Tool</div>
        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>
        </div>
      </nav>
      
      <div className="container">
        <h1>{questionnaireId ? 'Upload References' : 'Upload Questionnaire'}</h1>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        {/* Step 1: Upload Questionnaire */}
        {!questionnaireId && (
          <div className="card">
            <h2 className="card-title">Step 1: Upload Questionnaire</h2>
            <p style={{ marginBottom: '1rem', color: '#666' }}>
              Upload a PDF or Excel questionnaire file
            </p>
            
            {/* Hidden file input */}
            <input
              ref={questionnaireInputRef}
              type="file"
              className="file-input"
              accept=".pdf,.xlsx,.xls,.txt"
              onChange={handleQuestionnaireUpload}
              disabled={loading}
            />
            
            {/* Clickable upload area */}
            <div className="upload-area" onClick={triggerQuestionnaireUpload}>
              <div className="upload-icon">📄</div>
              <div>Click to upload questionnaire</div>
              <div style={{ fontSize: '0.875rem', color: '#999' }}>PDF, Excel, or TXT files</div>
            </div>
          </div>
        )}
        
        {/* Questionnaire Info */}
        {questionnaire && (
          <div className="card">
            <h2 className="card-title">Questionnaire: {questionnaire.filename}</h2>
            <p style={{ marginBottom: '1rem' }}>
              <strong>{questions.length}</strong> questions found
            </p>
            
            {questions.length > 0 && (
              <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  {questions.slice(0, 10).map((q, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem' }}>{q}</li>
                  ))}
                  {questions.length > 10 && (
                    <li>... and {questions.length - 10} more</li>
                  )}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {/* Step 2: Upload References */}
        {questionnaire && (
          <div className="card">
            <h2 className="card-title">Step 2: Upload Reference Documents</h2>
            <p style={{ marginBottom: '1rem', color: '#666' }}>
              Upload reference documents (PDF, TXT, Excel) that will be used to answer the questionnaire
            </p>
            
            {/* Hidden file input */}
            <input
              ref={referenceInputRef}
              type="file"
              className="file-input"
              accept=".pdf,.txt,.xlsx,.xls"
              onChange={handleReferenceUpload}
              disabled={loading}
            />
            
            {/* Clickable upload area */}
            <div className="upload-area" onClick={triggerReferenceUpload}>
              <div className="upload-icon">📚</div>
              <div>Click to upload reference documents</div>
              <div style={{ fontSize: '0.875rem', color: '#999' }}>PDF, TXT, or Excel files</div>
            </div>
            
            {references.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <h3>Uploaded References:</h3>
                <ul style={{ paddingLeft: '1.5rem', marginTop: '0.5rem' }}>
                  {references.map((ref) => (
                    <li key={ref.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span>{ref.filename}</span>
                      <button 
                        onClick={() => handleDeleteReference(ref.id)} 
                        className="btn btn-danger"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                      >
                        Delete
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {/* Step 3: Generate */}
        {questionnaire && references.length > 0 && (
          <div className="card">
            <h2 className="card-title">Step 3: Generate Answers</h2>
            <p style={{ marginBottom: '1rem', color: '#666' }}>
              Click below to generate answers using AI based on the reference documents
            </p>
            
            <button 
              onClick={handleGenerate} 
              className="btn btn-success"
              disabled={generating}
              style={{ padding: '1rem 2rem', fontSize: '1.125rem' }}
            >
              {generating ? 'Generating Answers...' : 'Generate Answers'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Upload;
