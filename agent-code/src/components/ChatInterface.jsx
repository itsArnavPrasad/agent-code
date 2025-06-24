// ChatInterface.jsx
import React, { useState } from 'react';

const ChatInterface = ({ onSend, messages, setMessages }) => {
  const [input, setInput] = useState("");

    const handleSend = () => {
      if (!input.trim()) return;

      const newMessage = { role: "user", content: input };
      const updatedMessages = [...messages, newMessage];
      setMessages(updatedMessages);

      onSend(input, updatedMessages);
      setInput("");
    };

  return (
    <div style={{ backgroundColor: "#1e1e1e", padding: "1rem", borderRadius: "8px", marginTop: "1rem", color: "white" }}>
      <div style={{ maxHeight: "200px", overflowY: "auto", marginBottom: "1rem" }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: "0.5rem" }}>
            <strong>{msg.role === "user" ? "You" : "Agent"}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={input}
          placeholder="Describe what you want the agent to do..."
          onChange={(e) => setInput(e.target.value)}
          style={{ flexGrow: 1, padding: "0.5rem", borderRadius: "4px", border: "1px solid #ccc" }}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};
export default ChatInterface;

