import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './DeliveryDashboard.css';

const DeliveryDashboard = () => {
  const [availableOrders] = useState([
    { id: 2001, distance: '2.5 km', address: '123 Main St', items: 3, basePrice: 15.00 },
    { id: 2002, distance: '5.0 km', address: '456 Oak Ave', items: 2, basePrice: 20.00 }
  ]);

  const [myBids] = useState([
    { orderId: 2001, bidAmount: 12.00, status: 'Pending', time: '10:25 AM' },
    { orderId: 2003, bidAmount: 18.00, status: 'Won', time: '09:45 AM' }
  ]);

  const [activeDeliveries] = useState([
    { id: 2003, address: '789 Pine Rd', status: 'In Transit', progress: 60 }
  ]);

  return (
    <div className="delivery-dashboard">
      <h1 className="dashboard-title">Delivery Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Available Orders for Bidding</h2>
          <div className="orders-list">
            {availableOrders.map(order => (
              <div key={order.id} className="order-bid-card">
                <div className="order-details">
                  <h3>Order #{order.id}</h3>
                  <p>Address: {order.address}</p>
                  <p>Distance: {order.distance}</p>
                  <p>Items: {order.items}</p>
                  <p className="base-price">Base Price: ${order.basePrice.toFixed(2)}</p>
                </div>
                <Link to="/bidding" className="btn btn-primary">Place Bid</Link>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <h2>My Bids</h2>
          <div className="bids-list">
            {myBids.map((bid, idx) => (
              <div key={idx} className="bid-item">
                <div className="bid-header">
                  <span>Order #{bid.orderId}</span>
                  <span className={`bid-status ${bid.status.toLowerCase()}`}>
                    {bid.status}
                  </span>
                </div>
                <div className="bid-details">
                  <p>Bid Amount: <strong>${bid.bidAmount.toFixed(2)}</strong></p>
                  <p className="bid-time">{bid.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <h2>Active Deliveries</h2>
          {activeDeliveries.length === 0 ? (
            <p className="empty-state">No active deliveries</p>
          ) : (
            <div className="deliveries-list">
              {activeDeliveries.map(delivery => (
                <div key={delivery.id} className="delivery-card">
                  <h3>Order #{delivery.id}</h3>
                  <p>Address: {delivery.address}</p>
                  <div className="delivery-status">
                    <span className={`status-badge ${delivery.status.toLowerCase().replace(' ', '-')}`}>
                      {delivery.status}
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${delivery.progress}%` }}
                    ></div>
                  </div>
                  <button className="btn btn-success">Update Status</button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-card stats-card">
          <h2>Today's Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">5</div>
              <div className="stat-label">Deliveries</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">$85.00</div>
              <div className="stat-label">Earnings</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">4.9</div>
              <div className="stat-label">Rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeliveryDashboard;

