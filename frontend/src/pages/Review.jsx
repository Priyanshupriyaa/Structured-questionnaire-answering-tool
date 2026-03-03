import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';

function Review({ token }) {
  const { questionnaireId } = useParams();
  const [questionnaire, setQuestionnaire] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [coverage, setCoverage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingAnswer, setEditingAnswer] = useState(null);
  const [editText, setEditText] = useState('');
  const [exporting, setExporting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, [questionnaireId]);

  const loadData = async () => {
    try {
      const [qData, answersData] = await Promise.all([
        api.getQuestionnaire(questionnaireId, token),
        api.getAnswers(questionnaireId, token)
      ]);
      
      setQuestionnaire(qData);
      setAnswers(answersData.answers);
      setCoverage(answersData.coverage_summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (answer) => {
    setEditingAnswer(answer.id);
    setEditText(answer.answer || '');
  };

  const handleSaveEdit = async (answerId) => {
    try {
      await api.updateAnswer(answerId, editText, token);
      setSuccess('Answer updated successfully!');
      setEditingAnswer(null);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancelEdit = () => {
    setEditingAnswer(null);
    setEditText('');
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const blob = await api.exportQuestionnaire(questionnaireId, format, token);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${questionnaire.filename.replace(/\.[^/.]+$/, '')}_answered.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  };

  const parseCitations = (citationsStr) => {
    try {
      return JSON.parse(citationsStr || '[]');
    } catch {
      return [];
    }
  };

  const parseEvidence = (evidenceStr) => {
    try {
      return JSON.parse(evidenceStr || '[]');
    } catch {
      return [];
    }
  };

  if (loading) {
    return (
      <div>
        <nav className="navbar">
          <div className="navbar-brand">SecureSync Questionnaire Tool</div>
          <div className="navbar-menu">
            <Link to="/">Dashboard</Link>
          </div>
        </nav>
        <div className="container">
          <div className="loading">
            <div className="spinner"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-brand">SecureSync Questionnaire Tool</div>
        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>
        </div>
      </nav>
      
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h1>{questionnaire?.filename}</h1>
            <p style={{ color: '#666' }}>Review and edit generated answers</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              onClick={() => handleExport('docx')} 
              className="btn btn-primary"
              disabled={exporting}
            >
              Export DOCX
            </button>
          </div>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        {/* Coverage Summary */}
        {coverage && (
          <div className="coverage-summary">
            <div className="coverage-item">
              <div className="coverage-value">{coverage.total_questions}</div>
              <div className="coverage-label">Total Questions</div>
            </div>
            <div className="coverage-item">
              <div className="coverage-value" style={{ color: '#27ae60' }}>{coverage.answered}</div>
              <div className="coverage-label">Answered</div>
            </div>
            <div className="coverage-item">
              <div className="coverage-value" style={{ color: '#e74c3c' }}>{coverage.not_found}</div>
              <div className="coverage-label">Not Found</div>
            </div>
            <div className="coverage-item">
              <div className="coverage-value" style={{ color: '#f39c12' }}>{coverage.edited}</div>
              <div className="coverage-label">Edited</div>
            </div>
            <div className="coverage-item">
              <div className="coverage-value">{coverage.average_confidence}</div>
              <div className="coverage-label">Avg Confidence</div>
            </div>
          </div>
        )}
        
        {/* Answers List */}
        {answers.map((answer, index) => (
          <div key={answer.id} className="review-item">
            <div className="review-question">
              {index + 1}. {answer.question}
            </div>
            
            {editingAnswer === answer.id ? (
              <div>
                <textarea
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  style={{
                    width: '100%',
                    minHeight: '100px',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    fontFamily: 'inherit'
                  }}
                />
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <button onClick={() => handleSaveEdit(answer.id)} className="btn btn-success">
                    Save
                  </button>
                  <button onClick={handleCancelEdit} className="btn btn-secondary">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="review-answer">
                  {answer.is_not_found ? (
                    <span style={{ color: '#e74c3c', fontStyle: 'italic' }}>
                      Not found in references.
                    </span>
                  ) : (
                    answer.answer || <span style={{ color: '#999' }}>No answer</span>
                  )}
                </div>
                
                {/* Citations */}
                {answer.citations && parseCitations(answer.citations).length > 0 && (
                  <div className="review-citations">
                    <strong>Citations:</strong>
                    <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem' }}>
                      {parseCitations(answer.citations).map((cite, i) => (
                        <li key={i}>
                          {cite.document} - {cite.position}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Evidence Snippets */}
                {answer.evidence_snippets && parseEvidence(answer.evidence_snippets).length > 0 && (
                  <div>
                    <strong>Evidence:</strong>
                    {parseEvidence(answer.evidence_snippets).map((snippet, i) => (
                      <div key={i} className="review-evidence">
                        "{snippet}"
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Confidence Score */}
                {answer.confidence_score > 0 && (
                  <div className="review-confidence" style={{ marginTop: '0.5rem' }}>
                    <span>Confidence:</span>
                    <div className="confidence-bar">
                      <div 
                        className="confidence-fill" 
                        style={{ 
                          width: `${answer.confidence_score * 100}%`,
                          background: answer.confidence_score > 0.7 ? '#27ae60' : 
                                     answer.confidence_score > 0.5 ? '#f39c12' : '#e74c3c'
                        }}
                      ></div>
                    </div>
                    <span>{(answer.confidence_score * 100).toFixed(1)}%</span>
                  </div>
                )}
                
                {/* Status Badge */}
                <div style={{ marginTop: '0.5rem' }}>
                  <span className={`badge badge-${answer.status}`}>
                    {answer.status === 'edited' ? 'Manually Edited' : 'AI Generated'}
                  </span>
                </div>
                
                {/* Edit Button */}
                <button 
                  onClick={() => handleEdit(answer)} 
                  className="btn btn-secondary"
                  style={{ marginTop: '0.5rem' }}
                >
                  Edit Answer
                </button>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Review;
