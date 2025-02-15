import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { FiSend } from "react-icons/fi"; // Send button icon
import { HiChatAlt2 } from "react-icons/hi"; // Chat icon for header
import "./App.css";

function App() {
    const [messages, setMessages] = useState([]); // Ensure messages state updates correctly
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const chatBoxRef = useRef(null);

    useEffect(() => {
        // Auto-scroll to latest message
        if (chatBoxRef.current) {
            chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessage = useCallback(async () => {
        if (!input.trim() || loading) return; // Prevent sending empty messages

        const userMessage = { role: "user", content: input };
        setMessages(prevMessages => [...prevMessages, userMessage]); // Update state properly

        setInput(""); // Clear input field
        setLoading(true);

        try {
            const response = await axios.post("http://127.0.0.1:5000/chat", { message: input });
            const botMessage = { role: "bot", content: response.data.reply };
            setMessages(prevMessages => [...prevMessages, botMessage]); // Add bot's reply properly
        } catch (error) {
            console.error("Error:", error);
            const errorMessage = { role: "bot", content: "Oops! Something went wrong." };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
        }

        setLoading(false);
    }, [input, loading]);

    return (
        <div className="chat-container">
            <div className="chat-header">
                <HiChatAlt2 size={28} className="chat-icon" />
                <div>
                    <h1>FF Assistant V0</h1>
                    <p>Your AI-powered chatbot</p>
                </div>
            </div>
            <div className="chat-box" ref={chatBoxRef}>
                {messages.length === 0 ? (
                    <p className="no-messages">Start a conversation...</p>
                ) : (
                    messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                            <p>{msg.content}</p>
                        </div>
                    ))
                )}
                {loading && <div className="typing">Bot is typing...</div>}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                />
                <button onClick={sendMessage} disabled={loading}>
                    <FiSend size={22} />
                </button>
            </div>
        </div>
    );
}

export default App;
