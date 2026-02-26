"use client";

import { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>🚀 YC AI Research Console</h1>

      <input
        type="text"
        placeholder="Ask about YC companies..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "100%", padding: "10px", marginTop: "20px" }}
      />

      <button
        onClick={askQuestion}
        style={{ marginTop: "10px", padding: "10px 20px" }}
      >
        Ask
      </button>

      {loading && <p>Analyzing...</p>}

      {result && (
        <div style={{ marginTop: "30px" }}>
          <h2>Answer:</h2>
          <p style={{ whiteSpace: "pre-line" }}>{result.answer}</p>

          <h3>Cited Companies:</h3>
          <ul>
            {result.cited_companies?.map((c: string, i: number) => (
              <li key={i}>{c}</li>
            ))}
          </ul>

          <h3>Reasoning Trace:</h3>
          <ul>
            {result.reasoning_trace?.map((r: string, i: number) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}