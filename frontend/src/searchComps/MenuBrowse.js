import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import './MenuBrowse.css';

const MenuBrowse = () => {
  const { addToCart } = useCart();
  const [searchTerm, setSearchTerm] = useState('');
  const [dishes] = useState([
    { id: 1, name: 'Margherita Pizza', chef: 'Chef Mario', price: 12.99, rating: 4.8, available: true },
    { id: 2, name: 'Pepperoni Pizza', chef: 'Chef Mario', price: 14.99, rating: 4.9, available: true },
    { id: 3, name: 'Caesar Salad', chef: 'Chef Alice', price: 8.99, rating: 4.6, available: true },
    { id: 4, name: 'Pasta Carbonara', chef: 'Chef Luigi', price: 13.99, rating: 4.7, available: true },
    { id: 5, name: 'Chicken Burger', chef: 'Chef Alice', price: 11.99, rating: 4.5, available: true },
    { id: 6, name: 'Chocolate Cake', chef: 'Chef Luigi', price: 7.99, rating: 4.9, available: true }
  ]);

  const filteredDishes = dishes.filter(dish =>
    dish.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dish.chef.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddToCart = (dish) => {
    addToCart(dish);
  };

  return (
    <div className="menu-browse">
      <h1 className="page-title">Browse Menu</h1>
      
      <div className="search-section">
        <input
          type="text"
          placeholder="Search dishes or chefs..."
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
                <p className="dish-chef">by {dish.chef}</p>
                <div className="dish-rating">
                  <span>Rating: {dish.rating}</span>
                </div>
                <div className="dish-footer">
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
    </div>
  );
};

export default MenuBrowse;

