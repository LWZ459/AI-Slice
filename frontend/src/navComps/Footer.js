import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3>AI Slice</h3>
          <p>AI-Enabled Restaurant Order & Delivery System</p>
        </div>
        
        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/menu">Menu</Link></li>
            <li><Link to="/signin">Sign In</Link></li>
            <li><Link to="/signup">Sign Up</Link></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>User Types</h4>
          <ul>
            <li><Link to="/customer">Customer</Link></li>
            <li><Link to="/chef">Chef</Link></li>
            <li><Link to="/delivery">Delivery</Link></li>
            <li><Link to="/manager">Manager</Link></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Contact</h4>
          <p>Email: support@aislice.com</p>
          <p>Phone: (555) 123-4567</p>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; 2025 AI Slice. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;

