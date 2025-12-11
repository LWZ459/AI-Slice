import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requiredUserType = null }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated()) {
    // Redirect to sign in if not authenticated
    return <Navigate to="/signin" replace />;
  }

  // If a specific user type is required, check it
  if (requiredUserType && user?.user_type !== requiredUserType) {
    // Redirect to their dashboard if wrong user type
    const routes = {
      customer: '/customer',
      vip: '/vip',
      chef: '/chef',
      delivery: '/delivery',
      manager: '/manager'
    };
    const dashboardRoute = routes[user?.user_type] || '/customer';
    return <Navigate to={dashboardRoute} replace />;
  }

  return children;
};

export default ProtectedRoute;




