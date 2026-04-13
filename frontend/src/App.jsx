import { useState } from 'react'
import axios from "axios";
import './App.css'

const API_URL = "http://127.0.0.1:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!question.trim() || loading) return;

    const userMessage = {role: "user", text: question};
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/query`, { question });
      const { answer, chunks } = response.data;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: answer, chunks },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Something went wrong. Is the backend running?", chunks: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>RAG Demo</h1>
        <p>Ask anything about your ingested documents</p>
      </header>

      <div className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state">Ask a question to get started</div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">{msg.text}</div>
            {msg.chunks && msg.chunks.length > 0 && (
              <div className="sources">
                <span className="sources-label">Sources:</span>
                {msg.chunks.map((chunk, j) => (
                  <span key={j} className="source-tag">
                    p.{chunk.page + 1} · {chunk.score}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="bubble loading">Thinking...</div>
          </div>
        )}
      </div>

      <div className="input-row">
        <textarea
          className="input"
          rows={1}
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="send-btn" onClick={handleSubmit} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}