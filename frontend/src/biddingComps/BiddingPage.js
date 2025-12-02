import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './BiddingPage.css';

const BiddingPage = () => {
  const navigate = useNavigate();
  const [selectedOrder] = useState({
    id: 2001,
    distance: '2.5 km',
    address: '123 Main St',
    items: ['Margherita Pizza x2', 'Caesar Salad'],
    basePrice: 15.00
  });

  const [bidAmount, setBidAmount] = useState('');
  const [bids] = useState([
    { deliveryPerson: 'Mike Johnson', amount: 12.00, time: '10:25 AM' },
    { deliveryPerson: 'Sarah Williams', amount: 15.00, time: '10:20 AM' }
  ]);

  const handleSubmitBid = (e) => {
    e.preventDefault();
    const amount = parseFloat(bidAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('Please enter a valid bid amount');
      return;
    }
    // TODO: Submit bid to backend
    alert(`Bid of $${amount.toFixed(2)} submitted successfully!`);
    navigate('/delivery');
  };

  return (
    <div className="bidding-page">
      <h1 className="page-title">Place Delivery Bid</h1>
      
      <div className="bidding-grid">
        <div className="bidding-card">
          <h2>Order Details</h2>
          <div className="order-info">
            <div className="info-row">
              <span className="info-label">Order ID:</span>
              <span className="info-value">#{selectedOrder.id}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Distance:</span>
              <span className="info-value">{selectedOrder.distance}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Address:</span>
              <span className="info-value">{selectedOrder.address}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Items:</span>
              <div className="info-value">
                {selectedOrder.items.map((item, idx) => (
                  <div key={idx}>{item}</div>
                ))}
              </div>
            </div>
            <div className="info-row">
              <span className="info-label">Base Price:</span>
              <span className="info-value base-price">${selectedOrder.basePrice.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div className="bidding-card">
          <h2>Place Your Bid</h2>
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
              <p className="form-hint">Enter an amount lower than base price to increase your chances</p>
            </div>
            <button type="submit" className="btn btn-primary btn-large">Submit Bid</button>
          </form>
        </div>

        <div className="bidding-card">
          <h2>Current Bids</h2>
          <div className="bids-list">
            {bids.length === 0 ? (
              <p className="no-bids">No bids yet. Be the first!</p>
            ) : (
              <>
                {bids.map((bid, idx) => (
                  <div key={idx} className="bid-item">
                    <div className="bid-person">{bid.deliveryPerson}</div>
                    <div className="bid-details">
                      <span className="bid-amount">${bid.amount.toFixed(2)}</span>
                      <span className="bid-time">{bid.time}</span>
                    </div>
                  </div>
                ))}
                <div className="bids-note">
                  <p>Lowest bidder wins automatically, unless manager overrides</p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BiddingPage;

