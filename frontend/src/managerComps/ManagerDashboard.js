import React, { useState } from 'react';
import './ManagerDashboard.css';

const ManagerDashboard = () => {
  const [pendingRegistrations] = useState([
    { id: 1, name: 'John Doe', type: 'Chef', email: 'john@example.com', date: '2023-12-15' },
    { id: 2, name: 'Jane Smith', type: 'Delivery', email: 'jane@example.com', date: '2023-12-14' }
  ]);

  const [pendingAssignments] = useState([
    { orderId: 3001, bids: [
      { deliveryPerson: 'Mike Johnson', amount: 12.00 },
      { deliveryPerson: 'Sarah Williams', amount: 15.00 },
      { deliveryPerson: 'Tom Brown', amount: 10.00 }
    ], lowestBidder: 'Tom Brown', lowestAmount: 10.00 }
  ]);

  const [hrActions] = useState([
    { id: 1, type: 'Warning', user: 'Chef Alice', reason: 'Low ratings', date: '2023-12-15' },
    { id: 2, type: 'Compliment', user: 'Delivery Bob', reason: 'Excellent service', date: '2023-12-14' }
  ]);

  const [staffMembers] = useState([
    { 
      id: 1, 
      name: 'Chef Mario', 
      role: 'Chef', 
      email: 'chef@test.com',
      status: 'Active', 
      avgRating: 4.8, 
      totalRatings: 45,
      warnings: 0,
      compliments: 3,
      lastActivity: '2023-12-15'
    },
    { 
      id: 2, 
      name: 'Chef Alice', 
      role: 'Chef', 
      email: 'alice@test.com',
      status: 'Active', 
      avgRating: 3.2, 
      totalRatings: 28,
      warnings: 2,
      compliments: 1,
      lastActivity: '2023-12-14'
    },
    { 
      id: 3, 
      name: 'Delivery Driver', 
      role: 'Delivery', 
      email: 'delivery@test.com',
      status: 'Active', 
      avgRating: 4.6, 
      totalRatings: 67,
      warnings: 0,
      compliments: 5,
      lastActivity: '2023-12-15'
    },
    { 
      id: 4, 
      name: 'Mike Johnson', 
      role: 'Delivery', 
      email: 'mike@test.com',
      status: 'On Leave', 
      avgRating: 4.5, 
      totalRatings: 32,
      warnings: 1,
      compliments: 2,
      lastActivity: '2023-12-10'
    },
    { 
      id: 5, 
      name: 'Sarah Williams', 
      role: 'Delivery', 
      email: 'sarah@test.com',
      status: 'Active', 
      avgRating: 4.9, 
      totalRatings: 89,
      warnings: 0,
      compliments: 8,
      lastActivity: '2023-12-15'
    }
  ]);

  return (
    <div className="manager-dashboard">
      <h1 className="dashboard-title">Manager Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Pending Registrations</h2>
          <div className="registrations-list">
            {pendingRegistrations.map(reg => (
              <div key={reg.id} className="registration-item">
                <div className="reg-info">
                  <h3>{reg.name}</h3>
                  <p>{reg.type} • {reg.email}</p>
                  <p className="reg-date">Applied: {reg.date}</p>
                </div>
                <div className="reg-actions">
                  <button className="btn btn-success">Approve</button>
                  <button className="btn btn-danger">Reject</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <h2>Delivery Assignments</h2>
          <div className="assignments-list">
            {pendingAssignments.map((assignment, idx) => (
              <div key={idx} className="assignment-card">
                <h3>Order #{assignment.orderId}</h3>
                <div className="bids-review">
                  <h4>Bids Received:</h4>
                  {assignment.bids.map((bid, bidIdx) => (
                    <div key={bidIdx} className={`bid-row ${bid.amount === assignment.lowestAmount ? 'lowest' : ''}`}>
                      <span>{bid.deliveryPerson}</span>
                      <span className="bid-amount">${bid.amount.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
                <div className="assignment-info">
                  <p className="lowest-bid">Lowest Bid: {assignment.lowestBidder} (${assignment.lowestAmount.toFixed(2)})</p>
                </div>
                <div className="assignment-actions">
                  <button className="btn btn-primary">Auto-Assign (Lowest)</button>
                  <button className="btn btn-secondary">Manual Override</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <h2>HR Actions</h2>
          <div className="hr-list">
            {hrActions.map(action => (
              <div key={action.id} className="hr-item">
                <div className={`hr-type ${action.type.toLowerCase()}`}>
                  {action.type}
                </div>
                <div className="hr-details">
                  <h3>{action.user}</h3>
                  <p>{action.reason}</p>
                  <p className="hr-date">{action.date}</p>
                </div>
                <button className="btn btn-primary">View Details</button>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card staff-management-card">
          <h2>Staff Management</h2>
          <div className="staff-list">
            {staffMembers.map(staff => (
              <div key={staff.id} className="staff-item">
                <div className="staff-header">
                  <div className="staff-info">
                    <h3>{staff.name}</h3>
                    <p className="staff-role">{staff.role} • {staff.email}</p>
                  </div>
                  <span className={`staff-status ${staff.status.toLowerCase().replace(' ', '-')}`}>
                    {staff.status}
                  </span>
                </div>
                <div className="staff-metrics">
                  <div className="metric-item">
                    <span className="metric-label">Rating:</span>
                    <span className={`metric-value rating ${staff.avgRating >= 4.5 ? 'high' : staff.avgRating >= 3.5 ? 'medium' : 'low'}`}>
                      {staff.avgRating.toFixed(1)} ({staff.totalRatings})
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Warnings:</span>
                    <span className={`metric-value warnings ${staff.warnings > 0 ? 'has-warnings' : ''}`}>
                      {staff.warnings}
                    </span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Compliments:</span>
                    <span className="metric-value compliments">
                      {staff.compliments}
                    </span>
                  </div>
                </div>
                <div className="staff-actions">
                  <button className="btn btn-secondary btn-small">View Details</button>
                  {staff.warnings > 0 && (
                    <button className="btn btn-warning btn-small">Review Warnings</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManagerDashboard;

