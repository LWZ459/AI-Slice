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
import AIChat from './discussionComps/AIChat';
import Forums from './discussionComps/Forums';
import RateOrder from './userComps/RateOrder';
import ComplaintPage from './userComps/ComplaintPage';
import ComplimentPage from './userComps/ComplimentPage';

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
                <Route path="/chat" element={<AIChat />} />
                <Route 
                  path="/forums" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <Forums />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/reviews" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <RateOrder />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/reviews/:orderId" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <RateOrder />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/delivery-reviews" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <RateOrder />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/delivery-reviews/:orderId" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <RateOrder />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/customer" 
                  element={
                    <ProtectedRoute requiredUserType="customer">
                      <CustomerDashboard />
                    </ProtectedRoute>
                  } 
                />
                {/* Fallback dashboard for VIP users who share the customer dashboard but have extra perks */}
                <Route 
                  path="/vip" 
                  element={
                    <ProtectedRoute requiredUserType="vip">
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
                    <Checkout />
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
                <Route 
                  path="/complaint" 
                  element={
                    <ProtectedRoute>
                      <ComplaintPage />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/compliment" 
                  element={
                    <ProtectedRoute>
                      <ComplimentPage />
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

