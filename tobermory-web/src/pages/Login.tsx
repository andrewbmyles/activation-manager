import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import tobermoryLogo from '../assets/images/TobermoryLogo.png';
import '../assets/images/forest-background.css';
import './Login.css';

export const Login: React.FC = () => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(false);
    setIsLoading(true);

    // Simulate a slight delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500));

    const success = login(password);
    if (success) {
      navigate('/home');
    } else {
      setError(true);
      setPassword('');
    }
    setIsLoading(false);
  };

  return (
    <div className="login-page">
      <div className="login-background forest-background">
        <div className="overlay"></div>
        <div className="mist mist-1"></div>
        <div className="mist mist-2"></div>
        <div className="mist mist-3"></div>
      </div>

      <div className="login-container">
        <div className="login-box">
          <div className="logo-section">
            <img 
              src={tobermoryLogo} 
              alt="Tobermory AI" 
              className="logo-image"
            />
            <h1 className="company-name">
              tobermory<span className="accent">.ai</span>
            </h1>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="password">Access Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className={error ? 'error' : ''}
                disabled={isLoading}
                autoFocus
                required
              />
              {error && (
                <span className="error-message fade-in">
                  Invalid password. Please try again.
                </span>
              )}
            </div>

            <button 
              type="submit" 
              className="submit-btn"
              disabled={isLoading || !password}
            >
              {isLoading ? 'Authenticating...' : 'Enter'}
            </button>
          </form>
        </div>

        <div className="footer">
          Ontario, Canada
        </div>
      </div>
    </div>
  );
};