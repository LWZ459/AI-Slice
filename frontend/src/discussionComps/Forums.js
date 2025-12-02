import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Forums.css';

const Forums = () => {
  const { user } = useAuth();
  const [topics, setTopics] = useState([
    {
      id: 1,
      title: 'Best Pizza Toppings?',
      author: 'PizzaLover123',
      date: '2023-12-01',
      replies: 5,
      content: 'What are your favorite toppings? I love pepperoni and mushrooms.'
    },
    {
      id: 2,
      title: 'Late Night Delivery',
      author: 'NightOwl',
      date: '2023-12-02',
      replies: 2,
      content: 'Does anyone know if delivery is faster after midnight?'
    }
  ]);

  const [newTopicTitle, setNewTopicTitle] = useState('');
  const [newTopicContent, setNewTopicContent] = useState('');
  const [showNewTopicForm, setShowNewTopicForm] = useState(false);

  const handleCreateTopic = (e) => {
    e.preventDefault();
    if (!newTopicTitle.trim() || !newTopicContent.trim()) return;

    const newTopic = {
      id: topics.length + 1,
      title: newTopicTitle,
      author: user?.name || 'Anonymous',
      date: new Date().toISOString().split('T')[0],
      replies: 0,
      content: newTopicContent
    };

    setTopics([newTopic, ...topics]);
    setNewTopicTitle('');
    setNewTopicContent('');
    setShowNewTopicForm(false);
  };

  return (
    <div className="forums-container">
      <div className="forums-header">
        <h1>Discussion Forums</h1>
        <p>Connect with other foodies!</p>
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

      <div className="topics-list">
        {topics.map(topic => (
          <div key={topic.id} className="topic-card">
            <div className="topic-header">
              <h3>{topic.title}</h3>
              <span className="topic-meta">
                Posted by {topic.author} on {topic.date}
              </span>
            </div>
            <p className="topic-content">{topic.content}</p>
            <div className="topic-footer">
              <span className="topic-replies">{topic.replies} Replies</span>
              <button className="btn btn-secondary btn-small">View Discussion</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Forums;

