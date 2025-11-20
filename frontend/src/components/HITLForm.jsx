import { useState } from "react";
import "./ui/HITLForm.css";

function HITLForm() {
  const [messages, setMessages] = useState<{ sender: string, text: string }[any]>([]);

  const [input, setInput] = useState("");
  const [checkpoint, setCheckpoint] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!input) return;
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    const res = await fetch("http://127.0.0.1:8000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: input }),
});
    if (!res.ok) {
      console.error("Failed to send message");
      return;
    }
    
    const data = await res.json();
    setMessages((prev) => [...prev, { sender: "ai", text: data.message }]);
    setCheckpoint(data.checkpoint_id);
    setInput("");
  };

  const resumeHITL = async () => {
    const res = await fetch("http://127.0.0.1:8000/api/resume", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ checkpoint_id: checkpoint }),
});
    if (!res.ok) {
      console.error("Failed to resume HITL");
      return;
    }
    
    const data = await res.json();
    setMessages((prev) => [...prev, { sender: "ai", text: data.message }]);
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((m, idx) => (
          <div key={idx} className={m.sender}>
            {m.text}
            {m.sender === "ai" && checkpoint && (
              <button onClick={resumeHITL}>Request Human Review</button>
            )}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default HITLForm;
