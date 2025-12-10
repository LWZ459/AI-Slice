import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './ManagerDashboard.css';

const ManagerDashboard = () => {
  const [stats, setStats] = useState(null);
  
  // Placeholder data for now until Manager endpoints are fully implemented in frontend
  const [pendingRegistrations] = useState([]);
  const [staffMembers] = useState([]);

  useEffect(() => {
    // Ideally fetch dashboard stats here
  }, []);

  const handleApproveUser = async (userId) => {
      alert(`Approve user ${userId}`);
      // await axios.post(`${API_BASE_URL}/api/manager/approve-customer/${userId}`);
  };

  return (
    <div className="manager-dashboard">
      <h1 className="dashboard-title">Manager Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Pending Registrations</h2>
          {pendingRegistrations.length === 0 ? (
              <p className="empty-state">No pending registrations.</p>
          ) : (
          <div className="registrations-list">
                {/* Map pending registrations here */}
                </div>
          )}
          <div style={{marginTop: '1rem'}}>
              <p className="note">Use API directly to approve users for now or check back later for full UI integration.</p>
          </div>
        </div>

        <div className="dashboard-card staff-management-card">
          <h2>Staff Overview</h2>
          <p>Manage Chefs and Delivery Personnel performance.</p>
          {/* Staff list would go here */}
        </div>

        <div className="dashboard-card">
            <h2>System Actions</h2>
            <div className="actions-list" style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
                <button className="btn btn-secondary">View Complaints</button>
                <button className="btn btn-secondary">Manage Knowledge Base</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManagerDashboard;
