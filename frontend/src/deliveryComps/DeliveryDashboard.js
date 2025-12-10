import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './DeliveryDashboard.css';

const DeliveryDashboard = () => {
  const [availableDeliveries, setAvailableDeliveries] = useState([]);
  const [myDeliveries, setMyDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const [availableRes, myRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/delivery/available`, config),
        axios.get(`${API_BASE_URL}/api/delivery/my-deliveries`, config)
      ]);

      setAvailableDeliveries(availableRes.data);
      setMyDeliveries(myRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching delivery data:', error);
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (deliveryId, newStatus) => {
      // Logic to update status would go here
      alert(`Update status for ${deliveryId} to ${newStatus}`);
  };

  return (
    <div className="delivery-dashboard">
      <h1 className="dashboard-title">Delivery Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Available Orders for Bidding</h2>
          {loading ? <p>Loading...</p> : availableDeliveries.length === 0 ? (
             <p className="empty-state">No orders available for bidding right now.</p>
          ) : (
          <div className="orders-list">
              {availableDeliveries.map(delivery => (
                <div key={delivery.id} className="order-bid-card">
                <div className="order-details">
                    <h3>Delivery #{delivery.id}</h3>
                    <p>Pickup: {delivery.pickup_address}</p>
                    <p>Dropoff: {delivery.delivery_address}</p>
                    <p className="base-price">Est. Pay: ${delivery.estimated_pay?.toFixed(2) || '---'}</p>
                </div>
                <Link to="/bidding" className="btn btn-primary">Place Bid</Link>
              </div>
            ))}
          </div>
          )}
        </div>

        <div className="dashboard-card">
          <h2>My Active Deliveries</h2>
          {myDeliveries.length === 0 ? (
            <p className="empty-state">No active deliveries</p>
          ) : (
            <div className="deliveries-list">
              {myDeliveries.map(delivery => (
                <div key={delivery.id} className="delivery-card">
                  <h3>Order #{delivery.order_id}</h3>
                  <p>Address: {delivery.delivery_address}</p>
                  <div className="delivery-status">
                    <span className={`status-badge ${delivery.status?.toLowerCase().replace(' ', '-')}`}>
                      {delivery.status}
                    </span>
                  </div>
                  <button 
                    className="btn btn-success"
                    onClick={() => handleUpdateStatus(delivery.id, 'delivered')}
                  >
                    Update Status
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DeliveryDashboard;
