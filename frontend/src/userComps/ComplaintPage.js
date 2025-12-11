import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './RateOrder.css'; // Re-use styling

const ComplaintPage = () => {
  const navigate = useNavigate();
  const [complaintType, setComplaintType] = useState('chef');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [targetId, setTargetId] = useState(''); // Just ID for now
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!title || !description || !targetId) {
      setError('All fields are required');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/reputation/complaint`,
        {
          subject_id: parseInt(targetId),
          title: title,
          description: description
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setSuccess('Complaint filed successfully. A manager will review it.');
      setTimeout(() => {
        navigate('/customer');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to file complaint');
    }
  };

  return (
    <div className="rate-order-container">
      <div className="rate-card">
        <h1>File a Complaint</h1>
        <p>We take feedback seriously. Please describe the issue.</p>
        
        {error && <div className="error-message" style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
        {success && <div className="success-message" style={{ color: 'green', marginBottom: '10px' }}>{success}</div>}

        <form onSubmit={handleSubmit}>
          
          <div className="form-group">
            <label>Complaint Against (User ID)</label>
            <input 
                type="number" 
                value={targetId} 
                onChange={e => setTargetId(e.target.value)}
                placeholder="Enter User ID (Chef/Delivery/Customer)"
                required
            />
            <small style={{color: '#666'}}>Find ID from Order Details or Forum</small>
          </div>

          <div className="form-group">
            <label>Title</label>
            <input 
                type="text" 
                value={title} 
                onChange={e => setTitle(e.target.value)}
                placeholder="Brief summary"
                required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detailed explanation of the incident..."
              rows="5"
              required
            />
          </div>

          <div className="button-group">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/customer')}>
              Cancel
            </button>
            <button type="submit" className="btn btn-danger">
              Submit Complaint
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ComplaintPage;

