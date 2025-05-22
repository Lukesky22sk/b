from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import aiplatform
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Initialize Google AI Platform client
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")  # default location
PUBLISHER_MODEL_ID = os.getenv("GEMINI_MODEL_ID")  # e.g. "text-bison@001"

client = aiplatform.gapic.PredictionServiceClient()

QUESTIONS = [
    {"question": "What's your name?", "guidance": "Please type your full name."},
    {"question": "What do you want to learn today?", "guidance": "Be as specific as you can."},
    {"question": "Why is that important to you?", "guidance": "Think about your personal goals."},
]

user_progress = {}
user_modes = {}

@app.route("/", methods=["GET"])
def home():
    return "Gemini backend is live!"

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

        # Construct the request for Gemini
        endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{PUBLISHER_MODEL_ID}:predict"

        instances = [
            {
                "content": f"You are an expert tutor specializing in K-12 education across math, science, English, and social studies. Answer the following question clearly and appropriately for a student:\n\nQuestion: {answer}\nAnswer:"
            }
        ]

        parameters = {
            "temperature": 0.7,
            "maxOutputTokens": 200,
        }

        try:
            response = client.predict(
                endpoint=endpoint,
                instances=instances,
                parameters=parameters,
            )

            # Gemini returns the predictions in response.predictions
            # Extract the content from the first prediction
            answer_text = response.predictions[0].get("content", "").strip()

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
