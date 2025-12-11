import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './ManagerDashboard.css';

const ManagerDashboard = () => {
  const [pendingRegistrations] = useState([]); // Placeholder
  const [activeDeliveries, setActiveDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDeliveryBids, setSelectedDeliveryBids] = useState(null);
  const [bidsLoading, setBidsLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    fetchDeliveries();
    
    const interval = setInterval(fetchDeliveries, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchDeliveries = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/delivery/available`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActiveDeliveries(response.data);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const fetchBids = async (deliveryId) => {
    setBidsLoading(true);
    setSelectedDeliveryBids(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/delivery/${deliveryId}/bids`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedDeliveryBids({
        deliveryId,
        bids: response.data
      });
    } catch (error) {
      setActionMessage('Failed to fetch bids');
      setTimeout(() => setActionMessage(''), 3000);
    } finally {
      setBidsLoading(false);
    }
  };

  const handleAutoAssign = async (deliveryId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/delivery/${deliveryId}/auto-assign`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setActionMessage(`Order #${response.data.order_id || 'Unknown'} auto-assigned successfully`);
      setTimeout(() => setActionMessage(''), 3000);
      fetchDeliveries(); // Refresh list
      setSelectedDeliveryBids(null); // Close bids view
    } catch (error) {
      setActionMessage(error.response?.data?.detail || 'Auto-assign failed');
      setTimeout(() => setActionMessage(''), 3000);
    }
  };

  const handleManualAssign = async (deliveryId, deliveryPersonId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/delivery/${deliveryId}/assign`,
        {
          delivery_person_id: deliveryPersonId,
          justification: "Manager manual selection" // Simple justification for now
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setActionMessage('Delivery assigned successfully');
      setTimeout(() => setActionMessage(''), 3000);
      fetchDeliveries();
      setSelectedDeliveryBids(null);
    } catch (error) {
      setActionMessage(error.response?.data?.detail || 'Assignment failed');
      setTimeout(() => setActionMessage(''), 3000);
    }
  };

  return (
    <div className="manager-dashboard">
      <h1 className="dashboard-title">Manager Dashboard</h1>
      
      {actionMessage && (
        <div className="action-message">
          {actionMessage}
        </div>
      )}
      
      <div className="dashboard-grid">
        {/* Delivery Management Section */}
        <div className="dashboard-card delivery-management-card">
          <h2>Delivery Management</h2>
          <p>Orders waiting for driver assignment</p>
          
          {loading ? <p>Loading deliveries...</p> : activeDeliveries.length === 0 ? (
            <p className="empty-state">No deliveries pending assignment.</p>
          ) : (
            <div className="deliveries-list">
              {activeDeliveries.map(delivery => (
                <div key={delivery.id} className="delivery-manage-item">
                  <div className="delivery-info">
                    <h3>Order #{delivery.order_id}</h3>
                    <p><strong>Pickup:</strong> {delivery.pickup_address}</p>
                    <p><strong>Fee:</strong> ${delivery.delivery_fee.toFixed(2)}</p>
                  </div>
                  <div className="delivery-actions">
                    <button 
                      className="btn-small btn-primary"
                      onClick={() => fetchBids(delivery.id)}
                    >
                      View Bids
                    </button>
                    <button 
                      className="btn-small btn-success"
                      onClick={() => handleAutoAssign(delivery.id)}
                    >
                      Auto Assign (Lowest Bid)
                    </button>
                  </div>
                  
                  {/* Bids Dropdown/Section */}
                  {selectedDeliveryBids && selectedDeliveryBids.deliveryId === delivery.id && (
                    <div className="bids-section">
                      <h4>Current Bids</h4>
                      {bidsLoading ? <p>Loading bids...</p> : selectedDeliveryBids.bids.length === 0 ? (
                        <p>No bids placed yet.</p>
                      ) : (
                        <div className="bids-list-small">
                          {selectedDeliveryBids.bids.map(bid => (
                            <div key={bid.id} className="bid-row">
                              <span>Bidder #{bid.delivery_person_id}</span>
                              <span>${bid.bid_amount.toFixed(2)}</span>
                              <span>{bid.estimated_time}m</span>
                              <button 
                                className="btn-xs"
                                onClick={() => handleManualAssign(delivery.id, bid.delivery_person_id)}
                              >
                                Assign
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-card">
          <h2>Pending Registrations</h2>
          {pendingRegistrations.length === 0 ? (
              <p className="empty-state">No pending registrations.</p>
          ) : (
          <div className="registrations-list">
                {/* Map pending registrations here */}
                </div>
          )}
          <div style={{marginTop: '1rem'}}>
              <p className="note">Use API directly to approve users for now or check back later for full UI integration.</p>
          </div>
        </div>

        <div className="dashboard-card staff-management-card">
          <h2>Staff Overview</h2>
          <p>Manage Chefs and Delivery Personnel performance.</p>
          {/* Staff list would go here */}
        </div>
      </div>
    </div>
  );
};

export default ManagerDashboard;
