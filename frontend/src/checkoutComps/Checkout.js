import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import API_BASE_URL from '../config/api';
import './Checkout.css';

const Checkout = () => {
  const navigate = useNavigate();
  const { cart, clearCart, removeFromCart, updateQuantity } = useCart();
  const { isAuthenticated, isVIP } = useAuth();
  
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [orderStatus, setOrderStatus] = useState(null);

  const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  // Only calculate discount if user is VIP and subtotal is greater than 0
  const isUserVIP = isAuthenticated() && isVIP();
  const discount = (isUserVIP && subtotal > 0) ? subtotal * 0.05 : 0;
  // Note: Backend also handles discounts, this is just for display estimate
  const total = subtotal - discount;

  const handleCheckout = async () => {
    // Address check removed
    
    setLoading(true);
    setError(null);

    try {
      const orderItems = cart.map(item => ({
        dish_id: item.id,
        quantity: item.quantity
      }));

      const payload = {
        items: orderItems,
        delivery_address: address || "Default Address", // Provide fallback if empty
        delivery_instructions: "" // Optional
      };

      const token = localStorage.getItem('token');
      const config = {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };

      await axios.post(`${API_BASE_URL}/api/orders/`, payload, config);
      
      clearCart();
      setOrderStatus('success');
      setTimeout(() => {
        navigate('/customer');
      }, 3000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Order failed. Please check your wallet balance.');
    } finally {
      setLoading(false);
    }
  };

  if (orderStatus === 'success') {
    return (
      <div className="checkout-success">
        <div className="success-card">
          <div className="success-icon">✓</div>
          <h2>Order Placed Successfully</h2>
          <p>Your order has been confirmed and will be prepared shortly.</p>
          <p className="estimated-time">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="checkout">
        <h1 className="page-title">Checkout</h1>
        <div className="checkout-card">
          <p style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
            Your cart is empty. <Link to="/menu" style={{ color: '#2c3e50', textDecoration: 'underline' }}>Browse menu</Link> to add items.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="checkout">
      <h1 className="page-title">Checkout</h1>
      
      <div className="checkout-grid">
        <div className="checkout-card">
          <h2>Order Summary</h2>
          <div className="cart-items">
            {cart.map(item => (
              <div key={item.id} className="checkout-item">
                <div className="item-info">
                  <span className="item-name">{item.name}</span>
                  <div className="item-controls">
                    <div className="quantity-controls">
                      <button 
                        className="quantity-btn-small"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        aria-label="Decrease quantity"
                      >
                        −
                      </button>
                      <span className="item-quantity">Qty: {item.quantity}</span>
                      <button 
                        className="quantity-btn-small"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        aria-label="Increase quantity"
                      >
                        +
                      </button>
                    </div>
                    <button 
                      className="remove-btn"
                      onClick={() => removeFromCart(item.id)}
                      aria-label="Remove item"
                      title="Remove from cart"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <span className="item-price">${(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>
          
          <div className="checkout-summary">
            <div className="summary-row">
              <span>Subtotal:</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            {isUserVIP && discount > 0 && (
              <div className="summary-row vip-discount">
                <span>VIP Discount (5%):</span>
                <span>-${discount.toFixed(2)}</span>
              </div>
            )}
            <div className="summary-row total">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div className="checkout-card">
          <h2>Delivery Details</h2>
          {isUserVIP && (
            <div style={{ marginBottom: '20px' }}>
              <span className="vip-badge">VIP Customer</span>
              <p className="vip-note">You get 5% off this order!</p>
            </div>
          )}

          <div className="form-group" style={{ display: 'none' }}>
            <label htmlFor="address">Delivery Address</label>
            <textarea
              id="address"
              className="input"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Enter your full delivery address"
              rows="3"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          {isAuthenticated() ? (
            <>
              <button 
                className="btn btn-primary btn-large"
                onClick={handleCheckout}
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Confirm Order'}
              </button>
              <p className="payment-note">Payment will be deducted from your wallet balance.</p>
            </>
          ) : (
            <div className="guest-checkout-prompt">
              <p>Please sign in to complete your order.</p>
              <Link to="/signin" className="btn btn-primary btn-large">
                Sign In to Checkout
              </Link>
              <p className="payment-note">Don't have an account? <Link to="/signup">Sign up here</Link></p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Checkout;
