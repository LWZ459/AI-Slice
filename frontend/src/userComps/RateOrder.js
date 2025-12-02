import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './RateOrder.css';

const RateOrder = () => {
  const navigate = useNavigate();
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [hoveredStar, setHoveredStar] = useState(0);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }
    // TODO: Submit rating to backend
    alert('Thank you for your feedback!');
    navigate('/customer');
  };

  return (
    <div className="rate-order-container">
      <div className="rate-card">
        <h1>Rate Your Order</h1>
        <p>How was your food?</p>

        <form onSubmit={handleSubmit}>
          <div className="star-rating-lg">
            {[1, 2, 3, 4, 5].map(star => (
              <button
                key={star}
                type="button"
                className={`star-btn-lg ${(hoveredStar || rating) >= star ? 'active' : ''}`}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredStar(star)}
                onMouseLeave={() => setHoveredStar(0)}
              >
                ★
              </button>
            ))}
          </div>

          <div className="form-group">
            <label>Leave a comment (optional)</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us what you liked or didn't like..."
              rows="4"
            />
          </div>

          <div className="button-group">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/customer')}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Submit Review
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RateOrder;

