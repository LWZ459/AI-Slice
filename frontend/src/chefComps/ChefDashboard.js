import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './ChefDashboard.css';

const ChefDashboard = () => {
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(true);

  // Note: Backend might not have direct endpoints for "Chef's Dishes" yet if generic menu endpoint is used
  // We'll use menu endpoint for now
  useEffect(() => {
    fetchMenu();
  }, []);

  const fetchMenu = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/menu/`);
      setDishes(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch menu:', error);
      setLoading(false);
    }
  };

  const handleToggleAvailability = async (dishId, currentStatus) => {
    // This requires an update endpoint in backend
    // Assuming PUT /api/menu/{id} exists
    try {
      // Optimistic update
      setDishes(dishes.map(d => d.id === dishId ? { ...d, is_available: !currentStatus } : d));
      
      // In a real app we would call:
      // await axios.put(`${API_BASE_URL}/api/menu/${dishId}`, { is_available: !currentStatus });
      alert("Feature coming soon: Update Dish Availability");
    } catch (error) {
      console.error(error);
      alert("Failed to update status");
    }
  };

  return (
    <div className="chef-dashboard">
      <h1 className="dashboard-title">Chef Dashboard</h1>
      
      <div className="dashboard-grid">
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

        <div className="dashboard-card stats-card">
          <h2>Performance Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">--</div>
              <div className="stat-label">Total Orders</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">--</div>
              <div className="stat-label">Avg Rating</div>
            </div>
          </div>
          <p className="note">Stats feature integration in progress.</p>
        </div>
      </div>
    </div>
  );
};

export default ChefDashboard;
