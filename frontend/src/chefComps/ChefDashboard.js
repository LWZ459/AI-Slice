import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './ChefDashboard.css';

const ChefDashboard = () => {
  const [dishes, setDishes] = useState([]);
  const [activeOrders, setActiveOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ordersLoading, setOrdersLoading] = useState(true);
  const [stats, setStats] = useState({
    active_orders: 0,
    total_dishes: 0,
    total_completed: 0,
    average_rating: 0
  });
  const [actionMessage, setActionMessage] = useState('');
  
  // Menu Management State
  const [categories, setCategories] = useState([]);
  const [showDishModal, setShowDishModal] = useState(false);
  const [editingDish, setEditingDish] = useState(null);
  const [dishForm, setDishForm] = useState({
    name: '',
    description: '',
    price: '',
    category_id: '',
    image_url: '',
    tags: '',
    is_special: false
  });

  useEffect(() => {
    fetchMenu();
    fetchOrders();
    fetchCategories();
    fetchStats();

    // Poll for new orders every 10 seconds
    const interval = setInterval(() => {
      fetchOrders();
      fetchStats();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/chef/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error("Failed to fetch stats", error);
    }
  };

  const fetchMenu = async () => {
    try {
      // Need to filter for *my* dishes ideally, but currently GET /api/menu/ returns all available.
      // However, the Chef dashboard usually implies managing *their* dishes. 
      // The backend GET /api/menu/ supports chef_id filter.
      // For now, we'll fetch all and maybe the backend filters or we see all.
      // A better approach if the API supports it is fetching "my dishes".
      // Let's assume fetching all is fine for now, or we can filter client side if we knew our ID.
      // Actually, standard practice: chefs manage their own menu. 
      // Let's fetch with ?chef_id=ME if possible, but we don't have our ID easily.
      // Let's just fetch all.
      const response = await axios.get(`${API_BASE_URL}/api/menu/`);
      setDishes(response.data);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };
  
  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/menu/categories/`);
      setCategories(response.data);
    } catch (error) {}
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
      setOrdersLoading(false);
    }
  };

  const handleUpdateOrderStatus = async (orderId, currentStatus) => {
    let newStatus = '';
    if (currentStatus === 'placed') newStatus = 'preparing';
    else if (currentStatus === 'preparing') newStatus = 'ready_for_delivery';
    else return;

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/api/chef/orders/${orderId}/status`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      fetchOrders();
      showMessage(`Order updated to ${newStatus.replace(/_/g, ' ')}`);
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to update status', 'error');
    }
  };

  const handleToggleAvailability = async (dishId, currentStatus) => {
    try {
      const token = localStorage.getItem('token');
      // If we just want to toggle availability, we might need a specific endpoint or use PUT.
      // The PUT endpoint expects a full DishUpdate object. 
      // Using DELETE endpoint which marks as unavailable? Or assume PUT supports partial.
      // Let's use PUT with just is_available field if backend supports partial (it usually does with exclude_unset).
      // Or we can use the "Delete" endpoint for removing/hiding.
      
      // Since the backend 'update_dish' uses 'exclude_unset=True', we can send just the field we want.
      await axios.put(
        `${API_BASE_URL}/api/menu/${dishId}`,
        { is_available: !currentStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Refresh menu
      fetchMenu();
      showMessage("Dish availability updated");
    } catch (error) {
      showMessage("Failed to update status", 'error');
    }
  };
  
  const handleSaveDish = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const payload = {
        ...dishForm,
        price: parseFloat(dishForm.price),
        category_id: parseInt(dishForm.category_id)
      };

      if (editingDish) {
        await axios.put(
          `${API_BASE_URL}/api/menu/${editingDish.id}`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        showMessage("Dish updated successfully");
      } else {
        await axios.post(
          `${API_BASE_URL}/api/menu/`,
          payload,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        showMessage("Dish created successfully");
      }
      
      closeModal();
      fetchMenu();
    } catch (error) {
      showMessage(error.response?.data?.detail || "Failed to save dish", 'error');
    }
  };
  
  const handleDeleteDish = async (dishId) => {
      if (!window.confirm("Are you sure you want to delete this dish?")) return;
      try {
          const token = localStorage.getItem('token');
          await axios.delete(`${API_BASE_URL}/api/menu/${dishId}`, {
              headers: { Authorization: `Bearer ${token}` }
          });
          showMessage("Dish deleted");
          fetchMenu();
      } catch (error) {
          showMessage("Failed to delete dish", 'error');
      }
  };

  const openAddModal = () => {
    setEditingDish(null);
    setDishForm({
      name: '',
      description: '',
      price: '',
      category_id: categories.length > 0 ? categories[0].id : '',
      image_url: '',
      tags: '',
      is_special: false
    });
    setShowDishModal(true);
  };

  const openEditModal = (dish) => {
    setEditingDish(dish);
    setDishForm({
      name: dish.name,
      description: dish.description || '',
      price: dish.price,
      category_id: dish.category_id || '',
      image_url: dish.image_url || '',
      tags: dish.tags || '',
      is_special: dish.is_special || false
    });
    setShowDishModal(true);
  };

  const closeModal = () => {
    setShowDishModal(false);
    setEditingDish(null);
  };

  const showMessage = (msg, type = 'success') => {
    setActionMessage(msg);
    setTimeout(() => setActionMessage(''), 3000);
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
        <div className="action-message">
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
          <div className="card-header-row">
            <h2>My Menu</h2>
            <button className="btn btn-success" onClick={openAddModal}>Add New Dish</button>
          </div>
          
          {loading ? <p>Loading menu...</p> : (
          <div className="dishes-list">
            {dishes.map(dish => (
              <div key={dish.id} className="dish-item">
                <div className="dish-info">
                  <h3>{dish.name} {dish.is_special && <span className="badge badge-warning">Special</span>}</h3>
                  <p>${dish.price.toFixed(2)}</p>
                    <span className={`status-badge ${dish.is_available ? 'available' : 'unavailable'}`}>
                      {dish.is_available ? 'Available' : 'Unavailable'}
                  </span>
                    <span className="orders-count">{dish.orders_count || 0} orders</span>
                </div>
                <div className="dish-actions">
                  <button className="btn-small" onClick={() => openEditModal(dish)}>Edit</button>
                  <button 
                      className="btn-small btn-secondary"
                      onClick={() => handleToggleAvailability(dish.id, dish.is_available)}
                  >
                      {dish.is_available ? 'Disable' : 'Enable'}
                  </button>
                  <button className="btn-small btn-danger" onClick={() => handleDeleteDish(dish.id)}>Delete</button>
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
              <div className="stat-value">{stats.active_orders}</div>
              <div className="stat-label">Active Orders</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.total_dishes}</div>
              <div className="stat-label">Total Dishes</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.total_completed}</div>
              <div className="stat-label">Total Completed</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.average_rating ? stats.average_rating.toFixed(1) : 'N/A'}</div>
              <div className="stat-label">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Dish Modal */}
      {showDishModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>{editingDish ? 'Edit Dish' : 'Add New Dish'}</h3>
            <form onSubmit={handleSaveDish}>
              <div className="form-group">
                <label>Name</label>
                <input 
                  type="text" 
                  value={dishForm.name} 
                  onChange={e => setDishForm({...dishForm, name: e.target.value})} 
                  required 
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  value={dishForm.description} 
                  onChange={e => setDishForm({...dishForm, description: e.target.value})} 
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Price ($)</label>
                  <input 
                    type="number" 
                    step="0.01" 
                    value={dishForm.price} 
                    onChange={e => setDishForm({...dishForm, price: e.target.value})} 
                    required 
                  />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select 
                    value={dishForm.category_id} 
                    onChange={e => setDishForm({...dishForm, category_id: e.target.value})}
                    required
                  >
                    <option value="">Select Category</option>
                    {categories.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Image URL</label>
                <input 
                  type="text" 
                  value={dishForm.image_url} 
                  onChange={e => setDishForm({...dishForm, image_url: e.target.value})} 
                  placeholder="https://example.com/image.jpg"
                />
              </div>
              <div className="form-group">
                <label>Tags (comma separated)</label>
                <input 
                  type="text" 
                  value={dishForm.tags} 
                  onChange={e => setDishForm({...dishForm, tags: e.target.value})} 
                  placeholder="spicy, vegan, italian"
                />
              </div>
              <div className="form-group checkbox-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={dishForm.is_special} 
                    onChange={e => setDishForm({...dishForm, is_special: e.target.checked})} 
                  />
                  VIP Special?
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn-success">{editingDish ? 'Update Dish' : 'Create Dish'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChefDashboard;
