import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import API_BASE_URL from '../config/api';
import './SignIn.css';

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated, user } = useAuth();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated() && user) {
      const routes = {
        customer: '/customer',
        chef: '/chef',
        delivery: '/delivery',
        manager: '/manager'
      };
      navigate(routes[user.user_type] || '/customer', { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Create URLSearchParams for x-www-form-urlencoded
      const params = new URLSearchParams();
      params.append('username', formData.email); // Backend allows email as username
      params.append('password', formData.password);

      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      if (response.data.access_token) {
        // Store token
        const token = response.data.access_token;
        localStorage.setItem('token', token);
        
        // Fetch user details
        const userResponse = await axios.get(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const user = userResponse.data;
        
        // Login user via AuthContext
        login(user);

        // Redirect based on user type
        const routes = {
          customer: '/customer',
          chef: '/chef',
          delivery: '/delivery',
          manager: '/manager'
        };
        // Use the actual user type from backend
        navigate(routes[user.user_type] || '/customer');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="signin-container">
      <div className="signin-card">
        <h1 className="signin-title">Sign In</h1>
        <form onSubmit={handleSubmit} className="signin-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className="input"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className="input"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          {error && (
            <div className="error-message" style={{ color: '#e74c3c', marginBottom: '15px', fontSize: '14px' }}>
              {error}
            </div>
          )}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignIn;
