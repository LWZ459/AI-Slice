import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import API_BASE_URL from '../config/api';
import './MenuBrowse.css';

// Mock dishes as fallback
const MOCK_DISHES = [
  { id: 1, name: 'Margherita Pizza', price: 12.99, is_available: true, description: 'Classic Italian pizza with fresh tomatoes, mozzarella cheese, and basil leaves on a thin crust.', average_rating: 4.8 },
  { id: 2, name: 'Pepperoni Pizza', price: 14.99, is_available: true, description: 'Traditional pepperoni pizza with spicy pepperoni slices and melted mozzarella cheese.', average_rating: 4.9 },
  { id: 3, name: 'Caesar Salad', price: 8.99, is_available: true, description: 'Fresh romaine lettuce with Caesar dressing, parmesan cheese, and croutons.', average_rating: 4.6 },
  { id: 4, name: 'Pasta Carbonara', price: 13.99, is_available: true, description: 'Creamy pasta dish with bacon, eggs, parmesan cheese, and black pepper.', average_rating: 4.7 },
  { id: 5, name: 'Chicken Burger', price: 11.99, is_available: true, description: 'Juicy grilled chicken patty with lettuce, tomato, and special sauce on a toasted bun.', average_rating: 4.5 },
  { id: 6, name: 'Chocolate Cake', price: 7.99, is_available: true, description: 'Rich and moist chocolate cake with chocolate frosting, perfect for dessert lovers.', average_rating: 4.9 }
];

const MenuBrowse = () => {
  const { addToCart } = useCart();
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [dishes, setDishes] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDishes();
    if (user) {
      fetchRecommendations();
    }
  }, [user]);

  const fetchDishes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/menu/`);
      // Use API data if available, otherwise fallback to mock data
      const apiDishes = response.data && response.data.length > 0 ? response.data : MOCK_DISHES;
      setDishes(apiDishes);
      setLoading(false);
    } catch (err) {
      // On error, use mock data as fallback
      setDishes(MOCK_DISHES);
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      // Get current time of day
      const hour = new Date().getHours();
      let timeOfDay = 'lunch';
      if (hour < 11) timeOfDay = 'morning';
      else if (hour > 16) timeOfDay = 'dinner';
      else if (hour > 21) timeOfDay = 'night';

      // We need to pass the token in header if we had one, but axios interceptors or simple header add works
      const token = localStorage.getItem('token');
      const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

      const response = await axios.get(`${API_BASE_URL}/api/menu/recommendations?time_of_day=${timeOfDay}`, config);
      setRecommendations(response.data);
    } catch (err) {
      // Fallback or just ignore recommendations error
    }
  };

  const filteredDishes = dishes.filter(dish => {
    // If no search term, show all
    if (!searchTerm) return true;
    
    const term = searchTerm.toLowerCase();
    const nameMatch = dish.name ? dish.name.toLowerCase().includes(term) : false;
    const descMatch = dish.description ? dish.description.toLowerCase().includes(term) : false;
    // Also match chef name if available
    const chefMatch = dish.chef_name ? dish.chef_name.toLowerCase().includes(term) : false;
    return nameMatch || descMatch || chefMatch;
  });

  const handleAddToCart = (dish) => {
    addToCart(dish);
  };

  if (loading && dishes.length === 0) return <div className="loading">Loading menu...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="menu-browse">
      <h1 className="page-title">Browse Menu</h1>
      
      <div className="search-section">
        <input
          type="text"
          placeholder="Search dishes..."
          className="search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {user && !searchTerm && recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>Recommended for You</h2>
          <p className="section-subtitle">Based on your taste and popular items</p>
          <div className="dishes-grid recommendations-grid">
            {recommendations.map(dish => (
              <div key={`rec-${dish.id}`} className="dish-card">
                <div className={`dish-image pattern-${dish.id % 3 + 1}`}>
                  <span className="recommendation-badge">Top Pick</span>
                </div>
                <div className="dish-content">
                  <div className="dish-header">
                    <h3 className="dish-name">{dish.name}</h3>
                    <span className="dish-price-badge">${dish.price.toFixed(2)}</span>
                  </div>
                  {/* Chef name not always available in basic dish object depending on backend */}
                  <div className="dish-rating">
                    <span>★ {dish.average_rating ? dish.average_rating.toFixed(1) : 'New'}</span>
                  </div>
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => handleAddToCart(dish)}
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {filteredDishes.length > 0 && (
        <>
          {!searchTerm && (
            <h2 className="section-title" style={{ marginTop: '2rem', marginBottom: '1rem' }}>
              All Menu Items
            </h2>
          )}
          <div className="dishes-grid">
            {filteredDishes.map((dish, index) => {
              const cardVariation = index % 2;
              const isWide = cardVariation === 1;
              
              return (
                <div 
                  key={dish.id} 
                  className={`dish-card ${isWide ? 'dish-card-wide' : ''}`}
                >
                  <div className={`dish-image pattern-${(index % 3) + 1}`}></div>
                  <div className="dish-content">
                    <div className="dish-header">
                      <h3 className="dish-name">{dish.name}</h3>
                      <span className="dish-price-badge">${dish.price.toFixed(2)}</span>
                    </div>
                    {dish.description && <p className="dish-description">{dish.description}</p>}
                    <div className="dish-rating">
                       <span>Rating: {dish.average_rating ? dish.average_rating.toFixed(1) : 'N/A'}</span>
                    </div>
                    <div className="dish-footer">
                      <button 
                        className="btn btn-primary"
                        onClick={() => handleAddToCart(dish)}
                        disabled={!dish.is_available}
                      >
                        {dish.is_available ? 'Add to Cart' : 'Unavailable'}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {!loading && filteredDishes.length === 0 && dishes.length === 0 && (
        <div className="no-results">
          <p>No dishes available at the moment. Please check back later.</p>
        </div>
      )}

      {!loading && filteredDishes.length === 0 && dishes.length > 0 && searchTerm && (
        <div className="no-results">
          <p>No dishes found matching "{searchTerm}"</p>
        </div>
      )}
    </div>
  );
};

export default MenuBrowse;
