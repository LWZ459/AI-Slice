import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import API_BASE_URL from '../config/api';
import './CustomerDashboard.css';

const CustomerDashboard = () => {
  const { user, isVIP } = useAuth();
  const { cart, getTotalPrice } = useCart();
  const [walletBalance, setWalletBalance] = useState(user?.walletBalance || 0);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && user.id) {
      fetchOrders();
      setWalletBalance(user.walletBalance || 0);
      
      // Set up polling for real-time updates every 5 seconds
      const pollInterval = setInterval(() => {
        fetchOrders();
      }, 5000);

      return () => clearInterval(pollInterval);
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchOrders = async () => {
    if (!user || !user.id) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/orders/user/${user.id}`);
      if (response.data.orders) {
        // Sort orders by creation date (newest first)
        const sortedOrders = response.data.orders.sort((a, b) => 
          new Date(b.createdAt) - new Date(a.createdAt)
        );
        setOrders(sortedOrders);
      }
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const cartTotal = getTotalPrice();
  // Only calculate discount if user is VIP and cart has items
  const isUserVIP = user && isVIP();
  const discount = (isUserVIP && cartTotal > 0) ? cartTotal * 0.05 : 0;
  const finalTotal = cartTotal - discount;

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusClass = (status) => {
    const statusLower = status?.toLowerCase() || '';
    if (statusLower.includes('placed')) return 'placed';
    if (statusLower.includes('preparing') || statusLower.includes('cooking')) return 'preparing';
    if (statusLower.includes('assigned') || statusLower.includes('delivery')) return 'delivery';
    if (statusLower.includes('delivered')) return 'delivered';
    if (statusLower.includes('cancelled')) return 'cancelled';
    return 'placed';
  };

  return (
    <div className="customer-dashboard">
      <h1 className="dashboard-title">Customer Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card wallet-card">
          <h2>Wallet</h2>
          <div className="wallet-balance">
            <span className="balance-amount">${walletBalance.toFixed(2)}</span>
            {isUserVIP && <span className="vip-badge">VIP</span>}
          </div>
          <button className="btn btn-success">Deposit Money</button>
        </div>

        <div className="dashboard-card cart-card">
          <h2>Shopping Cart</h2>
          {cart.length === 0 ? (
            <p className="empty-cart">Your cart is empty</p>
          ) : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <span>{item.name}</span>
                    <span>Qty: {item.quantity || 1}</span>
                    <span>${((item.price || 0) * (item.quantity || 1)).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div className="cart-summary">
                <div className="summary-row">
                  <span>Subtotal:</span>
                  <span>${cartTotal.toFixed(2)}</span>
                </div>
                {isUserVIP && discount > 0 && (
                  <div className="summary-row vip-discount">
                    <span>VIP Discount (5%):</span>
                    <span>-${discount.toFixed(2)}</span>
                  </div>
                )}
                <div className="summary-row total">
                  <span>Total:</span>
                  <span>${finalTotal.toFixed(2)}</span>
                </div>
              </div>
              <Link to="/checkout" className="btn btn-primary">Checkout</Link>
            </>
          )}
        </div>

        <div className="dashboard-card">
          <h2>My Orders</h2>
          {loading ? (
            <p style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>Loading orders...</p>
          ) : orders.length === 0 ? (
            <p style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
              No orders yet. <Link to="/menu" style={{ color: '#2c3e50', textDecoration: 'underline' }}>Browse menu</Link> to place your first order!
            </p>
          ) : (
            <div className="orders-list">
              {orders.map(order => (
                <div key={order.id} className="order-item">
                  <div className="order-header">
                    <Link to={`/orders/${order.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                      <span>Order #{order.id}</span>
                    </Link>
                    <span className={`status ${getStatusClass(order.status)}`}>
                      {order.status || 'Placed'}
                    </span>
                  </div>
                  <p className="order-date">{formatDate(order.createdAt)}</p>
                  <div className="order-items-preview">
                    {order.items && order.items.slice(0, 2).map((item, idx) => (
                      <span key={idx} className="order-item-name">
                        {item.quantity}x {item.name}
                      </span>
                    ))}
                    {order.items && order.items.length > 2 && (
                      <span className="order-item-name">+{order.items.length - 2} more</span>
                    )}
                  </div>
                  <div className="order-total-row">
                    {order.discount > 0 && (
                      <span className="order-discount">Discount: -${order.discount.toFixed(2)}</span>
                    )}
                    <p className="order-total">Total: ${order.total?.toFixed(2) || '0.00'}</p>
                  </div>
                  <Link 
                    to={`/orders/${order.id}`} 
                    className="btn btn-secondary"
                    style={{ marginTop: '10px', fontSize: '14px', padding: '8px 16px' }}
                  >
                    Track Order
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-card">
          <h2>Ratings & Reviews</h2>
          <div className="reviews-section">
            <Link to="/reviews" className="btn btn-secondary">Rate Food</Link>
            <Link to="/delivery-reviews" className="btn btn-secondary">Rate Delivery</Link>
          </div>
        </div>

        <div className="dashboard-card">
          <h2>Discussion Forums</h2>
          <p>Join conversations with other customers</p>
          <Link to="/forums" className="btn">View Forums</Link>
        </div>

        <div className="dashboard-card">
          <h2>Quick Actions</h2>
          <div className="quick-actions">
            <Link to="/menu" className="action-btn">Browse Menu</Link>
            <Link to="/chat" className="action-btn">AI Assistant</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;

