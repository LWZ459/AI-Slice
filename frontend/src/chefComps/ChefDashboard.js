import React, { useState } from 'react';
import './ChefDashboard.css';

const ChefDashboard = () => {
  const [dishes] = useState([
    { id: 1, name: 'Margherita Pizza', price: 12.99, available: true, orders: 5 },
    { id: 2, name: 'Pepperoni Pizza', price: 14.99, available: true, orders: 3 },
    { id: 3, name: 'Caesar Salad', price: 8.99, available: false, orders: 0 }
  ]);

  const [orders] = useState([
    { id: 1001, items: ['Margherita Pizza x2'], total: 25.98, status: 'Placed', time: '10:30 AM' },
    { id: 1002, items: ['Pepperoni Pizza'], total: 14.99, status: 'Preparing', time: '10:15 AM' }
  ]);

  return (
    <div className="chef-dashboard">
      <h1 className="dashboard-title">Chef Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card menu-card">
          <h2>My Menu</h2>
          <button className="btn btn-success" style={{ marginBottom: '20px' }}>Add New Dish</button>
          <div className="dishes-list">
            {dishes.map(dish => (
              <div key={dish.id} className="dish-item">
                <div className="dish-info">
                  <h3>{dish.name}</h3>
                  <p>${dish.price.toFixed(2)}</p>
                  <span className={`status-badge ${dish.available ? 'available' : 'unavailable'}`}>
                    {dish.available ? 'Available' : 'Unavailable'}
                  </span>
                  <span className="orders-count">{dish.orders} orders</span>
                </div>
                <div className="dish-actions">
                  <button className="btn-small">Edit</button>
                  <button className="btn-small btn-secondary">
                    {dish.available ? 'Mark Unavailable' : 'Mark Available'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card orders-card">
          <h2>Kitchen Orders</h2>
          <div className="orders-list">
            {orders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <span className="order-id">Order #{order.id}</span>
                  <span className={`order-status ${order.status.toLowerCase()}`}>
                    {order.status}
                  </span>
                </div>
                <div className="order-items">
                  {order.items.map((item, idx) => (
                    <p key={idx}>{item}</p>
                  ))}
                </div>
                <div className="order-footer">
                  <span className="order-time">{order.time}</span>
                  <span className="order-total">${order.total.toFixed(2)}</span>
                </div>
                <button className="btn btn-primary">Update Status</button>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card stats-card">
          <h2>Today's Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">8</div>
              <div className="stat-label">Total Orders</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">$125.50</div>
              <div className="stat-label">Revenue</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">4.8</div>
              <div className="stat-label">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChefDashboard;

