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

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"message": "Socratic Bot backend is live."}

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
        return {"response": response['choices'][0]['message']['content']}

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"response": "Sorry, I couldn't process your request. Please try again later."}
