import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Review from './pages/Review';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  
  const setAuth = (newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken);
    } else {
      localStorage.removeItem('token');
    }
    setToken(newToken);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={!token ? <Login setAuth={setAuth} /> : <Navigate to="/" />} />
        <Route path="/signup" element={!token ? <Signup setAuth={setAuth} /> : <Navigate to="/" />} />
        <Route path="/" element={token ? <Dashboard token={token} setAuth={setAuth} /> : <Navigate to="/login" />} />
        <Route path="/upload" element={token ? <Upload token={token} /> : <Navigate to="/login" />} />
        <Route path="/upload/:questionnaireId" element={token ? <Upload token={token} /> : <Navigate to="/login" />} />
        <Route path="/review/:questionnaireId" element={token ? <Review token={token} /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
