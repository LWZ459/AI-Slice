import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import './Forums.css';

const Forums = () => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Create Topic State
  const [newTopicTitle, setNewTopicTitle] = useState('');
  const [newTopicContent, setNewTopicContent] = useState('');
  const [newTopicCategory, setNewTopicCategory] = useState('General');
  const [showNewTopicForm, setShowNewTopicForm] = useState(false);

  // View Topic State
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [replyContent, setReplyContent] = useState('');
  const [postsLoading, setPostsLoading] = useState(false);

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/forum/topics`);
      setTopics(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load topics');
      setLoading(false);
    }
  };

  const handleCreateTopic = async (e) => {
    e.preventDefault();
    if (!newTopicTitle.trim() || !newTopicContent.trim()) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/forum/topics`,
        {
          title: newTopicTitle,
          content: newTopicContent,
          category: newTopicCategory
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Reset form and refresh
      setNewTopicTitle('');
      setNewTopicContent('');
      setNewTopicCategory('General');
      setShowNewTopicForm(false);
      fetchTopics();
    } catch (err) {
      alert('Failed to create topic');
    }
  };

  const handleViewTopic = async (topicId) => {
    setPostsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/forum/topics/${topicId}`);
      setSelectedTopic(response.data);
    } catch (err) {
      alert('Failed to load topic details');
    } finally {
      setPostsLoading(false);
    }
  };

  const handleReply = async (e) => {
    e.preventDefault();
    if (!replyContent.trim()) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/forum/topics/${selectedTopic.id}/posts`,
        { content: replyContent },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setReplyContent('');
      handleViewTopic(selectedTopic.id); // Refresh posts
    } catch (err) {
      alert('Failed to post reply');
    }
  };

  if (loading) return <div className="forums-container"><p>Loading forums...</p></div>;

  // Render Single Topic View
  if (selectedTopic) {
    return (
      <div className="forums-container">
        <button className="btn btn-secondary" onClick={() => setSelectedTopic(null)} style={{marginBottom: '20px'}}>
          &larr; Back to Topics
        </button>

        <div className="topic-detail">
          <div className="topic-header-detail">
            <h1>{selectedTopic.title}</h1>
            <span className="topic-category-badge">{selectedTopic.category}</span>
            <p className="topic-meta-detail">
              Posted by <strong>{selectedTopic.author_name}</strong> on {new Date(selectedTopic.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="topic-main-content">
            {selectedTopic.content}
          </div>

          <div className="posts-section">
            <h3>Replies ({selectedTopic.posts.length})</h3>
            
            {selectedTopic.posts.length === 0 ? (
              <p className="no-posts">No replies yet. Be the first!</p>
            ) : (
              selectedTopic.posts.map(post => (
                <div key={post.id} className="post-card">
                  <div className="post-header">
                    <strong>{post.author_name}</strong>
                    <span className="post-date">{new Date(post.created_at).toLocaleString()}</span>
                  </div>
                  <div className="post-content">{post.content}</div>
                </div>
              ))
            )}

            <div className="reply-form-section">
              <h4>Leave a Reply</h4>
              <form onSubmit={handleReply}>
                <textarea
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  placeholder="Write your reply..."
                  rows="4"
                  required
                />
                <button type="submit" className="btn btn-primary">Post Reply</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render Topic List
  return (
    <div className="forums-container">
      <div className="forums-header">
        <h1>Discussion Forums</h1>
        <p>Connect with other foodies! Discuss Chefs, Dishes, and Delivery.</p>
        <button 
          className="btn btn-primary"
          onClick={() => setShowNewTopicForm(!showNewTopicForm)}
        >
          {showNewTopicForm ? 'Cancel' : 'Start New Topic'}
        </button>
      </div>

      {showNewTopicForm && (
        <div className="new-topic-form">
          <h2>Create New Topic</h2>
          <form onSubmit={handleCreateTopic}>
            <div className="form-group">
              <label>Category</label>
              <select 
                value={newTopicCategory} 
                onChange={(e) => setNewTopicCategory(e.target.value)}
                className="input-select"
              >
                <option value="General">General</option>
                <option value="Chefs">Chefs</option>
                <option value="Dishes">Dishes</option>
                <option value="Delivery">Delivery</option>
              </select>
            </div>
            <div className="form-group">
              <label>Title</label>
              <input
                type="text"
                value={newTopicTitle}
                onChange={(e) => setNewTopicTitle(e.target.value)}
                placeholder="Topic Title"
                required
              />
            </div>
            <div className="form-group">
              <label>Content</label>
              <textarea
                value={newTopicContent}
                onChange={(e) => setNewTopicContent(e.target.value)}
                placeholder="What's on your mind?"
                rows="4"
                required
              />
            </div>
            <button type="submit" className="btn btn-success">Post Topic</button>
          </form>
        </div>
      )}

      {error && <p className="error-text">{error}</p>}

      <div className="topics-list">
        {topics.length === 0 ? (
          <p className="empty-state">No topics yet. Start one!</p>
        ) : (
          topics.map(topic => (
            <div key={topic.id} className="topic-card">
              <div className="topic-header">
                <h3>{topic.title}</h3>
                <span className="topic-category-badge">{topic.category}</span>
              </div>
              <p className="topic-meta">
                Posted by {topic.author_name} on {new Date(topic.created_at).toLocaleDateString()}
              </p>
              <p className="topic-preview">{topic.content.substring(0, 100)}...</p>
              <div className="topic-footer">
                <span className="topic-stat">{topic.reply_count} Replies</span>
                <span className="topic-stat">{topic.view_count} Views</span>
                <button 
                  className="btn btn-secondary btn-small"
                  onClick={() => handleViewTopic(topic.id)}
                >
                  View Discussion
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Forums;
