import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return; // Prevent sending empty messages

        const newMessages = [...messages, { role: "user", content: input }];
        setMessages(newMessages);
        setInput(""); // Clear input field after sending

        try {
            const response = await axios.post("http://127.0.0.1:5000/chat", { message: input });
            setMessages([...newMessages, { role: "bot", content: response.data.reply }]);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    return (
        <div className="chat-container">
            <h1>Chatbot</h1>
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <p key={index} className={msg.role}>
                        <strong>{msg.role === "user" ? "You: " : "Bot: "}</strong>
                        {msg.content}
                    </p>
                ))}
            </div>
            <input
                type="text" disabled={false}
                value={input} // Make sure input is controlled
                onChange={(e) => setInput(e.target.value)} // Update input state on change
                placeholder="Type a message..."
                onKeyPress={(e) => e.key === "Enter" && sendMessage()} // Send on Enter key press
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
}

export default App;
