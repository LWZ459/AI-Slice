import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { CartProvider } from './contexts/CartContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './navComps/Navbar';
import Footer from './navComps/Footer';
import ScrollToTop from './components/ScrollToTop';
import HomePage from './userComps/HomePage';
import SignIn from './SignInComps/SignIn';
import SignUp from './SignUpComps/SignUp';
import CustomerDashboard from './userComps/CustomerDashboard';
import OrderTracking from './userComps/OrderTracking';
import ChefDashboard from './chefComps/ChefDashboard';
import DeliveryDashboard from './deliveryComps/DeliveryDashboard';
import ManagerDashboard from './managerComps/ManagerDashboard';
import MenuBrowse from './searchComps/MenuBrowse';
import Checkout from './checkoutComps/Checkout';
import BiddingPage from './biddingComps/BiddingPage';
import NotFound from './404Page/NotFound';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <ScrollToTop />
          <div className="App">
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/signin" element={<SignIn />} />
                <Route path="/signup" element={<SignUp />} />
                <Route path="/menu" element={<MenuBrowse />} />
                <Route 
                  path="/customer" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <CustomerDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/orders/:orderId" 
                  element={
                    <ProtectedRoute>
                      <OrderTracking />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/chef" 
                  element={
                    <ProtectedRoute requiredUserType="chef">
                      <ChefDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/delivery" 
                  element={
                    <ProtectedRoute requiredUserType="delivery">
                      <DeliveryDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/manager" 
                  element={
                    <ProtectedRoute requiredUserType="manager">
                      <ManagerDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/checkout" 
                  element={
                    <ProtectedRoute>
                      <Checkout />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/bidding" 
                  element={
                    <ProtectedRoute requiredUserType="delivery">
                      <BiddingPage />
                    </ProtectedRoute>
                  } 
                />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;

