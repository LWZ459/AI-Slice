import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import API_BASE_URL from '../config/api';
import './OrderTracking.css';

const OrderTracking = () => {
  const { orderId } = useParams();
  const { user } = useAuth();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user || !user.id) {
      setLoading(false);
      return;
    }

    fetchOrderDetails();
    
    // Set up polling for real-time updates every 3 seconds
    const pollInterval = setInterval(() => {
      fetchOrderDetails();
    }, 3000);

    return () => clearInterval(pollInterval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId, user?.id]);

  const fetchOrderDetails = async () => {
    try {
      if (!user || !user.id) {
        setError('Please sign in to view order details');
        setLoading(false);
        return;
      }

      // Fetch specific order directly
      const response = await axios.get(`${API_BASE_URL}/api/orders/${orderId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const foundOrder = response.data;
      
      if (foundOrder) {
        setOrder(foundOrder);
      } else {
        setError('Order not found');
      }
    } catch (err) {
      setError('Failed to load order details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusSteps = (status) => {
    const statusLower = status?.toLowerCase() || 'placed';
    const steps = [
      { name: 'Order Placed', completed: true, active: statusLower.includes('placed') },
      { name: 'Preparing', completed: statusLower.includes('preparing') || statusLower.includes('assigned'), active: statusLower.includes('preparing') },
      { name: 'Assigned for Delivery', completed: statusLower.includes('assigned') || statusLower.includes('delivery'), active: statusLower.includes('assigned') },
      { name: 'Out for Delivery', completed: statusLower.includes('delivery') && !statusLower.includes('delivered'), active: statusLower.includes('delivery') && !statusLower.includes('delivered') },
      { name: 'Delivered', completed: statusLower.includes('delivered'), active: statusLower.includes('delivered') }
    ];
    return steps;
  };

  const getEstimatedWaitTime = (status) => {
    if (!status) return null;
    
    const statusLower = status.toLowerCase();
    
    if (statusLower.includes('delivered') || statusLower.includes('cancelled')) {
      return null;
    }
    
    if (statusLower.includes('placed')) {
      return "~20-30 minutes";
    } else if (statusLower.includes('preparing') || statusLower.includes('cooking')) {
      return "~15-25 minutes";
    } else if (statusLower.includes('assigned')) {
      return "~10-20 minutes";
    } else if (statusLower.includes('delivery')) {
      return "~5-15 minutes";
    }
    
    return "~15-30 minutes";
  };

  if (loading) {
    return (
      <div className="order-tracking">
        <div className="tracking-container">
          <p style={{ textAlign: 'center', padding: '40px' }}>Loading order details...</p>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="order-tracking">
        <div className="tracking-container">
          <div className="error-card">
            <h2>Order Not Found</h2>
            <p>{error || 'The order you are looking for does not exist.'}</p>
            <Link to="/customer" className="btn btn-primary">Back to Dashboard</Link>
          </div>
        </div>
      </div>
    );
  }

  const statusSteps = getStatusSteps(order.status);
  const estimatedWaitTime = getEstimatedWaitTime(order.status);

  return (
    <div className="order-tracking">
      <div className="tracking-container">
        <div className="tracking-header">
          <Link to="/customer" className="back-link">← Back to Orders</Link>
          <h1>Order #{order.id}</h1>
          <p className="order-date-full">Placed on {formatDate(order.created_at || order.createdAt)}</p>
        </div>

        <div className="tracking-card">
          <h2>Order Status</h2>
          {estimatedWaitTime && (
            <div className="estimated-wait-time">
              <span className="wait-time-label">Estimated wait time:</span>
              <span className="wait-time-value">{estimatedWaitTime}</span>
            </div>
          )}
          <div className="status-timeline">
            {statusSteps.map((step, index) => (
              <div key={index} className={`timeline-step ${step.completed ? 'completed' : ''} ${step.active ? 'active' : ''}`}>
                <div className="timeline-marker">
                  {step.completed ? '✓' : index + 1}
                </div>
                <div className="timeline-content">
                  <h3>{step.name}</h3>
                </div>
              </div>
            ))}
          </div>
          <div className="current-status">
            <span className={`status-badge ${order.status?.toLowerCase().replace(/\s+/g, '-')}`}>
              {order.status || 'Placed'}
            </span>
          </div>
        </div>

        <div className="tracking-card">
          <h2>Order Details</h2>
          <div className="order-items-detailed">
            {order.items && order.items.length > 0 ? (
              order.items.map((item, idx) => (
                <div key={idx} className="order-item-detailed">
                  <div className="item-info-detailed">
                    <span className="item-name-detailed">{item.dish_name || item.name}</span>
                    <span className="item-quantity-detailed">Quantity: {item.quantity}</span>
                  </div>
                  <span className="item-price-detailed">
                    ${((item.unit_price || item.price || 0) * (item.quantity || 1)).toFixed(2)}
                  </span>
                </div>
              ))
            ) : (
              <p>No items found</p>
            )}
          </div>
        </div>

        <div className="tracking-card">
          <h2>Order Summary</h2>
          <div className="order-summary-detailed">
            <div className="summary-row-detailed">
              <span>Subtotal:</span>
              <span>${order.subtotal?.toFixed(2) || '0.00'}</span>
            </div>
            {order.discount_amount > 0 && (
              <div className="summary-row-detailed vip-discount">
                <span>VIP Discount (5%):</span>
                <span>-${order.discount_amount.toFixed(2)}</span>
              </div>
            )}
            <div className="summary-row-detailed total">
              <span>Total:</span>
              <span>${order.total_amount?.toFixed(2) || '0.00'}</span>
            </div>
          </div>
        </div>

        {order.deliveryPersonId && (
          <div className="tracking-card">
            <h2>Delivery Information</h2>
            <p>Delivery Person ID: {order.deliveryPersonId}</p>
            {order.managerOverride && (
              <p className="manager-note">
                <strong>Note:</strong> This delivery was assigned by manager override.
                {order.justification && ` Reason: ${order.justification}`}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTracking;
