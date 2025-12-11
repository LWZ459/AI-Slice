import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { getTotalQuantity } = useCart();
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const cartQuantity = getTotalQuantity();

  const handleLinkClick = () => {
    // Scroll to top when clicking any navbar link
    window.scrollTo(0, 0);
    if (document.documentElement) {
      document.documentElement.scrollTop = 0;
    }
    if (document.body) {
      document.body.scrollTop = 0;
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    handleLinkClick();
  };

  const getDashboardRoute = () => {
    if (!user) return '/customer';
    const routes = {
      customer: '/customer',
      vip: '/vip',
      chef: '/chef',
      delivery: '/delivery',
      manager: '/manager'
    };
    return routes[user.user_type] || '/customer';
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={handleLinkClick}>
          <span className="logo-text">AI Slice</span>
        </Link>
        <ul className="navbar-menu">
          <li><Link to="/" className="navbar-link" onClick={handleLinkClick}>Home</Link></li>
          <li><Link to="/menu" className="navbar-link" onClick={handleLinkClick}>Menu</Link></li>
          <li>
            <Link to="/checkout" className="navbar-link cart-link" onClick={handleLinkClick}>
              <span className="cart-icon">Cart</span>
              {cartQuantity > 0 && (
                <span className="cart-badge">{cartQuantity}</span>
              )}
            </Link>
          </li>
          {isAuthenticated() ? (
            <>
              <li>
                <Link to={getDashboardRoute()} className="navbar-link" onClick={handleLinkClick}>
                  {user?.name || 'Dashboard'}
                </Link>
              </li>
              <li>
                <button onClick={handleLogout} className="navbar-link btn-logout">
                  Logout
                </button>
              </li>
            </>
          ) : (
            <>
              <li><Link to="/signin" className="navbar-link" onClick={handleLinkClick}>Sign In</Link></li>
              <li><Link to="/signup" className="navbar-link btn-nav" onClick={handleLinkClick}>Sign Up</Link></li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;

