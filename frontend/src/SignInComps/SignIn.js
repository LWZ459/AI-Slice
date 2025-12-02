import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import API_BASE_URL from '../config/api';
import './SignIn.css';

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    userType: 'customer'
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
      navigate(routes[user.userType] || '/customer', { replace: true });
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
      const response = await axios.post(`${API_BASE_URL}/api/auth/signin`, {
        email: formData.email,
        password: formData.password
      });

      if (response.data.success) {
        const user = response.data.user;
        
        // Verify user type matches selected type (optional check)
        if (formData.userType && user.userType !== formData.userType) {
          setError(`This account is registered as ${user.userType}, not ${formData.userType}`);
          setLoading(false);
          return;
        }

        // Login user via AuthContext
        login(user);

        // Redirect based on user type
        const routes = {
          customer: '/customer',
          chef: '/chef',
          delivery: '/delivery',
          manager: '/manager'
        };
        navigate(routes[user.userType] || '/customer');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Invalid email or password. Please try again.');
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

          <div className="form-group">
            <label htmlFor="userType">User Type</label>
            <select
              id="userType"
              name="userType"
              className="input"
              value={formData.userType}
              onChange={handleChange}
            >
              <option value="customer">Customer</option>
              <option value="chef">Chef</option>
              <option value="delivery">Delivery Staff</option>
              <option value="manager">Manager</option>
            </select>
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

