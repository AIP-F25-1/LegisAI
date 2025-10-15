// src/components/hitlService.js

const API_BASE = "http://localhost:8000/api"; // Adjust if backend runs on a different port

export const sendChatMessage = async (prompt) => {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    if (!res.ok) throw new Error(`Error: ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("Error sending chat message:", error);
    return { message: "Server error. Please try again later." };
  }
};

export const requestHumanReview = async (checkpoint_id) => {
  try {
    const res = await fetch(`${API_BASE}/resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ checkpoint_id }),
    });
    if (!res.ok) throw new Error(`Error: ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("Error resuming HITL flow:", error);
    return { message: "Human review request failed." };
  }
};
