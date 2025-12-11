import { useState } from "react";

export default function AIRating({ chatLogId }) {
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const sendRating = async () => {
    if (!chatLogId || rating === 0 || submitting) return;
    setSubmitting(true);

    try {
      const response = await fetch("http://localhost:8000/api/ai/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_log_id: chatLogId,
          rating: rating,
          feedback: feedback,
        }),
      });

      if (response.ok) {
        setSubmitted(true);
      } else {
        alert("Failed to submit rating.");
      }
    } catch (err) {
      alert("Failed to submit rating.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ marginTop: "15px" }}>
      <h4>Rate this AI Answer</h4>

      {/* Star Rating */}
      <div style={{ fontSize: "30px", cursor: "pointer" }}>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            onClick={() => setRating(star)}
            style={{ color: rating >= star ? "gold" : "gray" }}
          >
            ★
          </span>
        ))}
      </div>

      {/* Feedback */}
      <textarea
        style={{ width: "100%", marginTop: "10px", padding: "5px" }}
        placeholder="Optional feedback..."
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
      />

      {/* Submit */}
      <button
        onClick={sendRating}
        disabled={submitting || rating === 0 || !chatLogId}
        style={{
          marginTop: "10px",
          background: "#2e7d32",
          color: "white",
          padding: "8px 12px",
          border: "none",
          borderRadius: "4px",
          opacity: submitting || rating === 0 || !chatLogId ? 0.7 : 1,
          cursor: submitting || rating === 0 || !chatLogId ? "not-allowed" : "pointer",
        }}
      >
        {submitting ? "Submitting..." : "Submit"}
      </button>

      {submitted && <p>Thank you for your feedback!</p>}
    </div>
  );
}

