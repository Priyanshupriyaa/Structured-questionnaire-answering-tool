import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api';

function Dashboard({ token, setAuth }) {
  const [questionnaires, setQuestionnaires] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadQuestionnaires();
  }, []);

  const loadQuestionnaires = async () => {
    try {
      const data = await api.getQuestionnaires(token);
      setQuestionnaires(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this questionnaire?')) return;
    
    try {
      await api.deleteQuestionnaire(id, token);
      loadQuestionnaires();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogout = () => {
    setAuth(null);
  };

  const getStatusBadge = (status) => {
    const badges = {
      'pending': 'badge-pending',
      'generated': 'badge-generated',
      'reviewed': 'badge-reviewed'
    };
    return badges[status] || 'badge-pending';
  };

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-brand">SecureSync Questionnaire Tool</div>
        <div className="navbar-menu">
          <Link to="/">Dashboard</Link>
          <Link to="/upload">Upload New</Link>
          <button onClick={handleLogout} className="btn" style={{ background: 'transparent', color: 'white' }}>
            Logout
          </button>
        </div>
      </nav>
      
      <div className="container">
        <div className="dashboard-header">
          <h1>My Questionnaires</h1>
          <Link to="/upload" className="btn btn-primary">Upload New Questionnaire</Link>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : questionnaires.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ marginBottom: '1rem', color: '#666' }}>No questionnaires yet.</p>
            <Link to="/upload" className="btn btn-primary">Upload Your First Questionnaire</Link>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {questionnaires.map((q) => (
                  <tr key={q.id}>
                    <td>{q.filename}</td>
                    <td>{q.file_type.toUpperCase()}</td>
                    <td>
                      <span className={`badge ${getStatusBadge(q.status)}`}>
                        {q.status}
                      </span>
                    </td>
                    <td>{new Date(q.created_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <Link to={`/upload/${q.id}`} className="btn btn-secondary">
                          {q.status === 'pending' ? 'Add References' : 'Edit'}
                        </Link>
                        {q.status === 'generated' && (
                          <Link to={`/review/${q.id}`} className="btn btn-primary">
                            Review
                          </Link>
                        )}
                        <button 
                          onClick={() => handleDelete(q.id)} 
                          className="btn btn-danger"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
