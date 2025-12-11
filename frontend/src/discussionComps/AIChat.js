import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config/api';
import AIRating from '../components/AIRating';
import './AIChat.css';

const AIChat = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! I\'m your AI assistant. How can I help you today?', sender: 'ai' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user'
    };

    setMessages([...messages, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/ask`, {
        question: userMessage.text
      });

      const data = response.data;
      
      const aiResponse = {
        id: messages.length + 2,
        text: data.answer,
        sender: 'ai',
        fromLocalKB: data.source === 'local_kb',
        chatLogId: data.chat_log_id,
        canRate: data.can_rate,
        rating: null 
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      const errorResponse = {
        id: messages.length + 2,
        text: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later.",
        sender: 'ai'
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="ai-chat">
      <div className="chat-container">
        <div className="chat-header">
          <h1>AI Assistant</h1>
          <p>Ask me anything about our platform</p>
        </div>

        <div className="chat-messages">
          {messages.map(message => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}
            >
              <div className="message-content">
                {message.text}
                {message.fromLocalKB && message.sender === 'ai' && (
                  <span className="kb-badge">From Knowledge Base</span>
                )}
                {message.sender === 'ai' && (
                  <AIRating chatLogId={message.chatLogId} />
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message ai-message">
              <div className="message-content typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="chat-input-form">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your question..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">Send</button>
        </form>
      </div>
    </div>
  );
};

export default AIChat;
