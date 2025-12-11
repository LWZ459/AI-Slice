import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './RateOrder.css';

const ComplimentPage = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [targetType, setTargetType] = useState(''); // 'chef' or 'delivery'
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/orders/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Filter to only show delivered/completed orders
      const completedOrders = response.data.filter(o => 
        ['delivered', 'completed'].includes(o.status.toLowerCase())
      );
      setOrders(completedOrders);
      setLoading(false);
    } catch (err) {
      setError('Failed to load orders');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!selectedOrder || !targetType || !title) {
      setError('Please select an order, who to compliment, and add a title');
      return;
    }

    // Get the target user ID based on selection
    let targetId;
    if (targetType === 'chef') {
      // Use chef_id from the first item (simplified - assumes one chef per order)
      targetId = selectedOrder.items[0]?.chef_id;
    } else if (targetType === 'delivery') {
      targetId = selectedOrder.delivery_person_id;
    }

    if (!targetId) {
      setError(`Could not find ${targetType} information for this order`);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/reputation/compliment`,
        {
          receiver_id: targetId,
          title: title,
          description: description || undefined,
          order_id: selectedOrder.id
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setSuccess('Compliment submitted successfully! Thank you for your feedback. 🌟');
      setTimeout(() => {
        navigate('/customer');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit compliment');
    }
  };

  if (loading) {
    return (
      <div className="rate-order-container">
        <div className="rate-card">
          <p>Loading your orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rate-order-container">
      <div className="rate-card">
        <h1>Give a Compliment 🌟</h1>
        <p>Recognize someone who provided excellent service!</p>
        
        {error && <div className="error-message" style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
        {success && <div className="success-message" style={{ color: 'green', marginBottom: '10px' }}>{success}</div>}

        {orders.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <p>No completed orders found.</p>
            <p style={{ color: '#666' }}>Complete an order first to give compliments!</p>
            <button className="btn btn-primary" onClick={() => navigate('/menu')} style={{ marginTop: '15px' }}>
              Browse Menu
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            
            <div className="form-group">
              <label>Select Order *</label>
              <select 
                value={selectedOrder?.id || ''} 
                onChange={e => {
                  const order = orders.find(o => o.id === parseInt(e.target.value));
                  setSelectedOrder(order);
                  setTargetType('');
                }}
                required
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
              >
                <option value="">-- Select an order --</option>
                {orders.map(order => (
                  <option key={order.id} value={order.id}>
                    Order #{order.id} - {order.items.map(i => i.dish_name).join(', ').substring(0, 40)}...
                  </option>
                ))}
              </select>
            </div>

            {selectedOrder && (
              <div className="form-group">
                <label>Who would you like to compliment? *</label>
                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                  <button
                    type="button"
                    className={`btn ${targetType === 'chef' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setTargetType('chef')}
                    style={{ flex: 1, padding: '15px' }}
                  >
                    👨‍🍳 Chef
                    <br/>
                    <small>Food was great!</small>
                  </button>
                  <button
                    type="button"
                    className={`btn ${targetType === 'delivery' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setTargetType('delivery')}
                    style={{ flex: 1, padding: '15px' }}
                    disabled={!selectedOrder.delivery_person_id}
                  >
                    🚴 Delivery
                    <br/>
                    <small>{selectedOrder.delivery_person_id ? 'Fast & friendly!' : 'No delivery assigned'}</small>
                  </button>
                </div>
              </div>
            )}

            {targetType && (
              <>
                <div className="form-group">
                  <label>Title *</label>
                  <input 
                    type="text" 
                    value={title} 
                    onChange={e => setTitle(e.target.value)}
                    placeholder={targetType === 'chef' ? 'e.g., Delicious food!' : 'e.g., Super fast delivery!'}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Description (optional)</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Tell us more about your positive experience..."
                    rows="3"
                  />
                </div>

                <div className="button-group">
                  <button type="button" className="btn btn-secondary" onClick={() => navigate('/customer')}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" style={{ backgroundColor: '#27ae60' }}>
                    Submit Compliment 🌟
                  </button>
                </div>
              </>
            )}
          </form>
        )}
      </div>
    </div>
  );
};

export default ComplimentPage;
