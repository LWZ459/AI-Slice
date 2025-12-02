import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import './HomePage.css';

const HomePage = () => {
  const { addToCart } = useCart();
  const [searchTerm, setSearchTerm] = useState('');
  const [quantities, setQuantities] = useState({});
  const [dishes] = useState([
    { id: 1, name: 'Margherita Pizza', chef: 'Chef Mario', price: 12.99, rating: 4.8, available: true, description: 'Classic Italian pizza with fresh tomatoes, mozzarella cheese, and basil leaves on a thin crust.' },
    { id: 2, name: 'Pepperoni Pizza', chef: 'Chef Mario', price: 14.99, rating: 4.9, available: true, description: 'Traditional pepperoni pizza with spicy pepperoni slices and melted mozzarella cheese.' },
    { id: 3, name: 'Caesar Salad', chef: 'Chef Alice', price: 8.99, rating: 4.6, available: true, description: 'Fresh romaine lettuce with Caesar dressing, parmesan cheese, and croutons.' },
    { id: 4, name: 'Pasta Carbonara', chef: 'Chef Luigi', price: 13.99, rating: 4.7, available: true, description: 'Creamy pasta dish with bacon, eggs, parmesan cheese, and black pepper.' },
    { id: 5, name: 'Chicken Burger', chef: 'Chef Alice', price: 11.99, rating: 4.5, available: true, description: 'Juicy grilled chicken patty with lettuce, tomato, and special sauce on a toasted bun.' },
    { id: 6, name: 'Chocolate Cake', chef: 'Chef Luigi', price: 7.99, rating: 4.9, available: true, description: 'Rich and moist chocolate cake with chocolate frosting, perfect for dessert lovers.' }
  ]);

  const filteredDishes = dishes.filter(dish =>
    dish.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleQuantityChange = (dishId, value) => {
    const numValue = parseInt(value) || 1;
    if (numValue < 1) return;
    setQuantities(prev => ({ ...prev, [dishId]: numValue }));
  };

  const handleQuantityIncrement = (dishId) => {
    setQuantities(prev => ({ ...prev, [dishId]: (prev[dishId] || 1) + 1 }));
  };

  const handleQuantityDecrement = (dishId) => {
    setQuantities(prev => {
      const current = prev[dishId] || 1;
      if (current <= 1) return prev;
      return { ...prev, [dishId]: current - 1 };
    });
  };

  const handleAddToCart = (dish) => {
    const quantity = quantities[dish.id] || 1;
    for (let i = 0; i < quantity; i++) {
      addToCart(dish);
    }
    setQuantities(prev => ({ ...prev, [dish.id]: 1 }));
  };

  return (
    <div className="homepage">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">AI Slice</h1>
          <p className="hero-subtitle">Fresh Pizzas Made with Love • Fast Delivery • Order Now!</p>
          <div className="hero-buttons">
            <Link to="/signup" className="btn btn-primary">Get Started</Link>
            <Link to="/signin" className="btn btn-secondary">Sign In</Link>
          </div>
        </div>
      </section>

      <section className="menu-section">
        <h2 className="section-title">Our Menu</h2>
        <div className="search-section">
          <input
            type="text"
            placeholder="Search dishes..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
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
                  {dish.description && (
                    <p className="dish-description">{dish.description}</p>
                  )}
                  <div className="dish-rating">
                    <span>Rating: {dish.rating}</span>
                  </div>
                  <div className="dish-footer">
                    <div className="quantity-selector">
                      <button 
                        className="quantity-btn"
                        onClick={() => handleQuantityDecrement(dish.id)}
                        disabled={!dish.available || (quantities[dish.id] || 1) <= 1}
                      >
                        −
                      </button>
                      <input
                        type="number"
                        className="quantity-input"
                        value={quantities[dish.id] || 1}
                        onChange={(e) => handleQuantityChange(dish.id, e.target.value)}
                        min="1"
                        disabled={!dish.available}
                      />
                      <button 
                        className="quantity-btn"
                        onClick={() => handleQuantityIncrement(dish.id)}
                        disabled={!dish.available}
                      >
                        +
                      </button>
                    </div>
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleAddToCart(dish)}
                      disabled={!dish.available}
                    >
                      {dish.available ? 'Add to Cart' : 'Unavailable'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        {filteredDishes.length === 0 && (
          <div className="no-results">
            <p>No dishes found matching "{searchTerm}"</p>
          </div>
        )}
      </section>
    </div>
  );
};

export default HomePage;

