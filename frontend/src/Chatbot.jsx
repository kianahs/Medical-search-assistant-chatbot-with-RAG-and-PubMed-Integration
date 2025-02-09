import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Create a ref for the chat history container
  const chatHistoryRef = useRef(null);

  const sendMessage = async () => {
    if (!query.trim()) return;

    const newMessage = { sender: "user", text: query };
    setChatHistory((prev) => [...prev, newMessage]);
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/chat", {
        query,
      });
      const botResponse = response.data.response;
      typeMessage(botResponse);
    } catch (error) {
      console.error("Error fetching response:", error);
      setChatHistory((prev) => [
        ...prev,
        { sender: "bot", text: "Error fetching response. Please try again." },
      ]);
      setLoading(false);
    }

    setQuery("");
  };

  const typeMessage = (message) => {
    const words = message.split(" ");
    let index = 0;

    setChatHistory((prev) => [...prev, { sender: "bot", text: words[0] }]);

    const interval = setInterval(() => {
      setChatHistory((prev) => {
        const updatedChat = [...prev];
        const lastMessageIndex = updatedChat.length - 1;

        const nextWord = words[index];
        if (nextWord) {
          updatedChat[lastMessageIndex] = {
            ...updatedChat[lastMessageIndex],
            text: updatedChat[lastMessageIndex].text + " " + nextWord,
          };
        }

        return updatedChat;
      });

      index += 1;

      if (index === words.length) {
        clearInterval(interval);
        setLoading(false);
      }
    }, 200); // speed of typing in ms
  };

  // Scroll to the bottom whenever the chat history updates
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory]);

  return (
    <div className="d-flex flex-column align-items-center justify-content-center min-vh-50 bg-gradient">
      <div className="chat-container p-4 rounded-4 shadow-lg w-100 w-md-75 w-lg-50">
        <h2 className="text-center text-black mb-4">Medical Chatbot</h2>
        <div
          className="chat-history p-3 mb-4 rounded-3 overflow-auto bg-light"
          ref={chatHistoryRef} // Attach the ref here
          style={{ maxHeight: "400px" }} // Add a max height to make it scrollable
        >
          {chatHistory.map((msg, index) => (
            <div
              key={index}
              className={`mb-3 p-3 rounded-3 ${
                msg.sender === "user"
                  ? "bg-primary text-white text-start ms-auto"
                  : "bg-secondary text-white text-start me-auto"
              }`}
              style={{ maxWidth: "75%" }}
            >
              {msg.text}
            </div>
          ))}
          {loading && <div className="text-muted text-center">Thinking...</div>}
        </div>
        <div className="d-flex">
          <input
            type="text"
            className="form-control me-3 rounded-pill py-3 px-4"
            placeholder="Ask a question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button
            className="btn btn-success rounded-pill px-4 py-3"
            onClick={sendMessage}
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
