import React, { useState, useRef, useEffect } from 'react';
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

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        text: getAIResponse(inputMessage),
        sender: 'ai',
        fromLocalKB: Math.random() > 0.5, // Simulate local KB vs LLM
        rating: null // Add rating field
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000);
  };

  const handleRateAnswer = (messageId, rating) => {
    setMessages(prevMessages => 
      prevMessages.map(msg => 
        msg.id === messageId ? { ...msg, rating } : msg
      )
    );
    // TODO: Send rating to backend
    console.log(`Rated message ${messageId} with ${rating} stars`);
  };

  const getAIResponse = (query) => {
    const lowerQuery = query.toLowerCase();
    if (lowerQuery.includes('menu') || lowerQuery.includes('dish')) {
      return 'You can browse our menu by clicking on the "Menu" link in the navigation. We have a variety of dishes from our talented chefs including pizzas, salads, pasta, and desserts!';
    } else if (lowerQuery.includes('order') || lowerQuery.includes('checkout')) {
      return 'To place an order, add items to your cart from the menu page, then proceed to checkout. Make sure you have sufficient balance in your wallet. VIP customers get a 5% discount automatically!';
    } else if (lowerQuery.includes('delivery') || lowerQuery.includes('deliver')) {
      return 'Our delivery system uses a bidding model. Delivery staff can bid on orders, and the lowest bidder typically wins. The manager can override assignments if needed.';
    } else if (lowerQuery.includes('wallet') || lowerQuery.includes('payment')) {
      return 'You can deposit money to your wallet from the customer dashboard. All orders are paid from your wallet balance. Orders exceeding your balance will be automatically rejected.';
    } else {
      return 'I\'m here to help! You can ask me about the menu, placing orders, delivery, wallet management, or any other questions about our platform.';
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
                  <div className="message-rating">
                    <span className="rating-label">Rate this answer:</span>
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        key={star}
                        className={`star-btn ${message.rating >= star ? 'active' : ''}`}
                        onClick={() => handleRateAnswer(message.id, star)}
                        disabled={message.rating !== null}
                      >
                        ★
                      </button>
                    ))}
                  </div>
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

