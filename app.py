import openai
import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import redis

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app, supports_credentials=True)  # Ensure CORS allows session cookies

# Configure Redis for session storage
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = True  # 🔥 Keep session persistent
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "chat:"
app.config["SESSION_COOKIE_NAME"] = "chatbot_session"  # 🔥 Ensures browser stores session cookie
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True if using HTTPS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Allows frontend session sharing
app.config["SESSION_REDIS"] = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

# Initialize session
Session(app)

# Limit conversation history length
MAX_HISTORY_LENGTH = 10

@app.before_request
def ensure_session():
    """Ensure user keeps the same session."""
    if "session_id" not in session:
        session["session_id"] = request.cookies.get("session_id")
        if not session["session_id"]:
            session["session_id"] = os.urandom(24).hex()  # Generate unique session ID
        session.modified = True
    print(f"Using Session ID: {session['session_id']}")  # Debugging

def load_session():
    """Load previous conversation history from Redis."""
    redis_client = app.config["SESSION_REDIS"]
    redis_key = f"chat:{session['session_id']}"  # 🔥 Use consistent session ID
    stored_data = redis_client.get(redis_key)

    if stored_data:
        session["conversation"] = json.loads(stored_data)
    else:
        session["conversation"] = []

    print("Loaded Session:", json.dumps(session["conversation"], indent=2))  # Debugging

def save_session():
    """Save the current conversation history to Redis."""
    redis_client = app.config["SESSION_REDIS"]
    redis_key = f"chat:{session['session_id']}"
    redis_client.set(redis_key, json.dumps(session["conversation"]))
    session.modified = True
    print("Session saved:", json.dumps(session["conversation"], indent=2))  # Debugging

@app.route("/chat", methods=["POST"])
def chat():
    ensure_session()  # Ensure session ID is consistent
    load_session()  # Load previous session data

    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Append user message to conversation
    session["conversation"].append({"role": "user", "content": user_message})

    # Keep only the last 10 messages
    session["conversation"] = session["conversation"][-MAX_HISTORY_LENGTH:]

    save_session()  # Save updated session

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=session["conversation"]
        )

        bot_reply = response.choices[0].message.content
        print("Reply from AI:", bot_reply)

        # Save bot reply in conversation history
        session["conversation"].append({"role": "assistant", "content": bot_reply})
        save_session()  # Save updated session again

        response = jsonify({"reply": bot_reply})
        response.set_cookie("session_id", session["session_id"])  # 🔥 Ensures session ID persists
        return response
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
