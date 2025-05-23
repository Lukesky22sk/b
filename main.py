from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS settings (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set OpenAI key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Simulated in-memory storage for user questions and guidance
user_data = {}

# Request models
class PromptRequest(BaseModel):
    prompt: str

class AnswerRequest(BaseModel):
    user: str
    answer: str

# Root endpoint for health check
@app.get("/")
def read_root():
    return {"message": "Socratic Bot backend is live."}

# Socratic chat endpoint
@app.post("/chat")
async def socratic_guide(request: PromptRequest):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Socratic AI mentor. Do not give answers. "
                    "Only respond with thoughtful, open-ended questions that challenge the user's assumptions, "
                    "encourage deeper thinking, or help clarify the issue they are exploring."
                )
            },
            {"role": "user", "content": request.prompt}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.85,
        )

        return {
            "response": response['choices'][0]['message']['content']
        }

    except Exception as e:
        return {"error": str(e)}

# Endpoint to get question and guidance for a user
@app.get("/api/questions")
def get_question(user: str):
    if user not in user_data:
        # Provide a default starter question and guidance
        user_data[user] = {
            "question": "What is your favorite color?",
            "guidance": "Think about why that color appeals to you."
        }
    return user_data[user]

# Endpoint to receive user's answer and return next question/guidance
@app.post("/api/answers")
def post_answer(data: AnswerRequest):
    # Save user's answer and generate a new question/guidance
    user_data[data.user] = {
        "question": f"You answered: {data.answer}. What made you think that?",
        "guidance": "Try to explain your reasoning."
    }
    return user_data[data.user]
