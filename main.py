from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

QUESTIONS = [
    {"question": "What's your name?", "guidance": "Please type your full name."},
    {"question": "What do you want to learn today?", "guidance": "Be as specific as you can."},
    {"question": "Why is that important to you?", "guidance": "Think about your personal goals."},
]

user_progress = {}
user_modes = {}  # 'guided' or 'freechat'

@app.route("/", methods=["GET"])
def home():
    return "Michellekinzai backend is live!"

@app.route("/api/questions", methods=["GET"])
def get_initial_question():
    user_id = request.args.get("user", "default")
    user_progress[user_id] = 0
    user_modes[user_id] = "guided"
    return jsonify(QUESTIONS[0])

@app.route("/api/answers", methods=["POST"])
def submit_answer():
    data = request.get_json()
    user_id = data.get("user", "default")
    answer = data.get("answer", "").strip()

    mode = user_modes.get(user_id, "guided")

    if mode == "guided":
        current_index = user_progress.get(user_id, 0) + 1
        if current_index < len(QUESTIONS):
            user_progress[user_id] = current_index
            return jsonify(QUESTIONS[current_index])
        else:
            user_modes[user_id] = "freechat"
            return jsonify({
                "question": "Awesome! Now you can ask me any K-12 math, science, English, or social studies question.",
                "guidance": "Ask your question or type 'end' to finish."
            })

    elif mode == "freechat":
        if answer.lower() in ["end", "quit", "exit"]:
            user_modes.pop(user_id, None)
            user_progress.pop(user_id, None)
            return jsonify({
                "question": "Session ended. Thanks for chatting!",
                "guidance": ""
            })

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert tutor specializing in K-12 education across math, science, English, and social studies."
                    },
                    {
                        "role": "user",
                        "content": answer
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )

            answer_text = response.choices[0].message["content"].strip()

            return jsonify({
                "question": answer_text,
                "guidance": "Ask another question or type 'end' to finish."
            })

        except Exception as e:
            return jsonify({
                "question": f"Sorry, I couldn't process your question. Error: {str(e)}",
                "guidance": "Try again or type 'end' to finish."
            })

    else:
        return jsonify({
            "question": "Unknown session state. Please start over.",
            "guidance": ""
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
