import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import './Checkout.css';

const Checkout = () => {
  const navigate = useNavigate();
  const { cart, clearCart, removeFromCart, updateQuantity } = useCart();
  const { isAuthenticated, isVIP } = useAuth();

  const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  // Only calculate discount if user is VIP and subtotal is greater than 0
  const isUserVIP = isAuthenticated() && isVIP();
  const discount = (isUserVIP && subtotal > 0) ? subtotal * 0.05 : 0;
  const total = subtotal - discount;
  const [orderStatus, setOrderStatus] = useState(null);

  const handleCheckout = () => {
    // TODO: Process order
    clearCart();
    setOrderStatus('success');
    setTimeout(() => {
      navigate('/customer');
    }, 2000);
  };

  if (orderStatus === 'success') {
    return (
      <div className="checkout-success">
        <div className="success-card">
          <div className="success-icon"></div>
          <h2>Order Placed Successfully</h2>
          <p>Your order has been confirmed and will be prepared shortly.</p>
          <p className="estimated-time">Estimated delivery time: 30-45 minutes</p>
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
          <h2>Payment</h2>
          {isUserVIP && (
            <div style={{ marginBottom: '20px' }}>
              <span className="vip-badge">VIP Customer</span>
            </div>
          )}

          <button 
            className="btn btn-primary btn-large"
            onClick={handleCheckout}
          >
            Confirm Order
          </button>
        </div>
      </div>
    </div>
  );
};

export default Checkout;

