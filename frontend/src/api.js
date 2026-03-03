const API_BASE_URL = 'http://localhost:8000';

const getHeaders = (token) => ({
  'Authorization': `Bearer ${token}`,
});

export const api = {
  // Auth
  signup: async (username, email, password) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }
    return response.json();
  },

  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    return response.json();
  },

  getMe: async (token) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get user');
    return response.json();
  },

  // Questionnaires
  uploadQuestionnaire: async (file, token) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/api/questionnaires`, {
      method: 'POST',
      headers: getHeaders(token),
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    return response.json();
  },

  getQuestionnaires: async (token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get questionnaires');
    return response.json();
  },

  getQuestionnaire: async (id, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${id}`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get questionnaire');
    return response.json();
  },

  getQuestions: async (id, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${id}/questions`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get questions');
    return response.json();
  },

  deleteQuestionnaire: async (id, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${id}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to delete questionnaire');
    return response.json();
  },

  // Reference Documents
  uploadReference: async (questionnaireId, file, token) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${questionnaireId}/references`, {
      method: 'POST',
      headers: getHeaders(token),
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    return response.json();
  },

  getReferences: async (questionnaireId, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${questionnaireId}/references`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get references');
    return response.json();
  },

  deleteReference: async (referenceId, token) => {
    const response = await fetch(`${API_BASE_URL}/api/references/${referenceId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to delete reference');
    return response.json();
  },

  // Answers
  generateAnswers: async (questionnaireId, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${questionnaireId}/generate`, {
      method: 'POST',
      headers: getHeaders(token),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Generation failed');
    }
    return response.json();
  },

  getAnswers: async (questionnaireId, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${questionnaireId}/answers`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get answers');
    return response.json();
  },

  updateAnswer: async (answerId, answer, token) => {
    const response = await fetch(`${API_BASE_URL}/api/answers/${answerId}?answer_text=${encodeURIComponent(answer)}`, {
      method: 'PUT',
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to update answer');
    return response.json();
  },

  // Export
  exportQuestionnaire: async (questionnaireId, format, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${questionnaireId}/export?format=${format}`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to export');
    return response.blob();
  },

  getCoverage: async (questionnaireId, token) => {
    const response = await fetch(`${API_BASE_URL}/api/questionnaires/${questionnaireId}/coverage`, {
      headers: getHeaders(token),
    });
    if (!response.ok) throw new Error('Failed to get coverage');
    return response.json();
  },
};
