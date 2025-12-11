import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './BiddingPage.css';

const BiddingPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { deliveryId } = location.state || {}; // Get delivery ID from navigation state

  const [selectedOrder, setSelectedOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bidAmount, setBidAmount] = useState('');
  const [estimatedTime, setEstimatedTime] = useState('');
  const [bids, setBids] = useState([]);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!deliveryId) {
      setError('No delivery selected');
      setLoading(false);
      return;
    }
    fetchDeliveryDetails();
  }, [deliveryId]);

  const fetchDeliveryDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/delivery/${deliveryId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedOrder(response.data);
    } catch (err) {
      setError('Failed to fetch delivery details');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitBid = async (e) => {
    e.preventDefault();
    setError('');
    const amount = parseFloat(bidAmount);
    const time = parseInt(estimatedTime);

    if (isNaN(amount) || amount <= 0) {
      setError('Please enter a valid bid amount');
      return;
    }
    
    if (isNaN(time) || time <= 0) {
      setError('Please enter a valid estimated time');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/delivery/${deliveryId}/bid`,
        {
          bid_amount: amount,
          estimated_time: time,
          notes: "Placed via dashboard"
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setSuccessMessage('Bid placed successfully!');
      setTimeout(() => {
        navigate('/delivery');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to place bid');
    }
  };

  if (loading) return <div className="bidding-page"><p>Loading...</p></div>;
  if (!selectedOrder) return <div className="bidding-page"><p className="error">{error || 'Delivery not found'}</p></div>;

  return (
    <div className="bidding-page">
      <h1 className="page-title">Place Delivery Bid</h1>
      
      {successMessage && <div className="success-message" style={{color: 'green', textAlign: 'center', marginBottom: '20px'}}>{successMessage}</div>}

      <div className="bidding-grid">
        <div className="bidding-card">
          <h2>Order Details</h2>
          <div className="order-info">
            <div className="info-row">
              <span className="info-label">Order ID:</span>
              <span className="info-value">#{selectedOrder.order_id}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Distance:</span>
              <span className="info-value">{selectedOrder.distance} km</span>
            </div>
            <div className="info-row">
              <span className="info-label">Pickup:</span>
              <span className="info-value">{selectedOrder.pickup_address}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Dropoff:</span>
              <span className="info-value">{selectedOrder.delivery_address}</span>
            </div>
             <div className="info-row">
              <span className="info-label">Suggested Fee:</span>
              <span className="info-value base-price">${selectedOrder.delivery_fee.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div className="bidding-card">
          <h2>Place Your Bid</h2>
          {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
          <form onSubmit={handleSubmitBid} className="bid-form">
            <div className="form-group">
              <label htmlFor="bidAmount">Bid Amount ($)</label>
              <input
                type="number"
                id="bidAmount"
                className="input"
                value={bidAmount}
                onChange={(e) => setBidAmount(e.target.value)}
                placeholder="Enter your bid amount"
                step="0.01"
                min="0"
                required
              />
            </div>
             <div className="form-group">
              <label htmlFor="estimatedTime">Est. Time (minutes)</label>
              <input
                type="number"
                id="estimatedTime"
                className="input"
                value={estimatedTime}
                onChange={(e) => setEstimatedTime(e.target.value)}
                placeholder="e.g. 15"
                min="1"
                required
              />
            </div>
            <p className="form-hint">Enter an amount lower than base price to increase your chances</p>
            <button type="submit" className="btn btn-primary btn-large">Submit Bid</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default BiddingPage;
