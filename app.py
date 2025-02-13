import openai
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        client = openai.OpenAI()  # Use the new OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply = response.choices[0].message.content
        print("Reply for the AI - ",bot_reply)
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
