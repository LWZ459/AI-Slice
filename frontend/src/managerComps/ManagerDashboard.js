import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './ManagerDashboard.css';

const ManagerDashboard = () => {
  // --- State ---
  const [activeTab, setActiveTab] = useState('hiring'); // hiring, staff, deliveries, complaints
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  // Data
  const [pendingUsers, setPendingUsers] = useState([]);
  const [staffList, setStaffList] = useState([]);
  const [activeDeliveries, setActiveDeliveries] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [compliments, setCompliments] = useState([]);

  // Delivery Specific
  const [selectedDeliveryBids, setSelectedDeliveryBids] = useState(null);
  const [bidsLoading, setBidsLoading] = useState(false);

  // Staff Editing
  const [editingSalaryId, setEditingSalaryId] = useState(null);
  const [newSalary, setNewSalary] = useState('');

  // Complaint Resolution
  const [resolvingComplaintId, setResolvingComplaintId] = useState(null);
  const [resolutionNote, setResolutionNote] = useState('');

  useEffect(() => {
    fetchDataForTab();
    const interval = setInterval(fetchDataForTab, 15000); // Auto refresh
    return () => clearInterval(interval);
  }, [activeTab]);

  const fetchDataForTab = async () => {
    if (activeTab === 'hiring') fetchPendingUsers();
    else if (activeTab === 'staff') fetchStaff();
    else if (activeTab === 'deliveries') fetchDeliveries();
    else if (activeTab === 'complaints') {
      fetchComplaints();
      fetchCompliments();
    }
  };

  const showMessage = (msg, type = 'success') => {
    setActionMessage(msg);
    setTimeout(() => setActionMessage(''), 3000);
  };

  // --- API Calls ---

  // 1. Hiring
  const fetchPendingUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_BASE_URL}/api/manager/pending-registrations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingUsers(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleApproveUser = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_BASE_URL}/api/manager/approve-user/${userId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showMessage('User approved successfully');
      fetchPendingUsers();
    } catch (error) {
      showMessage('Failed to approve user', 'error');
    }
  };

  const handleRejectUser = async (userId) => {
    if (!window.confirm("Are you sure you want to reject this user?")) return;
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_BASE_URL}/api/manager/reject-user/${userId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showMessage('User rejected');
      fetchPendingUsers();
    } catch (error) {
      showMessage('Failed to reject user', 'error');
    }
  };

  // 2. Staff Management
  const fetchStaff = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_BASE_URL}/api/manager/staff`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStaffList(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleFireStaff = async (userId) => {
    if (!window.confirm("Are you sure you want to FIRE this staff member? This action is irreversible.")) return;
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_BASE_URL}/api/manager/staff/${userId}/fire`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showMessage('Staff member fired');
      fetchStaff();
    } catch (error) {
      showMessage('Failed to fire staff', 'error');
    }
  };

  const handleUpdateSalary = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_BASE_URL}/api/manager/staff/${userId}/salary`, 
        { salary: parseFloat(newSalary) }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      showMessage('Salary updated');
      setEditingSalaryId(null);
      fetchStaff();
    } catch (error) {
      showMessage('Failed to update salary', 'error');
    }
  };

  // 3. Deliveries (Existing Logic)
  const fetchDeliveries = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/delivery/available`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActiveDeliveries(response.data);
    } catch (error) {}
  };

  const fetchBids = async (deliveryId) => {
    setBidsLoading(true);
    setSelectedDeliveryBids(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/api/delivery/${deliveryId}/bids`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedDeliveryBids({ deliveryId, bids: response.data });
    } catch (error) {
      showMessage('Failed to fetch bids', 'error');
    } finally {
      setBidsLoading(false);
    }
  };

  const handleAutoAssign = async (deliveryId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/delivery/${deliveryId}/auto-assign`, {}, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      showMessage(`Order #${response.data.order_id || 'Unknown'} auto-assigned`);
      fetchDeliveries();
      setSelectedDeliveryBids(null);
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Auto-assign failed', 'error');
    }
  };

  const handleManualAssign = async (deliveryId, deliveryPersonId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/delivery/${deliveryId}/assign`,
        { delivery_person_id: deliveryPersonId, justification: "Manager manual selection" },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      showMessage('Delivery assigned successfully');
      fetchDeliveries();
      setSelectedDeliveryBids(null);
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Assignment failed', 'error');
    }
  };

  // 4. Complaints & Compliments
  const fetchComplaints = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_BASE_URL}/api/manager/complaints`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setComplaints(res.data);
    } catch (error) {}
  };

  const fetchCompliments = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_BASE_URL}/api/manager/compliments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCompliments(res.data);
    } catch (error) {}
  };

  const handleResolveComplaint = async (complaintId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_BASE_URL}/api/manager/complaints/${complaintId}/resolve`, 
        { decision: resolutionNote }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      showMessage('Complaint resolved');
      setResolvingComplaintId(null);
      fetchComplaints();
    } catch (error) {
      showMessage('Failed to resolve', 'error');
    }
  };

  const handleAcknowledgeCompliment = async (complimentId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_BASE_URL}/api/manager/compliments/${complimentId}/acknowledge`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      showMessage('Compliment acknowledged, rating boosted');
      fetchCompliments();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to acknowledge', 'error');
    }
  };

  return (
    <div className="manager-dashboard">
      <h1 className="dashboard-title">Manager Dashboard</h1>
      
      {actionMessage && <div className="action-message">{actionMessage}</div>}

      <div className="tabs">
        <button className={activeTab === 'hiring' ? 'active' : ''} onClick={() => setActiveTab('hiring')}>Hiring ({pendingUsers.length})</button>
        <button className={activeTab === 'staff' ? 'active' : ''} onClick={() => setActiveTab('staff')}>Staff Management</button>
        <button className={activeTab === 'deliveries' ? 'active' : ''} onClick={() => setActiveTab('deliveries')}>Deliveries</button>
        <button className={activeTab === 'complaints' ? 'active' : ''} onClick={() => setActiveTab('complaints')}>Complaints & Compliments</button>
      </div>

      <div className="tab-content">
        
        {/* --- Hiring Tab --- */}
        {activeTab === 'hiring' && (
          <div className="dashboard-card">
            <h2>Pending Registrations</h2>
            {pendingUsers.length === 0 ? <p className="empty-state">No pending applications.</p> : (
              <div className="list-container">
                {pendingUsers.map(u => (
                  <div key={u.id} className="list-item">
                    <div>
                      <strong>{u.username}</strong> ({u.email})
                      <br />
                      <span className="badge">{u.user_type}</span>
                    </div>
                    <div className="actions">
                      <button className="btn-small btn-success" onClick={() => handleApproveUser(u.id)}>Hire (Approve)</button>
                      <button className="btn-small btn-danger" onClick={() => handleRejectUser(u.id)}>Reject</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* --- Staff Management Tab --- */}
        {activeTab === 'staff' && (
          <div className="dashboard-card">
            <h2>Current Staff</h2>
            {staffList.length === 0 ? <p className="empty-state">No active staff found.</p> : (
              <div className="table-responsive">
                <table className="staff-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Role</th>
                      <th>Rating</th>
                      <th>Salary</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {staffList.map(s => (
                      <tr key={s.id}>
                        <td>{s.full_name || s.username}</td>
                        <td>{s.user_type}</td>
                        <td>{s.rating.toFixed(1)} ★</td>
                        <td>
                          {editingSalaryId === s.id ? (
                            <div className="salary-edit">
                              <input 
                                type="number" 
                                value={newSalary} 
                                onChange={(e) => setNewSalary(e.target.value)}
                                placeholder="New Salary"
                              />
                              <button onClick={() => handleUpdateSalary(s.id)}>Save</button>
                              <button onClick={() => setEditingSalaryId(null)}>X</button>
                            </div>
                          ) : (
                            <span onClick={() => { setEditingSalaryId(s.id); setNewSalary(s.salary); }} className="salary-display">
                              ${s.salary.toFixed(2)} ✎
                            </span>
                          )}
                        </td>
                        <td>
                          <button className="btn-xs btn-danger" onClick={() => handleFireStaff(s.id)}>Fire</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* --- Deliveries Tab --- */}
        {activeTab === 'deliveries' && (
          <div className="dashboard-card">
            <h2>Delivery Management</h2>
            {activeDeliveries.length === 0 ? <p className="empty-state">No deliveries pending assignment.</p> : (
              <div className="deliveries-list">
                {activeDeliveries.map(delivery => (
                  <div key={delivery.id} className="delivery-manage-item">
                    <div className="delivery-info">
                      <h3>Order #{delivery.order_id}</h3>
                      <p><strong>Pickup:</strong> {delivery.pickup_address}</p>
                      <p><strong>Fee:</strong> ${delivery.delivery_fee.toFixed(2)}</p>
                    </div>
                    <div className="delivery-actions">
                      <button className="btn-small btn-primary" onClick={() => fetchBids(delivery.id)}>View Bids</button>
                      <button className="btn-small btn-success" onClick={() => handleAutoAssign(delivery.id)}>Auto Assign</button>
                    </div>
                    {selectedDeliveryBids && selectedDeliveryBids.deliveryId === delivery.id && (
                      <div className="bids-section">
                        <h4>Current Bids</h4>
                        {bidsLoading ? <p>Loading...</p> : selectedDeliveryBids.bids.length === 0 ? <p>No bids.</p> : (
                          <div className="bids-list-small">
                            {selectedDeliveryBids.bids.map(bid => (
                              <div key={bid.id} className="bid-row">
                                <span>Bidder #{bid.delivery_person_id}</span>
                                <span>${bid.bid_amount.toFixed(2)}</span>
                                <span>{bid.estimated_time}m</span>
                                <button className="btn-xs" onClick={() => handleManualAssign(delivery.id, bid.delivery_person_id)}>Assign</button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* --- Complaints Tab --- */}
        {activeTab === 'complaints' && (
          <div className="dashboard-grid-2">
            <div className="dashboard-card">
              <h2>Complaints</h2>
              {complaints.length === 0 ? <p className="empty-state">No complaints filed.</p> : (
                <div className="list-container">
                  {complaints.map(c => (
                    <div key={c.id} className="list-item complaint-item">
                      <div>
                        <strong>{c.title}</strong>
                        <p>{c.description}</p>
                        <small>From: {c.complainant} | Against: {c.subject} | Status: {c.status}</small>
                      </div>
                      {c.status !== 'resolved' && (
                        <div className="resolution-box">
                          {resolvingComplaintId === c.id ? (
                            <>
                              <textarea 
                                value={resolutionNote} 
                                onChange={(e) => setResolutionNote(e.target.value)} 
                                placeholder="Resolution decision..."
                              />
                              <button onClick={() => handleResolveComplaint(c.id)}>Submit Resolution</button>
                              <button onClick={() => setResolvingComplaintId(null)}>Cancel</button>
                            </>
                          ) : (
                            <button className="btn-small" onClick={() => setResolvingComplaintId(c.id)}>Resolve</button>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="dashboard-card">
              <h2>Compliments</h2>
              {compliments.length === 0 ? <p className="empty-state">No compliments yet.</p> : (
                <div className="list-container">
                  {compliments.map(c => (
                    <div key={c.id} className="list-item compliment-item">
                      <div>
                        <strong>{c.title}</strong>
                        <p>"{c.description.replace(' [ACKNOWLEDGED]', '')}"</p>
                        <small>To: {c.receiver} (From: {c.giver})</small>
                      </div>
                      {!c.description.includes('[ACKNOWLEDGED]') ? (
                        <button className="btn-small btn-success" onClick={() => handleAcknowledgeCompliment(c.id)}>
                          Acknowledge (+Rating)
                        </button>
                      ) : (
                        <span className="badge badge-success">Acknowledged</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default ManagerDashboard;
