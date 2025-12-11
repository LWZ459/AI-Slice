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
  const [walletBalance, setWalletBalance] = useState(0);
  const [walletLoading, setWalletLoading] = useState(true);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [depositAmount, setDepositAmount] = useState('');
  const [depositLoading, setDepositLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [myComplaints, setMyComplaints] = useState([]);
  const [myCompliments, setMyCompliments] = useState([]);

  useEffect(() => {
    if (user && user.id) {
      fetchWallet();
      fetchOrders();
      fetchFeedback();
      
      // Set up polling for real-time updates every 5 seconds
      const pollInterval = setInterval(() => {
        fetchOrders();
        fetchWallet();
      }, 5000);

      return () => clearInterval(pollInterval);
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchWallet = async () => {
    if (!user || !user.id) {
      setWalletLoading(false);
      return;
    }
    
    try {
      setWalletLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/wallet`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const balance = response.data.balance || 0;
      setWalletBalance(balance);
    } catch (error) {
      // Set to 0 if error (user might not be a customer)
      setWalletBalance(0);
    } finally {
      setWalletLoading(false);
    }
  };

  const fetchOrders = async () => {
    if (!user || !user.id) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/orders/?_t=${new Date().getTime()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      // The API returns a list of orders directly, not wrapped in an object
      const ordersData = Array.isArray(response.data) ? response.data : (response.data.orders || []);
      
      if (ordersData) {
        // Sort orders by creation date (newest first)
        const sortedOrders = ordersData.sort((a, b) => 
          new Date(b.created_at || b.createdAt) - new Date(a.created_at || a.createdAt)
        );
        setOrders(sortedOrders);
      }
    } catch (error) {
      // Silently fail
    } finally {
      setLoading(false);
    }
  };

  const fetchFeedback = async () => {
    try {
      const token = localStorage.getItem('token');
      const [complaintsRes, complimentsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/reputation/complaints`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE_URL}/api/reputation/compliments`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      // Filter to only show complaints I filed
      setMyComplaints(complaintsRes.data.filter(c => c.is_mine));
      // Filter to only show compliments I gave
      setMyCompliments(complimentsRes.data.filter(c => c.is_mine));
    } catch (error) {
      // Silently fail
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

  const handleDeposit = async () => {
    const amount = parseFloat(depositAmount);
    setError('');
    setSuccessMessage('');
    
    if (!amount || amount <= 0) {
      setError('Please enter a valid amount greater than 0');
      return;
    }

    setDepositLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please sign in again to deposit money.');
      }
      
      const response = await axios.post(
        `${API_BASE_URL}/api/wallet/deposit`,
        {
          amount: amount,
          payment_method: 'credit_card'
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data.success) {
        // Update balance immediately
        setWalletBalance(response.data.balance);
        // Also refetch to ensure we have the latest data
        await fetchWallet();
        setDepositAmount('');
        setSuccessMessage(`Successfully deposited $${amount.toFixed(2)}! Your new balance is $${response.data.balance.toFixed(2)}`);
        
        // Hide modal after delay
        setTimeout(() => {
          setShowDepositModal(false);
          setSuccessMessage('');
        }, 2000);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Deposit failed. Please try again.');
    } finally {
      setDepositLoading(false);
    }
  };

  return (
    <div className="customer-dashboard">
      <h1 className="dashboard-title">Customer Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card wallet-card">
          <h2>Wallet</h2>
          {walletLoading ? (
            <div className="wallet-balance">
              <span className="balance-label">Loading balance...</span>
            </div>
          ) : (
            <div className="wallet-balance">
              <div className="balance-display">
                <span className="balance-label">Current Balance:</span>
                <span className="balance-amount">${walletBalance.toFixed(2)}</span>
              </div>
              {isUserVIP && <span className="vip-badge">VIP</span>}
            </div>
          )}
          <button className="btn btn-success" onClick={() => setShowDepositModal(true)}>
            Deposit Money
          </button>
          
          {user && user.reputation && user.reputation.total_warnings > 0 && (
             <div className="warning-banner" style={{marginTop: '15px', padding: '10px', backgroundColor: '#ffebee', border: '1px solid #ffcdd2', borderRadius: '4px', color: '#c62828'}}>
                <strong>⚠️ Warnings: {user.reputation.total_warnings}</strong>
                {user.reputation.total_warnings >= 2 && <p>Warning: 3 warnings will result in account closure.</p>}
             </div>
          )}
          
          {showDepositModal && (
            <div className="modal-overlay" onClick={() => setShowDepositModal(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Deposit Money</h3>
                
                {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
                {successMessage && <div style={{ color: 'green', marginBottom: '10px' }}>{successMessage}</div>}
                
                <div className="form-group">
                  <label htmlFor="depositAmount">Amount ($)</label>
                  <input
                    type="number"
                    id="depositAmount"
                    className="input"
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(e.target.value)}
                    placeholder="Enter amount"
                    min="0.01"
                    step="0.01"
                    disabled={depositLoading}
                  />
                </div>
                <div className="modal-actions">
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowDepositModal(false);
                      setDepositAmount('');
                    }}
                    disabled={depositLoading}
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-primary"
                    onClick={handleDeposit}
                    disabled={depositLoading}
                  >
                    {depositLoading ? 'Processing...' : 'Deposit'}
                  </button>
                </div>
              </div>
            </div>
          )}
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
                  <p className="order-date">{formatDate(order.created_at || order.createdAt)}</p>
                  <div className="order-items-preview">
                    {order.items && order.items.slice(0, 2).map((item, idx) => (
                      <span key={idx} className="order-item-name">
                        {item.quantity}x {item.dish_name || item.name}
                      </span>
                    ))}
                    {order.items && order.items.length > 2 && (
                      <span className="order-item-name">+{order.items.length - 2} more</span>
                    )}
                  </div>
                  <div className="order-total-row">
                    {order.discount_amount > 0 && (
                      <span className="order-discount">Discount: -${order.discount_amount.toFixed(2)}</span>
                    )}
                    <p className="order-total">Total: ${order.total_amount?.toFixed(2) || '0.00'}</p>
                  </div>
                  <Link 
                    to={`/orders/${order.id}`} 
                    className="btn btn-secondary"
                    style={{ marginTop: '10px', fontSize: '14px', padding: '8px 16px' }}
                  >
                    Track Order
                  </Link>
                  {order.status && order.status.toLowerCase() === 'delivered' && (
                    <Link 
                      to={`/reviews/${order.id}`} 
                      className="btn btn-primary"
                      style={{ marginTop: '10px', marginLeft: '10px', fontSize: '14px', padding: '8px 16px' }}
                    >
                      Rate Order
                    </Link>
                  )}
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

        <div className="dashboard-card feedback-card">
          <h2>My Feedback</h2>
          <div className="quick-actions" style={{marginBottom: '15px'}}>
             <Link to="/compliment" className="btn btn-success" style={{marginRight: '10px'}}>Give Compliment</Link>
             <Link to="/complaint" className="btn btn-danger">File Complaint</Link>
          </div>
          
          {/* Complaints I Filed */}
          {myComplaints.length > 0 && (
            <div className="feedback-section">
              <h3>📝 Complaints I Filed</h3>
              {myComplaints.map(c => (
                <div key={c.id} className={`feedback-item complaint-${c.status}`}>
                  <div className="feedback-header">
                    <strong>{c.title}</strong>
                    <span className={`status-badge ${c.status}`}>{c.status}</span>
                  </div>
                  <p className="feedback-target">Against: {c.subject}</p>
                  {c.manager_decision && (
                    <p className="resolution-note">
                      <strong>Resolution:</strong> {c.manager_decision}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {/* Compliments I Gave */}
          {myCompliments.length > 0 && (
            <div className="feedback-section">
              <h3>🌟 Compliments I Gave</h3>
              {myCompliments.map(c => (
                <div key={c.id} className="feedback-item compliment">
                  <strong>{c.title}</strong>
                  <p className="feedback-target">To: {c.receiver}</p>
                </div>
              ))}
            </div>
          )}
          
          {myComplaints.length === 0 && myCompliments.length === 0 && (
            <p style={{color: '#7f8c8d', textAlign: 'center', marginTop: '10px'}}>No feedback submitted yet</p>
          )}
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

