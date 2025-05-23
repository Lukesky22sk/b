from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class AnswerRequest(BaseModel):
    user: str
    answer: str

# In-memory user state
user_states = {}

@app.get("/api/questions")
async def get_question(user: str):
    if user not in user_states:
        user_states[user] = {
            "question": "What topic would you like to explore?",
            "guidance": "Try to be as specific as possible with your answer."
        }
    return user_states[user]

@app.post("/api/answers")
async def post_answer(data: AnswerRequest):
    user = data.user
    user_answer = data.answer

    prompt = (
        f"You are a Socratic AI mentor. The student answered: '{user_answer}'.\n"
        "Respond ONLY with a thoughtful, open-ended question or hint that encourages deeper thinking. "
        "Do NOT give direct answers."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Socratic AI mentor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
        )
        guidance = response['choices'][0]['message']['content']
    except Exception as e:
        guidance = "Sorry, I couldn't process your request. Please try again."

    user_states[user] = {
        "question": f"Considering your answer '{user_answer}', what do you think about this?",
        "guidance": guidance
    }

    return user_states[user]

@app.get("/")
def read_root():
    return {"message": "Socratic Bot backend is live."}
