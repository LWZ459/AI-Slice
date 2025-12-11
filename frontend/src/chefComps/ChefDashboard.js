import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './ChefDashboard.css';

const ChefDashboard = () => {
  const [dishes, setDishes] = useState([]);
  const [activeOrders, setActiveOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ordersLoading, setOrdersLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    fetchMenu();
    fetchOrders();

    // Poll for new orders every 10 seconds
    const interval = setInterval(fetchOrders, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchMenu = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/menu/`);
      setDishes(response.data);
      setLoading(false);
    } catch (error) {
      // Silently fail
      setLoading(false);
    }
  };

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/chef/orders`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActiveOrders(response.data);
      setOrdersLoading(false);
    } catch (error) {
      // Silently fail
      setOrdersLoading(false);
    }
  };

  const handleUpdateOrderStatus = async (orderId, currentStatus) => {
    let newStatus = '';
    if (currentStatus === 'placed') newStatus = 'preparing';
    else if (currentStatus === 'preparing') newStatus = 'ready_for_delivery';
    else return; // Should not happen

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/api/chef/orders/${orderId}/status`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Refresh orders immediately
      fetchOrders();
      setActionMessage(`Order updated to ${newStatus.replace(/_/g, ' ')}`);
      setTimeout(() => setActionMessage(''), 3000);
    } catch (error) {
      setActionMessage(error.response?.data?.detail || 'Failed to update status');
      setTimeout(() => setActionMessage(''), 3000);
    }
  };

  const handleToggleAvailability = async (dishId, currentStatus) => {
    try {
      // Optimistic update
      setDishes(dishes.map(d => d.id === dishId ? { ...d, is_available: !currentStatus } : d));
      setActionMessage("Dish availability updated");
      setTimeout(() => setActionMessage(''), 3000);
    } catch (error) {
      setActionMessage("Failed to update status");
      setTimeout(() => setActionMessage(''), 3000);
    }
  };

  const getNextStatusLabel = (status) => {
    if (status === 'placed') return 'Start Cooking';
    if (status === 'preparing') return 'Mark Ready for Delivery';
    return '';
  };

  return (
    <div className="chef-dashboard">
      <h1 className="dashboard-title">Chef Dashboard</h1>
      
      {actionMessage && (
        <div style={{
          padding: '10px 20px',
          marginBottom: '20px',
          backgroundColor: '#34495e',
          color: 'white',
          borderRadius: '4px',
          textAlign: 'center'
        }}>
          {actionMessage}
        </div>
      )}
      
      <div className="dashboard-grid">
        
        {/* Active Orders Section */}
        <div className="dashboard-card orders-card">
          <h2>Active Orders</h2>
          {ordersLoading ? <p>Loading orders...</p> : activeOrders.length === 0 ? (
            <p className="empty-state">No active orders right now.</p>
          ) : (
            <div className="orders-list">
              {activeOrders.map(order => (
                <div key={order.id} className="order-card">
                  <div className="order-header">
                    <span className="order-id">Order #{order.id}</span>
                    <span className={`order-status ${order.status.toLowerCase()}`}>
                      {order.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  
                  <div className="order-items">
                    {order.items.map((item, idx) => (
                      <p key={idx}>
                        <strong>{item.quantity}x</strong> {item.dish_name}
                        {item.special_instructions && (
                          <span className="special-instructions">
                            <br/>Note: {item.special_instructions}
                          </span>
                        )}
                      </p>
                    ))}
                  </div>
                  
                  <div className="order-footer">
                    <span className="order-time">
                      {new Date(order.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>
                    <button 
                      className="btn-small btn-primary"
                      onClick={() => handleUpdateOrderStatus(order.id, order.status.toLowerCase())}
                    >
                      {getNextStatusLabel(order.status.toLowerCase())}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Menu Management Section */}
        <div className="dashboard-card menu-card">
          <h2>My Menu</h2>
          <button className="btn btn-success" style={{ marginBottom: '20px' }}>Add New Dish</button>
          
          {loading ? <p>Loading menu...</p> : (
          <div className="dishes-list">
            {dishes.map(dish => (
              <div key={dish.id} className="dish-item">
                <div className="dish-info">
                  <h3>{dish.name}</h3>
                  <p>${dish.price.toFixed(2)}</p>
                    <span className={`status-badge ${dish.is_available ? 'available' : 'unavailable'}`}>
                      {dish.is_available ? 'Available' : 'Unavailable'}
                  </span>
                    <span className="orders-count">{dish.orders_count || 0} orders</span>
                </div>
                <div className="dish-actions">
                  <button className="btn-small">Edit</button>
                    <button 
                      className="btn-small btn-secondary"
                      onClick={() => handleToggleAvailability(dish.id, dish.is_available)}
                    >
                      {dish.is_available ? 'Mark Unavailable' : 'Mark Available'}
                  </button>
                </div>
              </div>
            ))}
          </div>
          )}
        </div>

        {/* Stats Section */}
        <div className="dashboard-card stats-card">
          <h2>Performance Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{activeOrders.length}</div>
              <div className="stat-label">Active Orders</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">--</div>
              <div className="stat-label">Total Completed</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">--</div>
              <div className="stat-label">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChefDashboard;
