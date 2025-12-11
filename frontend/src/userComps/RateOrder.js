import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './RateOrder.css';

const RateOrder = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { orderId: paramOrderId } = useParams();
  
  const initialOrderId = paramOrderId || (location.state ? location.state.orderId : null);
  
  const [orderId, setOrderId] = useState(initialOrderId);
  const [rateableOrders, setRateableOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  
  // For individual item ratings
  const [orderItems, setOrderItems] = useState([]);
  const [itemRatings, setItemRatings] = useState({}); // { itemId: rating }
  const [hoveredItemStars, setHoveredItemStars] = useState({}); // { itemId: star }

  // Delivery rating
  const [deliveryRating, setDeliveryRating] = useState(0);
  const [hoveredDeliveryStar, setHoveredDeliveryStar] = useState(0);
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 1. If no orderId, fetch list
  useEffect(() => {
    if (!orderId) {
      fetchRateableOrders();
    } else {
      fetchOrderDetails(orderId);
    }
  }, [orderId]);

  const fetchRateableOrders = async () => {
    setLoadingOrders(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/orders/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const orders = Array.isArray(response.data) ? response.data : (response.data.orders || []);
      const validOrders = orders.filter(o => 
        (o.status?.toLowerCase() === 'delivered' || o.status?.toLowerCase() === 'completed') &&
        (!o.delivery_rating) // Only check overall/delivery rating presence to decide availability
      );
      validOrders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setRateableOrders(validOrders);
    } catch (err) {
      console.error(err);
      setError('Failed to load orders.');
    } finally {
      setLoadingOrders(false);
    }
  };

  const fetchOrderDetails = async (id) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/orders/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrderItems(response.data.items || []);
    } catch (err) {
      setError('Failed to load order details.');
    }
  };

  const handleSelectOrder = (id) => {
    setOrderId(id);
    window.history.replaceState(null, '', `/reviews/${id}`);
  };

  const setItemRating = (itemId, rating) => {
    setItemRatings(prev => ({ ...prev, [itemId]: rating }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate: At least one item rated OR delivery rated
    const hasItemRating = Object.values(itemRatings).some(r => r > 0);
    if (!hasItemRating && deliveryRating === 0) {
      setError('Please rate at least one dish or the delivery service.');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      const payload = {
        delivery_rating: deliveryRating || undefined,
        // Convert itemRatings map to list of {order_item_id, rating}
        items: Object.entries(itemRatings).map(([itemId, rating]) => ({
          order_item_id: parseInt(itemId),
          rating: rating
        }))
      };

      await axios.put(
        `${API_BASE_URL}/api/orders/${orderId}/rate`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setSuccess('Thank you for your feedback!');
      setTimeout(() => {
        navigate('/customer');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit rating');
    }
  };

  // --- Render Selection List ---
  if (!orderId) {
    return (
      <div className="rate-order-container">
        <div className="rate-card selection-card">
          <h1>Select an Order to Rate</h1>
          {error && <p className="error-text">{error}</p>}
          {loadingOrders ? <p>Loading...</p> : rateableOrders.length === 0 ? (
            <div className="empty-state">
              <p>No recent orders found to rate.</p>
              <button className="btn btn-primary" onClick={() => navigate('/customer')}>Dashboard</button>
            </div>
          ) : (
            <>
              <div className="orders-list-compact">
                {rateableOrders.map(order => (
                  <div key={order.id} className="order-selection-item" onClick={() => handleSelectOrder(order.id)}>
                    <div className="order-info">
                      <strong>Order #{order.id}</strong>
                      <span>{new Date(order.created_at).toLocaleDateString()}</span>
                    </div>
                    <button className="btn-small">Rate</button>
                  </div>
                ))}
              </div>
              <div className="button-group">
                <button className="btn btn-secondary" onClick={() => navigate('/customer')}>
                  Back to Dashboard
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  // --- Render Rating Form ---
  return (
    <div className="rate-order-container">
      <div className="rate-card wide-card">
        <h1>Rate Order #{orderId}</h1>
        <p>Rate each dish and the delivery service.</p>
        
        {error && <div className="error-message" style={{ color: 'red' }}>{error}</div>}
        {success && <div className="success-message" style={{ color: 'green' }}>{success}</div>}

        <form onSubmit={handleSubmit}>
          
          <div className="items-rating-list">
            <h3>Dishes</h3>
            {orderItems.map(item => (
              <div key={item.id} className="item-rating-row">
                <span className="item-name">{item.dish_name}</span>
                <div className="star-rating-md">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={`item-${item.id}-${star}`}
                      type="button"
                      className={`star-btn-md ${(hoveredItemStars[item.id] || itemRatings[item.id] || 0) >= star ? 'active' : ''}`}
                      onClick={() => setItemRating(item.id, star)}
                      onMouseEnter={() => setHoveredItemStars(prev => ({ ...prev, [item.id]: star }))}
                      onMouseLeave={() => setHoveredItemStars(prev => ({ ...prev, [item.id]: 0 }))}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="rating-section delivery-section">
            <h3>Delivery Service</h3>
            <div className="star-rating-lg">
              {[1, 2, 3, 4, 5].map(star => (
                <button
                  key={`delivery-${star}`}
                  type="button"
                  className={`star-btn-lg ${(hoveredDeliveryStar || deliveryRating) >= star ? 'active' : ''}`}
                  onClick={() => setDeliveryRating(star)}
                  onMouseEnter={() => setHoveredDeliveryStar(star)}
                  onMouseLeave={() => setHoveredDeliveryStar(0)}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          <div className="button-group">
            <button type="button" className="btn btn-secondary" onClick={() => setOrderId(null)}>Back</button>
            <button type="submit" className="btn btn-primary">Submit Review</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RateOrder;
